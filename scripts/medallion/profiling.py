from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from .common import OUTPUTS_DIR, RAW_DIR, ensure_dir


def profile_dataset(dataset_slug: str) -> dict:
    """
    Generate comprehensive profiling report for a dataset.
    
    Returns dictionary with:
    - profile_df: Polars DataFrame with column-level statistics
    - bitacora: List of dictionaries documenting profiling steps
    - output_path: Path to saved profile CSV
    """
    csv_path = RAW_DIR / dataset_slug / "data.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")
    
    # Read dataset
    df = pl.read_csv(csv_path, ignore_errors=True)
    
    # Build profile data
    profile_rows = []
    for column in df.columns:
        dtype = str(df[column].dtype)
        
        # Count nulls
        null_count = df[column].is_null().sum()
        null_pct = (null_count / len(df)) * 100 if len(df) > 0 else 0
        
        # Cardinality
        unique_count = df[column].n_unique()
        
        # Duplicates (non-null rows minus unique)
        non_null_count = df[column].is_not_null().sum()
        duplicate_count = non_null_count - unique_count if non_null_count > unique_count else 0
        
        profile_rows.append({
            "column": column,
            "dtype": dtype,
            "non_null_count": non_null_count,
            "null_count": null_count,
            "null_pct": round(null_pct, 2),
            "unique_count": unique_count,
            "duplicate_count": duplicate_count,
            "cardinality_pct": round((unique_count / non_null_count * 100) if non_null_count > 0 else 0, 2),
        })
    
    profile_df = pl.DataFrame(profile_rows)
    
    # Save profile
    profile_dir = OUTPUTS_DIR / "profiling"
    ensure_dir(profile_dir)
    profile_path = profile_dir / f"{dataset_slug}_profile.csv"
    profile_df.write_csv(profile_path)
    
    # Create bitacora entry
    bitacora = [
        {
            "layer": "profiling",
            "dataset": dataset_slug,
            "rule": "generate_profile",
            "note": f"Profiled {len(df)} rows, {len(df.columns)} columns",
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "output_file": str(profile_path.relative_to(OUTPUTS_DIR.parent)),
        }
    ]
    
    return {
        "profile_df": profile_df,
        "bitacora": bitacora,
        "output_path": profile_path,
    }


def profile_all_datasets(dataset_slugs: list[str]) -> dict:
    """Profile all datasets and combine bitácora."""
    profile_results = {}
    all_bitacora = []
    
    for slug in dataset_slugs:
        try:
            result = profile_dataset(slug)
            profile_results[slug] = result
            all_bitacora.extend(result["bitacora"])
        except Exception as e:
            print(f"Error profiling {slug}: {e}")
    
    # Save combined bitácora
    if all_bitacora:
        bitacora_df = pl.DataFrame(all_bitacora)
        bitacora_path = OUTPUTS_DIR / "bitacora" / "bitacora_profiling.csv"
        ensure_dir(bitacora_path.parent)
        bitacora_df.write_csv(bitacora_path)
    
    return {
        "profiles": profile_results,
        "bitacora_path": OUTPUTS_DIR / "bitacora" / "bitacora_profiling.csv" if all_bitacora else None,
    }


if __name__ == "__main__":
    from .common import DATASET_CONFIGS
    
    slugs = [config.slug for config in DATASET_CONFIGS]
    result = profile_all_datasets(slugs)
    print(f"Profiling complete. Bitácora: {result['bitacora_path']}")
