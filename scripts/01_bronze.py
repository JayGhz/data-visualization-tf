"""
01_bronze.py
Raw CSV ingestion to Parquet. No business logic applied.
All columns kept as strings to avoid parsing errors.
Column names are standardized to UPPERCASE with underscores.
"""
import polars as pl
from config import DETALLE_RAW, F12B_RAW, CIERRE_RAW, DETALLE_BRONZE, F12B_BRONZE, CIERRE_BRONZE


DATASETS = [
    (DETALLE_RAW, DETALLE_BRONZE, "detalle"),
    (F12B_RAW,    F12B_BRONZE,    "f12b"),
    (CIERRE_RAW,  CIERRE_BRONZE,  "cierre"),
]


def normalize_columns(lf: pl.LazyFrame) -> pl.LazyFrame:
    cols = lf.collect_schema().names()
    mapping = {c: c.strip().upper().replace(" ", "_").replace('"', "") for c in cols}
    return lf.rename(mapping)


def ingest(src, dst, name: str) -> None:
    print(f"  [{name}] {src.name} -> {dst.name}")
    lf = pl.scan_csv(src, infer_schema_length=0, ignore_errors=True)
    lf = normalize_columns(lf)
    lf.sink_parquet(dst)


def run_bronze() -> None:
    print("Bronze layer — raw ingestion")
    for src, dst, name in DATASETS:
        ingest(src, dst, name)
    print("Bronze complete.\n")


if __name__ == "__main__":
    run_bronze()
