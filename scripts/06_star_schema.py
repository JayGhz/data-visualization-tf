"""
06_star_schema.py
Entrega 4 -- Esquema estrella con llaves sustitutas para Tableau.

Lee el Gold master, calcula metricas de segmentacion y exporta
6 tablas en esquema estrella listas para conectar en Tableau:

  fact_inversiones.csv  -- tabla de hechos central con SK_ y medidas
  dim_proyecto.csv      -- atributos de identidad y estado del proyecto
  dim_ubicacion.csv     -- geografia con SK_Ubicacion
  dim_institucion.csv   -- entidad ejecutora con SK_Institucion
  dim_estructura.csv    -- clasificacion funcional con SK_Estructura
  dim_tiempo.csv        -- calendario estandar con SK_Tiempo (YYYYMMDD)

Justificacion del modelo estrella:
  Se eligio esquema estrella sobre tabla plana (OBT) porque:
  - Evita redundancia de texto en columnas categoricas repetidas
  - Las llaves sustitutas (SK_) permiten joins eficientes en Tableau
  - Tableau gestiona relaciones 1:1 con mejor rendimiento que tablas anchas
  - Permite filtros independientes por dimension sin afectar otras vistas
  - Es el modelo estandar de BI para dashboards de inversion publica

Relaciones en Tableau (todas por llave sustituta):
  fact_inversiones.SK_Proyecto    → dim_proyecto.CODIGO_UNICO
  fact_inversiones.SK_Ubicacion   → dim_ubicacion.SK_Ubicacion
  fact_inversiones.SK_Institucion → dim_institucion.SK_Institucion
  fact_inversiones.SK_Estructura  → dim_estructura.SK_Estructura
  fact_inversiones.SK_Tiempo_*    → dim_tiempo.SK_Tiempo
"""
import polars as pl
from config import GOLD_MASTER, GOLD_DIR


# ---------------------------------------------------------------------------
# Metricas de segmentacion
# ---------------------------------------------------------------------------

def calcular_semaforos(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calcula columnas de semaforo y segmentacion para el dashboard.
    Estas columnas van a fact_inversiones para que Tableau las use
    como filtros y colores en las vistas.
    """
    return df.with_columns([

        # SEMAFORO_BRECHA: clasifica la desalineacion financiero-fisica
        # <= 10pp: diferencia esperada por desfase de registro (NORMAL)
        # 10-30pp: requiere seguimiento activo (ALERTA)
        # > 30pp: posible irregularidad, bandera roja (CRITICO)
        pl.when(pl.col("BRECHA").is_null())
            .then(pl.lit("SIN DATO"))
          .when(pl.col("BRECHA") <= 10)
            .then(pl.lit("NORMAL"))
          .when(pl.col("BRECHA") <= 30)
            .then(pl.lit("ALERTA"))
          .otherwise(pl.lit("CRITICO"))
          .alias("SEMAFORO_BRECHA"),

        # SEMAFORO_REPORTE: clasifica la vigencia del ultimo reporte
        # <= 30 dias: al dia / <= 90 dias: rezagado / > 90: paralizado
        pl.when(pl.col("DIAS_SIN_REPORTE").is_null())
            .then(pl.lit("SIN DATO"))
          .when(pl.col("DIAS_SIN_REPORTE") <= 30)
            .then(pl.lit("AL DIA"))
          .when(pl.col("DIAS_SIN_REPORTE") <= 90)
            .then(pl.lit("REZAGADO"))
          .otherwise(pl.lit("PARALIZADO"))
          .alias("SEMAFORO_REPORTE"),

        # RANGO_COSTO: segmenta proyectos por envergadura presupuestal
        # Permite analizar si los megaproyectos tienen peor ejecucion
        pl.when(pl.col("COSTO_ACTUALIZADO") < 500_000)
            .then(pl.lit("PEQUENO"))
          .when(pl.col("COSTO_ACTUALIZADO") < 5_000_000)
            .then(pl.lit("MEDIANO"))
          .when(pl.col("COSTO_ACTUALIZADO") < 50_000_000)
            .then(pl.lit("GRANDE"))
          .otherwise(pl.lit("MEGAPROYECTO"))
          .alias("RANGO_COSTO"),

        # PCT_EJECUCION_PRESUPUESTAL: porcentaje del costo total ejecutado
        # Complementa AVANCE_FISICO para detectar proyectos que gastan
        # sin avanzar fisicamente
        (pl.col("DEVENGADO_ACUMULADO") /
         pl.col("COSTO_ACTUALIZADO") * 100)
         .round(2)
         .alias("PCT_EJECUCION_PRESUPUESTAL"),
    ])


# ---------------------------------------------------------------------------
# Dimensiones con llaves sustitutas
# ---------------------------------------------------------------------------

def build_dim_ubicacion(df: pl.DataFrame) -> pl.DataFrame:
    """
    dim_ubicacion: geografia de la inversion.
    SK_Ubicacion es llave sustituta numerica autogenerada.
    Unica por combinacion UBIGEO.
    """
    dim = (
        df.select(["UBIGEO", "DEPARTAMENTO", "PROVINCIA", "DISTRITO",
                   "LATITUD", "LONGITUD"])
          .unique(subset=["UBIGEO"])
          .with_row_index(offset=1)
          .rename({"index": "SK_Ubicacion"})
    )
    return dim


def build_dim_institucion(df: pl.DataFrame) -> pl.DataFrame:
    """
    dim_institucion: entidad ejecutora e institucionalidad.
    SK_Institucion es llave sustituta numerica autogenerada.
    Unica por combinacion SECTOR + ENTIDAD.
    """
    dim = (
        df.select(["SECTOR", "ENTIDAD", "NIVEL"])
          .unique(subset=["SECTOR", "ENTIDAD"])
          .with_row_index(offset=1)
          .rename({"index": "SK_Institucion"})
    )
    return dim


def build_dim_estructura(df: pl.DataFrame) -> pl.DataFrame:
    """
    dim_estructura: clasificacion funcional del proyecto.
    SK_Estructura es llave sustituta numerica autogenerada.
    Unica por FUNCION.
    """
    dim = (
        df.select(["FUNCION", "TIPO_INVERSION", "MARCO"])
          .unique(subset=["FUNCION"])
          .with_row_index(offset=1)
          .rename({"index": "SK_Estructura"})
    )
    return dim


def build_dim_proyecto(df: pl.DataFrame) -> pl.DataFrame:
    """
    dim_proyecto: identidad y estado del proyecto.
    Usa CODIGO_UNICO como llave natural (ya es unico por proyecto).
    Incluye atributos cualitativos y flags de formularios.
    """
    cols = [
        "CODIGO_UNICO",
        "ESTADO",
        "SITUACION",
        "LIFECYCLE",
        "EXPEDIENTE_TECNICO",
        "TIENE_F8",
        "TIENE_F12B",
        "TIENE_AVAN_FISICO",
        "CULMINADA",
        "INFORME_CIERRE",
        "CATEGORIA_PROBLEMA",
        "ULT_PROBLEMA",
        "ULT_ESTADO_SITUACIONAL",
    ]
    return df.select([c for c in cols if c in df.columns]).unique("CODIGO_UNICO")


def build_dim_tiempo() -> pl.DataFrame:
    """
    dim_tiempo: calendario estandar de 2000 a 2035.
    SK_Tiempo = YYYYMMDD como entero (ej: 20260101).
    Se une con fact_inversiones por las columnas SK_Tiempo_*.
    """
    fechas = pl.date_range(
        start=pl.date(2000, 1, 1),
        end=pl.date(2035, 12, 31),
        interval="1d",
        eager=True
    )
    dim = pl.DataFrame({"FECHA": fechas}).with_columns([
        pl.col("FECHA").dt.year().alias("ANIO"),
        pl.col("FECHA").dt.month().alias("MES"),
        pl.col("FECHA").dt.quarter().alias("TRIMESTRE"),
        pl.col("FECHA").dt.month().map_elements(
            lambda m: ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                       "Julio","Agosto","Setiembre","Octubre","Noviembre","Diciembre"][m-1],
            return_dtype=pl.String
        ).alias("NOMBRE_MES"),
        (pl.col("FECHA").dt.year() * 10000 +
         pl.col("FECHA").dt.month() * 100 +
         pl.col("FECHA").dt.day()).cast(pl.Int64).alias("SK_Tiempo"),
    ])
    return dim


# ---------------------------------------------------------------------------
# Helper para convertir fecha a SK_Tiempo (YYYYMMDD)
# ---------------------------------------------------------------------------

def fecha_a_sk(col_name: str) -> pl.Expr:
    """Convierte columna datetime a SK_Tiempo entero YYYYMMDD."""
    return (
        pl.col(col_name).dt.year() * 10000 +
        pl.col(col_name).dt.month() * 100 +
        pl.col(col_name).dt.day()
    ).cast(pl.Int64).fill_null(-1).alias(f"SK_Tiempo_{col_name}")


# ---------------------------------------------------------------------------
# Tabla de hechos
# ---------------------------------------------------------------------------
def build_fact(df: pl.DataFrame,
               dim_ubicacion: pl.DataFrame,
               dim_institucion: pl.DataFrame,
               dim_estructura: pl.DataFrame) -> pl.DataFrame:
    fact = (
        df
        # Eliminar duplicados en CODIGO_UNICO antes de construir la fact
        # Justificacion: la granularidad de la fact es 1 fila por proyecto
        .unique(subset=["CODIGO_UNICO"], keep="first")
        # Join para obtener SK_Ubicacion
        .join(
            dim_ubicacion.select(["UBIGEO", "SK_Ubicacion"]),
            on="UBIGEO", how="left"
        )
        # Join para obtener SK_Institucion
        .join(
            dim_institucion.select(["SECTOR", "ENTIDAD", "SK_Institucion"]),
            on=["SECTOR", "ENTIDAD"], how="left"
        )
        # Join para obtener SK_Estructura
        .join(
            dim_estructura.select(["FUNCION", "SK_Estructura"]),
            on="FUNCION", how="left"
        )
        .with_columns([
            fecha_a_sk("FECHA_REGISTRO"),
            fecha_a_sk("FECHA_VIABILIDAD"),
            fecha_a_sk("FEC_INI_EJECUCION"),
            fecha_a_sk("FEC_FIN_EJECUCION"),
            fecha_a_sk("ULT_FEC_DECLA_ESTIM"),
        ])
        .select([
            pl.col("CODIGO_UNICO").alias("SK_Proyecto"),
            "SK_Ubicacion",
            "SK_Institucion",
            "SK_Estructura",
            "SK_Tiempo_FECHA_REGISTRO",
            "SK_Tiempo_FECHA_VIABILIDAD",
            "SK_Tiempo_FEC_INI_EJECUCION",
            "SK_Tiempo_FEC_FIN_EJECUCION",
            "SK_Tiempo_ULT_FEC_DECLA_ESTIM",
            "LIFECYCLE",
            "COSTO_ACTUALIZADO",
            "MONTO_VIABLE",
            "DEVENGADO_ACUMULADO",
            "PCT_EJECUCION_PRESUPUESTAL",
            "AVANCE_FISICO",
            "AVANCE_EJECUCION",
            "BRECHA",
            "DIAS_SIN_REPORTE",
            "DIAS_ARRANQUE",
            "DIAS_PLANIFICADOS",
            "SEMAFORO_BRECHA",
            "SEMAFORO_REPORTE",
            "RANGO_COSTO",
            "NUM_HABITANTES_BENEF",
            "FLAG_SIN_AVANCE_FISICO",
            "FLAG_FECHAS_INCONSISTENTES",
        ])
    )
    return fact

# ---------------------------------------------------------------------------
# Validacion del esquema
# ---------------------------------------------------------------------------

def validar_esquema(fact: pl.DataFrame, tables: dict) -> None:
    """Verifica integridad referencial del esquema estrella."""
    print("\n--- Validacion del esquema estrella ---")

    total = len(fact)

    # Duplicados en fact
    dupes = fact["SK_Proyecto"].is_duplicated().sum()
    print(f"  fact_inversiones filas          : {total:,}")
    print(f"  fact_inversiones duplicados SK  : {dupes:,}")
    assert dupes == 0, "La tabla de hechos tiene duplicados en SK_Proyecto"

    # Cobertura de llaves sustitutas
    for sk_col, dim_name in [
        ("SK_Ubicacion",   "dim_ubicacion"),
        ("SK_Institucion", "dim_institucion"),
        ("SK_Estructura",  "dim_estructura"),
    ]:
        sin_llave = fact[sk_col].is_null().sum()
        print(f"  {sk_col:<25}: {sin_llave:,} nulos ({sin_llave/total*100:.1f}%)")

    # Tamano de dimensiones
    print()
    for nombre, df in tables.items():
        print(f"  {nombre:<25}: {len(df):>8,} filas x {df.width} cols")


# ---------------------------------------------------------------------------
# Resumen de segmentos para el informe
# ---------------------------------------------------------------------------

def imprimir_segmentos(fact: pl.DataFrame,
                       dim_institucion: pl.DataFrame,
                       dim_ubicacion: pl.DataFrame) -> None:
    """Imprime distribucion de segmentos para documentar en el informe."""

    df = fact.join(
        dim_institucion.select(["SK_Institucion", "SECTOR"]),
        on="SK_Institucion", how="left"
    ).join(
        dim_ubicacion.select(["SK_Ubicacion", "DEPARTAMENTO"]),
        on="SK_Ubicacion", how="left"
    )

    print("\n--- Distribucion de segmentos ---")

    print("\n  LIFECYCLE:")
    print(df.group_by("LIFECYCLE")
            .agg(pl.len().alias("n"))
            .sort("n", descending=True)
            .to_pandas().to_string(index=False))

    print("\n  SEMAFORO_BRECHA:")
    print(df.group_by("SEMAFORO_BRECHA")
            .agg(pl.len().alias("n"))
            .sort("n", descending=True)
            .to_pandas().to_string(index=False))

    print("\n  RANGO_COSTO:")
    print(df.group_by("RANGO_COSTO")
            .agg(pl.len().alias("n"))
            .sort("n", descending=True)
            .to_pandas().to_string(index=False))

    print("\n  Top 10 SECTOR por brecha media:")
    top = (df.filter(pl.col("BRECHA").is_not_null())
             .group_by("SECTOR")
             .agg([
                 pl.col("BRECHA").mean().round(2).alias("brecha_media"),
                 pl.len().alias("n_proyectos"),
             ])
             .sort("brecha_media", descending=True)
             .head(10))
    print(top.to_pandas().to_string(index=False))

    print("\n  Top 10 DEPARTAMENTO por proyectos criticos:")
    criticos = df.filter(pl.col("SEMAFORO_BRECHA") == "CRITICO")
    if len(criticos) > 0:
        print(criticos.group_by("DEPARTAMENTO")
                      .agg(pl.len().alias("n_criticos"))
                      .sort("n_criticos", descending=True)
                      .head(10)
                      .to_pandas().to_string(index=False))
    else:
        print("  Sin proyectos criticos en el universo filtrado.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_star_schema() -> None:
    print("Entrega 4 -- Esquema estrella con llaves sustitutas\n")

    df = pl.read_parquet(GOLD_MASTER)
    print(f"Gold cargado: {len(df):,} filas x {df.width} cols")

    # Calcular semaforos y segmentos
    df = calcular_semaforos(df)
    print(f"Semaforos calculados. Columnas: {df.width}")

    # Construir dimensiones
    print("\nConstruyendo dimensiones...")
    dim_ubicacion   = build_dim_ubicacion(df)
    dim_institucion = build_dim_institucion(df)
    dim_estructura  = build_dim_estructura(df)
    dim_proyecto    = build_dim_proyecto(df)
    dim_tiempo      = build_dim_tiempo()

    # Construir tabla de hechos
    print("Construyendo tabla de hechos...")
    fact = build_fact(df, dim_ubicacion, dim_institucion, dim_estructura)

    # Agrupar tablas
    tables = {
        "fact_inversiones": fact,
        "dim_proyecto":     dim_proyecto,
        "dim_ubicacion":    dim_ubicacion,
        "dim_institucion":  dim_institucion,
        "dim_estructura":   dim_estructura,
        "dim_tiempo":       dim_tiempo,
    }

    # Validar
    validar_esquema(fact, tables)

    # Segmentos para el informe
    imprimir_segmentos(fact, dim_institucion, dim_ubicacion)

    # Exportar
    print("\n--- Exportando tablas ---")
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    for nombre, tabla in tables.items():
        path = GOLD_DIR / f"{nombre}.csv"
        tabla.write_csv(path)
        size_mb = path.stat().st_size / 1024 / 1024
        print(f"  {nombre:<25}: {len(tabla):>8,} filas "
              f"x {tabla.width:>3} cols  {size_mb:.1f} MB")

    print(f"\n  Exportados en: {GOLD_DIR}")
    print("\nEntrega 4 completa.")
    print("Conecta en Tableau:")
    print("  fact_inversiones.SK_Proyecto    -> dim_proyecto.CODIGO_UNICO")
    print("  fact_inversiones.SK_Ubicacion   -> dim_ubicacion.SK_Ubicacion")
    print("  fact_inversiones.SK_Institucion -> dim_institucion.SK_Institucion")
    print("  fact_inversiones.SK_Estructura  -> dim_estructura.SK_Estructura")
    print("  fact_inversiones.SK_Tiempo_*    -> dim_tiempo.SK_Tiempo")


if __name__ == "__main__":
    run_star_schema()