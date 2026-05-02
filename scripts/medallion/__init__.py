"""
Medallion Architecture Pipeline

Bronze → Silver → Gold

Modules:
- common: Configuration and utility functions
- profiling: Data quality analysis
- bronze_to_silver: Cleaning and normalization
- silver_to_gold: Dimensional modeling
"""

from .common import DATASET_CONFIGS, RAW_DIR, PROCESSED_DIR, OUTPUTS_DIR, ensure_dir
from .profiling import profile_dataset, profile_all_datasets
from .bronze_to_silver import run_pipeline as run_bronze_to_silver
from .silver_to_gold import run_pipeline as run_silver_to_gold

__all__ = [
    "DATASET_CONFIGS",
    "RAW_DIR",
    "PROCESSED_DIR", 
    "OUTPUTS_DIR",
    "ensure_dir",
    "profile_dataset",
    "profile_all_datasets",
    "run_bronze_to_silver",
    "run_silver_to_gold",
]
