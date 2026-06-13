from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"

# Raw Data
RAW_DIR = DATA_DIR / "raw"

# Medallion Layers
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

# Specific File Paths
DETALLE_RAW = RAW_DIR / "detalle-de-inversiones" / "data.csv"
F12B_RAW = RAW_DIR / "formato-12b-de-de-inversiones" / "data.csv"
CIERRE_RAW = RAW_DIR / "cierre-de-inversiones" / "data.csv"

# Bronze Files
DETALLE_BRONZE = BRONZE_DIR / "detalle.parquet"
F12B_BRONZE = BRONZE_DIR / "f12b.parquet"
CIERRE_BRONZE = BRONZE_DIR / "cierre.parquet"

# Silver & Gold Files
SILVER_MASTER = SILVER_DIR / "silver_master.parquet"
GOLD_MASTER = GOLD_MATERIALIZED = GOLD_DIR / "gold_master.parquet"


# Ensure dirs exist
for d in [BRONZE_DIR, SILVER_DIR, GOLD_DIR, RAW_DIR]:
    d.mkdir(parents=True, exist_ok=True)
