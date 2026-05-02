"""
03_silver.py
Cleaning, merging, and enrichment layer. Reads from Bronze, writes Silver.

Steps:
  1. Strip CSV artefacts (quotes, whitespace) from all string columns.
  2. Build master project universe by unioning Detalle (ACTIVE) + Cierre (CLOSED).
  3. Impute categoricals: null/empty -> "DESCONOCIDO".
  4. Enrich with F12B: left join to add operational tracking variables.
  5. Coalesce AVANCE_FISICO: prefer F12B value (more recent) over Detalle.
  6. Parse dates: standard datetime columns + YYYYMM columns (PRIMER/ULTIMO_DEVENGADO).
  7. Semantic NLP classification of ULT_PROBLEMA via SentenceTransformers.
  8. Cast selected numeric columns to Float64.
"""
import polars as pl
from sentence_transformers import SentenceTransformer, util
from config import DETALLE_BRONZE, F12B_BRONZE, CIERRE_BRONZE, SILVER_MASTER

# ---------------------------------------------------------------------------
# Selected columns per dataset (from seleccion_variables_3datasets.xlsx)
# ---------------------------------------------------------------------------

DETALLE_COLS = [
    "CODIGO_UNICO", "ESTADO", "SITUACION", "MONTO_VIABLE", "COSTO_ACTUALIZADO",
    "DEPARTAMENTO", "PROVINCIA", "DISTRITO", "UBIGEO", "SECTOR", "ENTIDAD",
    "TIPO_INVERSION", "MARCO", "NIVEL", "FUNCION",
    "FECHA_REGISTRO", "FECHA_VIABILIDAD",
    "FEC_INI_EJECUCION", "FEC_FIN_EJECUCION",
    "FEC_INI_EJEC_FISICA", "FEC_FIN_EJEC_FISICA",
    "LATITUD", "LONGITUD", "NUM_HABITANTES_BENEF",
    "EXPEDIENTE_TECNICO",
    "TIENE_F8", "TIENE_F12B", "TIENE_AVAN_FISICO",
]

CIERRE_COLS = [
    "CODIGO_UNICO", "ESTADO", "SITUACION", "MONTO_VIABLE", "COSTO_ACTUALIZADO",
    "DEPARTAMENTO", "PROVINCIA", "DISTRITO", "UBIGEO", "SECTOR", "ENTIDAD",
    "TIPO_INVERSION", "MARCO", "NIVEL", "FUNCION",
    "FECHA_REGISTRO", "FECHA_VIABILIDAD",
    "LATITUD", "LONGITUD",
    "FEC_CIERRE", "CULMINADA", "INFORME_CIERRE",
    "INICIO_EJEC_FISICA", "CULMINA_EJEC_FISICA",
]

F12B_COLS = [
    "CODIGO_UNICO",
    "ULT_PROBLEMA", "ULT_ESTADO_SITUACIONAL",
    "AVANCE_FISICO", "AVANCE_EJECUCION",
    "ULT_FEC_DECLA_ESTIM",
    "PRIMER_DEVENGADO", "ULTIMO_DEVENGADO",
    "DEVENGADO_ACUMULADO",
]

# Categoricals to impute with DESCONOCIDO when null/empty
CATS_TO_IMPUTE = [
    "DEPARTAMENTO", "PROVINCIA", "DISTRITO",
    "SECTOR", "ENTIDAD", "SITUACION", "ESTADO",
    "TIPO_INVERSION", "MARCO", "NIVEL", "FUNCION",
]

# Standard datetime columns (format: YYYY-MM-DD HH:MM:SS)
STD_DATE_COLS = [
    "FECHA_REGISTRO", "FECHA_VIABILIDAD",
    "ULT_FEC_DECLA_ESTIM",
    "FEC_INI_EJECUCION", "FEC_FIN_EJECUCION",
    "FEC_INI_EJEC_FISICA", "FEC_FIN_EJEC_FISICA",
    "FEC_CIERRE",
    "INICIO_EJEC_FISICA", "CULMINA_EJEC_FISICA",
]

NUMERIC_COLS = [
    "MONTO_VIABLE", "COSTO_ACTUALIZADO",
    "AVANCE_FISICO", "AVANCE_EJECUCION",
    "DEVENGADO_ACUMULADO", "NUM_HABITANTES_BENEF",
    "LATITUD", "LONGITUD",
]

# Semantic anchors for zero-shot NLP classification (Spanish)
NLP_CATEGORIES = {
    "SOCIAL":      "Conflictos con la comunidad, huelgas, paralización social, oposición de pobladores.",
    "PRESUPUESTO": "Falta de presupuesto, demora en transferencia de recursos, problemas financieros.",
    "TECNICO":     "Deficiencias en expediente técnico, fallas de diseño, problemas de terreno o clima.",
    "CONTRATACION":"Problemas en licitación, controversias contractuales, arbitraje, demora en selección.",
    "EMERGENCIA":  "Estado de emergencia, pandemia, covid-19, desastres naturales, fenómeno El Niño.",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def strip_artefacts(df: pl.DataFrame) -> pl.DataFrame:
    """Remove CSV quote artefacts and leading/trailing whitespace from strings."""
    exprs = [
        pl.col(c).str.replace_all('"', "").str.strip_chars()
        if df[c].dtype == pl.String else pl.col(c)
        for c in df.columns
    ]
    return df.select(exprs)


def parse_yyyymm(col: str) -> pl.Expr:
    """Convert a YYYYMM string column to a Date (first day of month)."""
    return (
        pl.when(pl.col(col).str.len_chars() == 6)
        .then(
            pl.format("{}-{}-01", pl.col(col).str.slice(0, 4), pl.col(col).str.slice(4, 2))
            .str.to_date(strict=False)
        )
        .otherwise(pl.lit(None).cast(pl.Date))
        .alias(f"FEC_{col}")
    )


def classify_hybrid(
    series: pl.Series,
    categories: dict[str, str],
    model_name: str = "all-MiniLM-L6-v2",
) -> pl.Series:
    """
    Hybrid classification:
    1. Regex-based fast matching for common patterns.
    2. Zero-shot NLP for the remainder (sampled top unique).
    """
    print("    Running Hybrid NLP classification...")
    
    # 1. Regex Pass
    df_text = series.to_frame().with_columns([
        pl.col(series.name).str.to_lowercase().alias("_clean")
    ])
    
    res = df_text.with_columns(
        pl.when(pl.col("_clean").str.contains("social|comunidad|poblacion|huelga|protesta"))
          .then(pl.lit("SOCIAL"))
          .when(pl.col("_clean").str.contains("presupuesto|financiero|recursos|transferencia|dinero|pago|pension"))
          .then(pl.lit("PRESUPUESTO"))
          .when(pl.col("_clean").str.contains("tecnico|expediente|terreno|diseño|suelo|clima|terreno|lluvia"))
          .then(pl.lit("TECNICO"))
          .when(pl.col("_clean").str.contains("licitacion|contrato|arbitraje|proceso|legal|norma|adenda"))
          .then(pl.lit("CONTRATACION"))
          .when(pl.col("_clean").str.contains("covid|pandemia|emergencia|sanitaria"))
          .then(pl.lit("EMERGENCIA"))
          .otherwise(pl.lit(None))
          .alias("CATEGORIA_PROBLEMA")
    )

    # 2. NLP Pass for remaining nulls
    unclassified = res.filter(pl.col("CATEGORIA_PROBLEMA").is_null() & pl.col(series.name).is_not_null())
    unique_unclassified = unclassified[series.name].value_counts().sort("count", descending=True).head(2000)
    
    if len(unique_unclassified) > 0:
        print(f"    Deep NLP on {len(unique_unclassified)} unique unclassified texts...")
        texts = unique_unclassified[series.name].to_list()
        
        model = SentenceTransformer(model_name)
        cat_names = list(categories.keys())
        cat_anchors = list(categories.values())
        
        anchor_emb = model.encode(cat_anchors, convert_to_tensor=True, show_progress_bar=False)
        text_emb = model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
        
        cos_sim = util.cos_sim(text_emb, anchor_emb)
        best_idx = cos_sim.argmax(dim=1).tolist()
        mapping = {t: cat_names[idx] for t, idx in zip(texts, best_idx)}
        
        res = res.with_columns(
            pl.col("CATEGORIA_PROBLEMA").fill_null(pl.col(series.name).replace_strict(mapping, default="OTRO"))
        )
    else:
        res = res.with_columns(pl.col("CATEGORIA_PROBLEMA").fill_null(pl.lit("OTRO")))

    return res["CATEGORIA_PROBLEMA"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_silver() -> None:
    print("Silver layer — clean, merge, enrich\n")

    # 1. Load & strip artefacts
    df_det  = strip_artefacts(pl.read_parquet(DETALLE_BRONZE))
    df_f12b = strip_artefacts(pl.read_parquet(F12B_BRONZE))
    df_cie  = strip_artefacts(pl.read_parquet(CIERRE_BRONZE))

    # 2. Build project universe (Detalle ACTIVE + Cierre CLOSED)
    cols_det = [c for c in DETALLE_COLS if c in df_det.columns]
    cols_cie = [c for c in CIERRE_COLS  if c in df_cie.columns]

    df_master = pl.concat([
        df_det.select(cols_det).with_columns(pl.lit("ACTIVE").alias("LIFECYCLE")),
        df_cie.select(cols_cie).with_columns(pl.lit("CLOSED").alias("LIFECYCLE")),
    ], how="diagonal")

    print(f"  Project universe: {len(df_master):,} rows")

    # 3. Impute categoricals
    impute_exprs = [
        pl.when((pl.col(c).is_null()) | (pl.col(c).str.strip_chars() == ""))
        .then(pl.lit("DESCONOCIDO"))
        .otherwise(pl.col(c))
        .alias(c)
        for c in CATS_TO_IMPUTE if c in df_master.columns
    ]
    if impute_exprs:
        df_master = df_master.with_columns(impute_exprs)

    # 4. Prepare F12B enrichment
    cols_f12b = [c for c in F12B_COLS if c in df_f12b.columns]
    df_f12b_sub = df_f12b.select(cols_f12b)

    # Parse YYYYMM dates before join
    yyyymm_present = [c for c in ("PRIMER_DEVENGADO", "ULTIMO_DEVENGADO") if c in df_f12b_sub.columns]
    if yyyymm_present:
        df_f12b_sub = df_f12b_sub.with_columns([parse_yyyymm(c) for c in yyyymm_present])

    # 5. Semantic NLP on ULT_PROBLEMA
    if "ULT_PROBLEMA" in df_f12b_sub.columns:
        df_f12b_sub = df_f12b_sub.with_columns(
            classify_hybrid(df_f12b_sub["ULT_PROBLEMA"], NLP_CATEGORIES).alias("CATEGORIA_PROBLEMA")
        )

    # 6. Left join master + F12B
    df_silver = df_master.join(df_f12b_sub, on="CODIGO_UNICO", how="left", suffix="_F12B")

    # 7. Coalesce AVANCE_FISICO (F12B preferred, Detalle as fallback)
    if "AVANCE_FISICO_F12B" in df_silver.columns:
        df_silver = df_silver.with_columns(
            pl.coalesce(["AVANCE_FISICO_F12B", "AVANCE_FISICO"]).alias("AVANCE_FISICO")
        ).drop("AVANCE_FISICO_F12B")

    # Imputation Rule from User Script: If TIENE_AVAN_FISICO == "NO" then AVANCE_FISICO = 0
    if "TIENE_AVAN_FISICO" in df_silver.columns and "AVANCE_FISICO" in df_silver.columns:
        df_silver = df_silver.with_columns(
            pl.when((pl.col("TIENE_AVAN_FISICO") == "NO") & pl.col("AVANCE_FISICO").is_null())
            .then(pl.lit(0.0))
            .otherwise(pl.col("AVANCE_FISICO"))
            .alias("AVANCE_FISICO")
        )

    # 8. Parse standard datetime columns & Handle Outliers
    from datetime import datetime
    max_year = datetime.now().year + 10
    
    for c in STD_DATE_COLS:
        if c in df_silver.columns:
            df_silver = df_silver.with_columns(
                pl.col(c).str.to_datetime(strict=False).alias(c)
            )
            # Nullify extreme future dates (outliers)
            df_silver = df_silver.with_columns(
                pl.when(pl.col(c).dt.year() > max_year)
                .then(pl.lit(None))
                .otherwise(pl.col(c))
                .alias(c)
            )

    # 9. Cast numeric columns
    for c in NUMERIC_COLS:
        if c in df_silver.columns:
            df_silver = df_silver.with_columns(
                pl.col(c).cast(pl.Float64, strict=False)
            )

    df_silver.write_parquet(SILVER_MASTER)
    print(f"\n  Silver saved: {len(df_silver):,} rows x {df_silver.width} cols -> {SILVER_MASTER.name}")


if __name__ == "__main__":
    run_silver()
