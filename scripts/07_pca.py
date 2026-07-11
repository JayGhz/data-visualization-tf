"""
07_pca.py
Entrega 6 -- Componente avanzado: PCA sobre la tabla de hechos.

Lee fact_inversiones.csv (esquema estrella, salida de 06_star_schema.py)
y aplica Analisis de Componentes Principales (PCA) con scikit-learn
sobre las 6 metricas numericas centrales del proyecto:

  BRECHA             : desalineacion financiero-fisica (pp)
  AVANCE_FISICO      : % de avance fisico reportado
  AVANCE_EJECUCION   : % de ejecucion financiera
  DIAS_SIN_REPORTE   : dias desde el ultimo reporte (staleness)
  DIAS_ARRANQUE      : dias entre registro e inicio de ejecucion
  COSTO_ACTUALIZADO  : costo total actualizado (S/)

Decisiones metodologicas:
  - Nulos imputados con la MEDIANA de cada variable (robusta a la fuerte
    asimetria de COSTO_ACTUALIZADO y de las variables de dias).
  - Estandarizacion z-score (StandardScaler) antes del PCA: las variables
    estan en unidades incomparables (pp, dias, soles) y sin escalar el
    costo dominaria la varianza total.
  - 2 componentes (PC1, PC2) para proyectar en un scatter de Tableau.

Salida:
  data/gold/pca_proyectos.csv con columnas:
    SK_Proyecto, PC1, PC2, SEMAFORO_BRECHA, LIFECYCLE, SECTOR
  (SECTOR se recupera via join con dim_institucion.csv)
"""
import sys
from pathlib import Path

# Permite ejecutar el script directamente: python scripts/07_pca.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from config import GOLD_DIR

FACT_CSV = GOLD_DIR / "fact_inversiones.csv"
DIM_INSTITUCION_CSV = GOLD_DIR / "dim_institucion.csv"
PCA_CSV = GOLD_DIR / "pca_proyectos.csv"

# Variables numericas sobre las que se aplica el PCA
PCA_FEATURES = [
    "BRECHA",
    "AVANCE_FISICO",
    "AVANCE_EJECUCION",
    "DIAS_SIN_REPORTE",
    "DIAS_ARRANQUE",
    "COSTO_ACTUALIZADO",
]

# Columnas de contexto que acompanan a PC1/PC2 en el export
CONTEXT_COLS = ["SK_Proyecto", "SEMAFORO_BRECHA", "LIFECYCLE"]


def run_pca() -> None:
    print("Entrega 6 -- PCA sobre fact_inversiones\n")

    fact = pd.read_csv(
        FACT_CSV,
        usecols=CONTEXT_COLS + PCA_FEATURES + ["SK_Institucion"],
    )
    print(f"Fact cargada: {len(fact):,} filas")

    # SECTOR via dim_institucion (el esquema estrella no lo guarda en la fact)
    dim_inst = pd.read_csv(DIM_INSTITUCION_CSV, usecols=["SK_Institucion", "SECTOR"])
    fact = fact.merge(dim_inst, on="SK_Institucion", how="left")

    # -- Imputacion de nulos con la mediana --------------------------------
    nulos = fact[PCA_FEATURES].isna().sum()
    print("\nNulos por variable (antes de imputar):")
    for var, n in nulos.items():
        print(f"  {var:<20}: {n:>8,} ({n / len(fact) * 100:.1f}%)")

    imputer = SimpleImputer(strategy="median")
    X = imputer.fit_transform(fact[PCA_FEATURES])

    print("\nMedianas usadas para imputar:")
    for var, med in zip(PCA_FEATURES, imputer.statistics_):
        print(f"  {var:<20}: {med:,.2f}")

    # -- Estandarizacion + PCA ---------------------------------------------
    X_std = StandardScaler().fit_transform(X)

    pca = PCA(n_components=2, random_state=42)
    componentes = pca.fit_transform(X_std)

    print("\nVarianza explicada:")
    for i, var in enumerate(pca.explained_variance_ratio_, start=1):
        print(f"  PC{i}: {var * 100:.2f}%")
    print(f"  Total (PC1+PC2): {pca.explained_variance_ratio_.sum() * 100:.2f}%")

    print("\nCargas (loadings) de cada variable:")
    loadings = pd.DataFrame(
        pca.components_.T,
        index=PCA_FEATURES,
        columns=["PC1", "PC2"],
    )
    print(loadings.round(3).to_string())

    # -- Export --------------------------------------------------------------
    out = fact[["SK_Proyecto", "SEMAFORO_BRECHA", "LIFECYCLE", "SECTOR"]].copy()
    # Int64 nullable: la fact trae 1 SK_Proyecto nulo y pandas lo leeria como
    # float64, rompiendo el join por tipo en Tableau
    out["SK_Proyecto"] = out["SK_Proyecto"].astype("Int64")
    out.insert(1, "PC1", componentes[:, 0].round(4))
    out.insert(2, "PC2", componentes[:, 1].round(4))
    out = out[["SK_Proyecto", "PC1", "PC2", "SEMAFORO_BRECHA", "LIFECYCLE", "SECTOR"]]

    out.to_csv(PCA_CSV, index=False)
    size_mb = PCA_CSV.stat().st_size / 1024 / 1024
    print(f"\nExportado: {PCA_CSV}  ({len(out):,} filas x {out.shape[1]} cols, {size_mb:.1f} MB)")


if __name__ == "__main__":
    run_pca()
