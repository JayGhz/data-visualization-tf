"""
run_pipeline.py
Orchestrates the full Medallion pipeline.

Usage:
    python run_pipeline.py [--from STEP]

Steps:
    0  download        Download raw CSVs from MEF (optional)
    1  bronze          Raw CSV -> Parquet (no logic)
    2  eda_preliminary  Data profiling + join overlap audit
    3  silver          Clean + merge + NLP classification
    4  gold            Business metric derivation
    5  eda_gold        Post-pipeline analytics reporting

Use --from to skip completed steps, e.g.:
    python run_pipeline.py --from silver
"""
import argparse
import sys
import time
from pathlib import Path


# Make scripts importable
PROJECT_ROOT = Path(__file__).parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))


STEP_ORDER = ["download", "bronze", "eda_preliminary", "silver", "gold", "eda_gold","star_schema"]


def import_step(name: str):
    module_map = {
        "download":        ("00_download_data",    "run_download"),
        "bronze":          ("01_bronze",          "run_bronze"),
        "eda_preliminary": ("02_eda_preliminary",  "run_eda"),
        "silver":          ("03_silver",           "run_silver"),
        "gold":            ("04_gold",             "run_gold"),
        "eda_gold":        ("05_eda_gold",         "run_eda_gold"),
        "star_schema":    ("06_star_schema",     "run_star_schema"),

    }
    mod_name, fn_name = module_map[name]
    import importlib
    mod = importlib.import_module(mod_name)
    return getattr(mod, fn_name)


def run(from_step: str = "bronze") -> None:
    if from_step not in STEP_ORDER:
        print(f"Unknown step '{from_step}'. Valid: {STEP_ORDER}")
        sys.exit(1)

    start_idx = STEP_ORDER.index(from_step)
    steps = STEP_ORDER[start_idx:]

    print(f"Running prototype pipeline: {' -> '.join(steps)}\n{'='*60}")
    total_start = time.time()

    for step in steps:
        print(f"\n[{step.upper()}]")
        t0 = time.time()
        fn = import_step(step)
        fn()
        print(f"  Done in {time.time() - t0:.1f}s")

    print(f"\n{'='*60}")
    print(f"Pipeline complete in {time.time() - total_start:.1f}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prototype Medallion pipeline")
    parser.add_argument(
        "--from", dest="from_step", default="download",
        choices=STEP_ORDER,
        help="Start pipeline from this step (default:download)"
    )
    args = parser.parse_args()
    run(args.from_step)

