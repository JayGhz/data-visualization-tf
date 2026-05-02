from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from .common import OUTPUTS_DIR, PROCESSED_DIR, ensure_dir


def _load_silver(slug: str) -> pl.DataFrame:
    return pl.read_csv(PROCESSED_DIR / "silver" / slug / "data.csv", ignore_errors=True)


def _select_columns(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    existing = [column for column in columns if column in df.columns]
    return df.select(existing)


def _aggregate_f12b(df: pl.DataFrame) -> pl.DataFrame:
    dev_columns = [column for column in df.columns if column.startswith("DEV_")]

    if dev_columns:
        df = df.with_columns(pl.sum_horizontal(dev_columns).alias("DEV_TOTAL"))
    else:
        df = df.with_columns(pl.lit(0).alias("DEV_TOTAL"))

    return (
        df.with_columns(pl.col("CODIGO_UNICO").cast(pl.Utf8))
        .group_by(["CODIGO_UNICO"], maintain_order=True)
        .agg(
            [
                pl.col("DEV_TOTAL").sum().alias("DEV_TOTAL"),
                pl.col("AVANCE_FISICO").max().alias("AVANCE_FISICO"),
            ]
        )
    )


def _aggregate_estado(df: pl.DataFrame) -> pl.DataFrame:
    # Normalizar tipos
    df = df.with_columns(pl.col("CODIGO_UNICO").cast(pl.Utf8))

    # Filtrar solo registros de situación
    if "TIP_REGISTRO" in df.columns:
        df = df.filter(
            pl.col("TIP_REGISTRO")
            .cast(pl.Utf8)
            .str.to_uppercase()
            .str.contains("SITU")
        )

    # Validación mínima
    required_cols = ["CODIGO_UNICO", "PERIODO"]
    if any(col not in df.columns for col in required_cols):
        return pl.DataFrame()

    agg_exprs = []

    if "DESCRIPCION" in df.columns:
        agg_exprs.append(
            pl.col("DESCRIPCION").drop_nulls().first().alias("SITUACION_TEXTO")
        )

    if "FECHA_REGISTRO" in df.columns:
        df = df.with_columns(
            pl.when(pl.col("FECHA_REGISTRO").cast(pl.Utf8).str.strip_chars() == "")
            .then(None)
            .otherwise(pl.col("FECHA_REGISTRO"))
            .alias("FECHA_REGISTRO")
        )

        agg_exprs.append(
            pl.col("FECHA_REGISTRO").max().alias("SITUACION_FECHA")
        )

    result = (
        df.group_by(["CODIGO_UNICO", "PERIODO"], maintain_order=True)
        .agg(agg_exprs)
        .drop_nulls(subset=["CODIGO_UNICO", "PERIODO"])
    )

    return result


def run_pipeline() -> dict[str, Path]:
    gold_dir = PROCESSED_DIR / "gold"
    ensure_dir(gold_dir)

    # ================= LOAD =================

    detalle = _load_silver("detalle-de-inversiones")
    cierre = _load_silver("cierre-de-inversiones")
    f12b = _load_silver("formato-12b-de-de-inversiones")
    estado = _load_silver("estado-situacional-de-inversiones")
    proceso = _load_silver("proceso-de-seleccion-de-inversiones")

    # ================= DIMENSIONES =================

    dim_inversion_cols = [
        "CODIGO_UNICO",
        "NOMBRE_INVERSION",
        "ESTADO",
        "SITUACION",
        "SECTOR",
        "FUNCION",
        "PROGRAMA",
        "SUBPROGRAMA",
        "DEPARTAMENTO",
        "PROVINCIA",
        "DISTRITO",
        "UBIGEO",
        "LATITUD",
        "LONGITUD",
    ]

    dim_inversion = _select_columns(detalle, dim_inversion_cols).with_columns(
        pl.col("CODIGO_UNICO").cast(pl.Utf8)
    )

    dim_inversion_path = gold_dir / "dim_inversion.csv"
    dim_inversion.write_csv(dim_inversion_path)

    dim_cierre = _select_columns(
        cierre,
        ["CODIGO_UNICO", "FEC_CIERRE", "DES_CIERRE", "CULMINADA", "TOTAL_LIQUIDACION"],
    )

    dim_cierre_path = gold_dir / "dim_cierre.csv"
    dim_cierre.write_csv(dim_cierre_path)

    # ================= FACT TABLES =================

    fact_financiera_path = gold_dir / "fact_financiera.csv"
    f12b.write_csv(fact_financiera_path)

    fact_situacional_path = gold_dir / "fact_situacional.csv"
    estado.write_csv(fact_situacional_path)

    fact_componentes_path = gold_dir / "fact_componentes.csv"
    proceso.write_csv(fact_componentes_path)

    # ================= AGG =================

    f12b_agg = _aggregate_f12b(f12b)
    estado_agg = _aggregate_estado(estado)

    # ================= TABLEAU =================

    tableau = estado_agg.join(dim_inversion, on="CODIGO_UNICO", how="left")
    tableau = tableau.join(f12b_agg, on="CODIGO_UNICO", how="left")

    # ================= FLAGS =================

    tableau = tableau.with_columns(
        [
            pl.when(pl.col("NOMBRE_INVERSION").is_null())
            .then(pl.lit("SIN_DIM"))
            .otherwise(pl.lit("OK"))
            .alias("FLAG_DIM"),

            pl.when(pl.col("AVANCE_FISICO").is_null())
            .then(pl.lit("SIN_AVANCE"))
            .otherwise(pl.lit("OK"))
            .alias("FLAG_AVANCE"),

            pl.when(
                (pl.col("LATITUD").is_null()) | (pl.col("LONGITUD").is_null())
            )
            .then(pl.lit("SIN_GEO"))
            .otherwise(pl.lit("OK"))
            .alias("FLAG_GEO"),
        ]
    )

    # ================= DATASET ANALÍTICO =================

    tableau_clean = tableau.filter(
        (pl.col("FLAG_DIM") == "OK") &
        (pl.col("FLAG_AVANCE") == "OK")
    )

    # ================= EXPORTS =================

    tableau_full_path = gold_dir / "tableau_inversion_period_full.csv"
    tableau_clean_path = gold_dir / "tableau_inversion_period_clean.csv"

    tableau.write_csv(tableau_full_path)
    tableau_clean.write_csv(tableau_clean_path)

    # ================= BITACORA =================

    bitacora_path = OUTPUTS_DIR / "bitacora" / "bitacora_silver_gold.csv"

    bitacora_df = pl.DataFrame(
        [
            {
                "layer_from": "silver",
                "layer_to": "gold",
                "rule": "aggregate_f12b",
                "note": "Aggregated financial data by CODIGO_UNICO",
                "applied_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "layer_from": "silver",
                "layer_to": "gold",
                "rule": "aggregate_estado",
                "note": "Aggregated situational data by CODIGO_UNICO and PERIODO",
                "applied_at": datetime.now(timezone.utc).isoformat(),
            },
        ]
    )

    bitacora_df.write_csv(bitacora_path)

    return {
        "dim_inversion": dim_inversion_path,
        "dim_cierre": dim_cierre_path,
        "fact_financiera": fact_financiera_path,
        "fact_situacional": fact_situacional_path,
        "fact_componentes": fact_componentes_path,
        "tableau_full": tableau_full_path,
        "tableau_clean": tableau_clean_path,
        "bitacora": bitacora_path,
    }


if __name__ == "__main__":
    outputs = run_pipeline()
    for key, path in outputs.items():
        print(f"{key}: {path}")