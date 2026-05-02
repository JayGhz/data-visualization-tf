"""
05_eda_gold.py
Post-Gold analytics EDA. Reads from Gold only.
Visualizes the business-ready data to validate and communicate findings.

Covers:
  - Problem category distribution (CATEGORIA_PROBLEMA from NLP)
  - BRECHA distribution by LIFECYCLE and SECTOR
  - Staleness analysis (DIAS_SIN_REPORTE)
  - Execution vs Physical scatter (sample)
"""
import polars as pl
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
from config import GOLD_MASTER, PROJECT_ROOT

REPORT_DIR = PROJECT_ROOT / "reports" / "eda_gold"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="darkgrid", font_scale=1.05)


def save(fig: plt.Figure, name: str) -> None:
    path = REPORT_DIR / f"{name}.png"
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {path.name}")


# ---------------------------------------------------------------------------
# 1. Problem category distribution
# ---------------------------------------------------------------------------

def plot_problem_categories(df: pl.DataFrame) -> None:
    if "CATEGORIA_PROBLEMA" not in df.columns:
        print("  [skip] CATEGORIA_PROBLEMA not found — run Silver first.")
        return

    print("\n[1] Problem category distribution...")
    vc = (
        df.filter(pl.col("CATEGORIA_PROBLEMA").is_not_null())
        .group_by("CATEGORIA_PROBLEMA")
        .agg(pl.len().alias("count"))
        .sort("count", descending=True)
    )

    total_with_problem = vc["count"].sum()
    vc = vc.with_columns(
        (pl.col("count") / total_with_problem * 100).alias("pct")
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = sns.color_palette("rocket", len(vc))
    bars = ax.bar(vc["CATEGORIA_PROBLEMA"].to_list(), vc["count"].to_list(), color=colors)

    for bar, pct in zip(bars, vc["pct"].to_list()):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 200,
            f"{bar.get_height():,.0f}\n({pct:.1f}%)",
            ha="center", va="bottom", fontsize=9
        )

    ax.set_title(
        f"Investment Bottleneck Distribution — Semantic NLP Classification\n"
        f"({total_with_problem:,} projects with registered problems)",
        fontsize=12
    )
    ax.set_ylabel("Project Count")
    ax.set_xlabel("Problem Category")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    save(fig, "01_problem_categories")


# ---------------------------------------------------------------------------
# 2. BRECHA distribution by LIFECYCLE
# ---------------------------------------------------------------------------

def plot_brecha(df: pl.DataFrame) -> None:
    if "BRECHA" not in df.columns:
        print("  [skip] BRECHA not found.")
        return

    print("\n[2] BRECHA distribution by LIFECYCLE...")
    sub = df.filter(
        pl.col("BRECHA").is_not_null() &
        pl.col("BRECHA").is_between(-100, 100)
    )

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    # Distribution by lifecycle
    for lifecycle, color in [("ACTIVE", "#3498db"), ("CLOSED", "#27ae60")]:
        vals = sub.filter(pl.col("LIFECYCLE") == lifecycle)["BRECHA"].to_numpy()
        axes[0].hist(vals, bins=60, alpha=0.6, color=color, label=lifecycle, edgecolor="none")

    axes[0].axvline(0, color="red", ls="--", lw=1.5, label="No brecha")
    axes[0].set_title("BRECHA Distribution (Execution - Physical Progress) by Lifecycle")
    axes[0].set_xlabel("BRECHA (%)")
    axes[0].set_ylabel("Projects")
    axes[0].legend()

    # Median BRECHA per top sectors
    top_sectors = (
        sub.group_by("SECTOR")
        .agg(pl.col("BRECHA").median().alias("median_brecha"), pl.len().alias("n"))
        .sort("n", descending=True)
        .head(10)
    )

    colors_sectors = ["#e74c3c" if v > 0 else "#2980b9" for v in top_sectors["median_brecha"].to_list()]
    axes[1].barh(top_sectors["SECTOR"].to_list(), top_sectors["median_brecha"].to_list(), color=colors_sectors)
    axes[1].axvline(0, color="gray", ls="--", lw=1)
    axes[1].invert_yaxis()
    axes[1].set_title("Median BRECHA by Sector (Top 10 by volume)")
    axes[1].set_xlabel("Median BRECHA (%)")

    plt.suptitle("Execution vs Physical Progress Gap (BRECHA)", fontsize=13)
    plt.tight_layout()
    save(fig, "02_brecha_analysis")


# ---------------------------------------------------------------------------
# 3. Staleness — DIAS_SIN_REPORTE
# ---------------------------------------------------------------------------

def plot_staleness(df: pl.DataFrame) -> None:
    if "DIAS_SIN_REPORTE" not in df.columns:
        print("  [skip] DIAS_SIN_REPORTE not found.")
        return

    print("\n[3] Report staleness (DIAS_SIN_REPORTE)...")
    sub = df.filter(
        pl.col("DIAS_SIN_REPORTE").is_not_null() &
        (pl.col("LIFECYCLE") == "ACTIVE") &
        (pl.col("DIAS_SIN_REPORTE") >= 0)
    )

    fig, ax = plt.subplots(figsize=(12, 5))
    vals = np.clip(sub["DIAS_SIN_REPORTE"].to_numpy(), 0, 1000)
    ax.hist(vals, bins=80, color="#e67e22", alpha=0.85, edgecolor="none")
    ax.axvline(30,  color="orange", ls="--", label="30 days")
    ax.axvline(90,  color="red",    ls="--", label="90 days (at-risk)")
    ax.axvline(180, color="darkred",ls="--", label="180 days (paralyzed)")
    ax.set_title("Days Since Last Progress Report — Active Projects", fontsize=12)
    ax.set_xlabel("Days Without Update (capped at 1000)")
    ax.set_ylabel("Project Count")
    ax.legend()
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    stale_30  = int((sub["DIAS_SIN_REPORTE"] > 30).sum())
    stale_90  = int((sub["DIAS_SIN_REPORTE"] > 90).sum())
    stale_180 = int((sub["DIAS_SIN_REPORTE"] > 180).sum())
    total = len(sub)
    print(f"    >30 days without report : {stale_30:,}  ({stale_30/total*100:.1f}%)")
    print(f"    >90 days without report : {stale_90:,}  ({stale_90/total*100:.1f}%)")
    print(f"    >180 days without report: {stale_180:,} ({stale_180/total*100:.1f}%)")

    plt.tight_layout()
    save(fig, "03_staleness")


# ---------------------------------------------------------------------------
# 4. Execution vs Physical scatter (sampled)
# ---------------------------------------------------------------------------

def plot_execution_vs_physical(df: pl.DataFrame) -> None:
    if "AVANCE_FISICO" not in df.columns or "AVANCE_EJECUCION" not in df.columns:
        print("  [skip] AVANCE columns not found.")
        return

    print("\n[4] Execution vs Physical scatter...")
    sub = (
        df.filter(
            pl.col("AVANCE_FISICO").is_not_null() &
            pl.col("AVANCE_EJECUCION").is_not_null()
        )
        .sample(n=min(15_000, len(df)), seed=42)
    )

    phys = sub["AVANCE_FISICO"].to_numpy()
    exec_ = sub["AVANCE_EJECUCION"].to_numpy()

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(phys, exec_, alpha=0.08, s=4, color="#2980b9")
    ax.plot([0, 100], [0, 100], color="red", ls="--", lw=1.5, label="Perfect alignment")
    ax.set_xlabel("Avance Fisico (%)")
    ax.set_ylabel("Avance Ejecucion (%)")
    ax.set_title("Physical vs Financial Execution Progress\n(15k sample — above diagonal = finance ahead)")
    ax.legend()
    plt.tight_layout()
    save(fig, "04_execution_vs_physical")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_eda_gold() -> None:
    print("Gold EDA — post-pipeline analytics reporting\n")
    df = pl.read_parquet(GOLD_MASTER)
    print(f"  Gold table: {len(df):,} rows x {df.width} cols\n")

    plot_problem_categories(df)
    plot_brecha(df)
    plot_staleness(df)
    plot_execution_vs_physical(df)

    print("\nGold EDA complete — outputs in reports/eda_gold/")


if __name__ == "__main__":
    run_eda_gold()
