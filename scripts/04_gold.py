"""
04_gold.py
Business metric derivation. Reads from Silver, writes Gold.

All columns should already be clean and typed in Silver.
This layer only computes derived variables — no cleaning, no NLP, no joins.

Derived columns (per seleccion_variables_3datasets.xlsx):
  BRECHA               : AVANCE_EJECUCION - AVANCE_FISICO (positive = finance ahead of physical)
  DIAS_SIN_REPORTE     : days since ULT_FEC_DECLA_ESTIM (staleness signal)
  DIAS_ARRANQUE        : FEC_INI_EJECUCION - FECHA_REGISTRO (time-to-start)
  DIAS_PLANIFICADOS    : FEC_FIN_EJECUCION - FEC_INI_EJECUCION (planned duration)
  FLAG_SIN_AVANCE_FISICO : 1 when AVANCE_FISICO is null (no physical report)
  FLAG_FIN_ANTES_INICIO  : 1 when FEC_FIN < FEC_INI (date coherence error)

Business rules:
  - AVANCE_FISICO for CLOSED projects: if still null after Silver coalesce, set to 100.0.
  - AVANCE_FISICO cap: values > 100 are data-entry errors; cap to 100.0.
"""
import polars as pl
from datetime import datetime, timezone
from config import SILVER_MASTER, GOLD_MASTER


def run_gold() -> None:
    print("Gold layer — business metric derivation\n")

    df = pl.read_parquet(SILVER_MASTER)
    today = datetime.now(tz=timezone.utc).replace(tzinfo=None)

    # -- Business rules on AVANCE_FISICO -----------------------------------------------
    # Rule 1: closed projects with no physical report are assumed 100% complete
    df = df.with_columns(
        pl.when(
            (pl.col("LIFECYCLE") == "CLOSED") & pl.col("AVANCE_FISICO").is_null()
        )
        .then(pl.lit(100.0))
        .otherwise(pl.col("AVANCE_FISICO"))
        .alias("AVANCE_FISICO")
    )

    # Rule 2: cap data-entry errors above 100%
    for col in ("AVANCE_FISICO", "AVANCE_EJECUCION"):
        if col in df.columns:
            df = df.with_columns(pl.col(col).clip(upper_bound=100.0))

    # -- Derived metrics ---------------------------------------------------------------
    derived = []

    if "AVANCE_EJECUCION" in df.columns and "AVANCE_FISICO" in df.columns:
        derived.append(
            (pl.col("AVANCE_EJECUCION") - pl.col("AVANCE_FISICO")).alias("BRECHA")
        )

    if "ULT_FEC_DECLA_ESTIM" in df.columns:
        derived.append(
            (pl.lit(today) - pl.col("ULT_FEC_DECLA_ESTIM"))
            .dt.total_days()
            .alias("DIAS_SIN_REPORTE")
        )

    if "FEC_INI_EJECUCION" in df.columns and "FECHA_REGISTRO" in df.columns:
        derived.append(
            (pl.col("FEC_INI_EJECUCION") - pl.col("FECHA_REGISTRO"))
            .dt.total_days()
            .alias("DIAS_ARRANQUE")
        )

    if "FEC_FIN_EJECUCION" in df.columns and "FEC_INI_EJECUCION" in df.columns:
        derived.append(
            (pl.col("FEC_FIN_EJECUCION") - pl.col("FEC_INI_EJECUCION"))
            .dt.total_days()
            .alias("DIAS_PLANIFICADOS")
        )

    # Flags
    if "AVANCE_FISICO" in df.columns:
        derived.append(
            pl.col("AVANCE_FISICO").is_null().cast(pl.Int8).alias("FLAG_SIN_AVANCE_FISICO")
        )

    if "FEC_FIN_EJECUCION" in df.columns and "FEC_INI_EJECUCION" in df.columns:
        derived.append(
            (pl.col("FEC_FIN_EJECUCION") <= pl.col("FEC_INI_EJECUCION"))
            .cast(pl.Int8)
            .alias("FLAG_FECHAS_INCONSISTENTES")
        )

    if derived:
        df = df.with_columns(derived)

    df.write_parquet(GOLD_MASTER)
    print(f"  Gold saved: {len(df):,} rows x {df.width} cols -> {GOLD_MASTER.name}")
    print(f"  Derived columns: BRECHA, DIAS_SIN_REPORTE, DIAS_ARRANQUE, DIAS_PLANIFICADOS, FLAGS")


if __name__ == "__main__":
    run_gold()
