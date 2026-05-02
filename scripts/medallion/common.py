from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


# Directory configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


def ensure_dir(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


@dataclass
class DatasetConfig:
    """Configuration for a dataset in the medallion pipeline."""
    slug: str
    unique_key: bool = False
    key_columns: list[str] | None = None
    period_columns: list[str] | None = None
    numeric_regex: str = r"^(MONTO|DEVENGADO|PRESUPUESTO|AVANCE|EJECUTADO|VIGENTE|MODIFICADO|DEV_|TOTAL)"


# Define dataset configurations
DATASET_CONFIGS = [
    DatasetConfig(
        slug="detalle-de-inversiones",
        unique_key=True,
        key_columns=["CODIGO_UNICO"],
        period_columns=[],
        numeric_regex=r"^(MONTO|PRESUPUESTO|AVANCE)",
    ),
    DatasetConfig(
        slug="formato-12b-de-de-inversiones",
        unique_key=True,
        key_columns=["CODIGO_UNICO"],
        period_columns=["ULT_PERIODO_REG_F12B"],
        numeric_regex=r"^(MONTO|DEVENGADO|PRESUPUESTO|AVANCE|EJECUTADO|VIGENTE|MODIFICADO|DEV_|PIM_)",
    ),
    DatasetConfig(
        slug="estado-situacional-de-inversiones",
        unique_key=False,
        key_columns=None,
        period_columns=["PERIODO"],
        numeric_regex=r"^(MONTO|PRESUPUESTO|AVANCE)",
    ),
    DatasetConfig(
        slug="proceso-de-seleccion-de-inversiones",
        unique_key=False,
        key_columns=None,
        period_columns=["PERIODO"],
        numeric_regex=r"^(MONTO|PRESUPUESTO|AVANCE|EJECUCION)",
    ),
    DatasetConfig(
        slug="cierre-de-inversiones",
        unique_key=True,
        key_columns=["CODIGO_UNICO"],
        period_columns=[],
        numeric_regex=r"^(MONTO|TOTAL|PRESUPUESTO|LIQUIDACION)",
    ),
]


def standardize_cui(value: str) -> str | None:
    """
    Standardize CODIGO_UNICO: remove decimals, trim whitespace.
    
    Examples:
        "12345.0" -> "12345"
        "  12345  " -> "12345"
    """
    if value is None or (isinstance(value, float) and value != value):  # NaN check
        return None
    value_str = str(value).strip()
    if "." in value_str:
        value_str = value_str.split(".")[0]
    return value_str if value_str else None


def normalize_period(value: str) -> str | None:
    """
    Normalize period format: YYYYMM -> YYYY-MM.
    
    Examples:
        "202301" -> "2023-01"
        "2023-01" -> "2023-01"
        "2023/01" -> "2023-01"
    """
    if value is None or (isinstance(value, float) and value != value):  # NaN check
        return None
    value_str = str(value).strip()
    
    # Already in YYYY-MM format
    if re.match(r"^\d{4}-\d{2}$", value_str):
        return value_str
    
    # YYYYMM format
    if re.match(r"^\d{6}$", value_str):
        return f"{value_str[:4]}-{value_str[4:6]}"
    
    # YYYY/MM format
    if re.match(r"^\d{4}/\d{2}$", value_str):
        return value_str.replace("/", "-")
    
    # Try to extract YYYY and MM from various formats
    match = re.search(r"(\d{4})[/-]?(\d{2})", value_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    
    return value_str
