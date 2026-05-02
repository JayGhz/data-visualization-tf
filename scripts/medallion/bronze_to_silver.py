from __future__ import annotations

from datetime import datetime, timezone
import re

import polars as pl

from .common import DATASET_CONFIGS, OUTPUTS_DIR, RAW_DIR, PROCESSED_DIR, ensure_dir
from .common import normalize_period, standardize_cui


def _process_dataset(config) -> dict:
    csv_path = RAW_DIR / config.slug / "data.csv"
    output_dir = PROCESSED_DIR / "silver" / config.slug
    ensure_dir(output_dir)
    output_path = output_dir / "data.csv"

    bitacora = []
    drop_null_cui = 0
    drop_dupe = 0
    period_normalized = 0

    scan = pl.scan_csv(csv_path, ignore_errors=True)
    total_rows = scan.select(pl.len().alias("rows")).collect().item()

    if "CODIGO_UNICO" in scan.columns:
        null_cui = (
            scan.select(pl.col("CODIGO_UNICO").is_null().sum().alias("n"))
            .collect()
            .item()
        )
        drop_null_cui = int(null_cui)

    if config.unique_key and config.key_columns:
        unique_count = (
            scan.unique(subset=config.key_columns)
            .select(pl.len().alias("n"))
            .collect()
            .item()
        )
        drop_dupe = int(total_rows - unique_count)

    ldf = scan

    string_cols = [
        column for column, dtype in ldf.schema.items() if dtype == pl.Utf8
    ]
    if string_cols:
        ldf = ldf.with_columns([pl.col(string_cols).str.strip_chars()])

    if "CODIGO_UNICO" in ldf.columns:
        ldf = ldf.with_columns(
            pl.col("CODIGO_UNICO").map_elements(standardize_cui, return_dtype=pl.Utf8)
        ).filter(pl.col("CODIGO_UNICO").is_not_null())

    for column in config.period_columns:
        if column in ldf.columns:
            ldf = ldf.with_columns(
                pl.col(column).map_elements(normalize_period, return_dtype=pl.Utf8)
            )

    numeric_pattern = re.compile(config.numeric_regex)
    numeric_columns = [column for column in ldf.columns if numeric_pattern.match(column)]
    if numeric_columns:
        ldf = ldf.with_columns(
            [pl.col(numeric_columns).cast(pl.Float64, strict=False)]
        )

    date_columns = [
        column
        for column in ldf.columns
        if column.startswith("FECHA_") or column.startswith("FEC_")
    ]
    if date_columns:
        ldf = ldf.with_columns(
            [
                pl.col(date_columns)
                .str.strptime(pl.Datetime, strict=False)
                .dt.strftime("%Y-%m-%d")
            ]
        )

    if config.unique_key and config.key_columns:
        ldf = ldf.unique(subset=config.key_columns, keep="first")

    ldf.sink_csv(output_path)

    applied_at = datetime.now(timezone.utc).isoformat()
    if drop_null_cui:
        bitacora.append(
            {
                "layer_from": "bronze",
                "layer_to": "silver",
                "dataset": config.slug,
                "rule": "drop_null_cui",
                "columns": "CODIGO_UNICO",
                "affected_rows": drop_null_cui,
                "note": "Removed rows without CODIGO_UNICO",
                "applied_at": applied_at,
            }
        )

    if drop_dupe:
        bitacora.append(
            {
                "layer_from": "bronze",
                "layer_to": "silver",
                "dataset": config.slug,
                "rule": "drop_duplicate_keys",
                "columns": ",".join(config.key_columns),
                "affected_rows": drop_dupe,
                "note": "Removed duplicate keys for unique dataset",
                "applied_at": applied_at,
            }
        )

    if period_normalized:
        bitacora.append(
            {
                "layer_from": "bronze",
                "layer_to": "silver",
                "dataset": config.slug,
                "rule": "normalize_period",
                "columns": ",".join(config.period_columns),
                "affected_rows": period_normalized,
                "note": "Normalized YYYYMM to YYYY-MM",
                "applied_at": applied_at,
            }
        )

    bitacora.append(
        {
            "layer_from": "bronze",
            "layer_to": "silver",
            "dataset": config.slug,
            "rule": "coerce_numeric",
            "columns": config.numeric_regex,
            "affected_rows": None,
            "note": "Coerced numeric-like columns",
            "applied_at": applied_at,
        }
    )

    bitacora.append(
        {
            "layer_from": "bronze",
            "layer_to": "silver",
            "dataset": config.slug,
            "rule": "parse_dates",
            "columns": "FECHA_*|FEC_*",
            "affected_rows": None,
            "note": "Parsed date columns to ISO format",
            "applied_at": applied_at,
        }
    )

    return {"output": output_path, "bitacora": bitacora}


def run_pipeline() -> dict[str, Path]:
    bitacora_rows = []
    outputs = {}

    for config in DATASET_CONFIGS:
        result = _process_dataset(config)
        outputs[config.slug] = result["output"]
        bitacora_rows.extend(result["bitacora"])

    bitacora_df = pl.DataFrame(bitacora_rows)
    bitacora_path = OUTPUTS_DIR / "bitacora" / "bitacora_bronze_silver.csv"
    bitacora_df.write_csv(bitacora_path)

    return {"silver_outputs": outputs, "bitacora": bitacora_path}


if __name__ == "__main__":
    result = run_pipeline()
    print(f"bitacora: {result['bitacora']}")
