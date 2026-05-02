"""
02_eda_preliminary.py
Profiling of Bronze-layer data. Runs AFTER 01_bronze.py, BEFORE 03_silver.py.

Covers:
  - Missing value rates per dataset (all columns)
  - Join overlap audit (CUI cardinality and Venn intersections)
  - Numeric distribution outlier profiles
  - Temporal distribution of investment activity
  - F12B status and ULT_PROBLEMA text length profile

Output: reports/eda/*.png + reports/eda/cleaning_rules.md
"""
import polars as pl
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np  
from config import (
    DETALLE_BRONZE, F12B_BRONZE, CIERRE_BRONZE,
    PROJECT_ROOT,
)

EDA_DIR = PROJECT_ROOT / "reports" / "eda"
EDA_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="darkgrid", font_scale=1.05)

DETALLE_NUMERIC = [
    "DEV_ANIO_ACTUAL", "AVANCE_FISICO", "PIM_ANIO_ACTUAL",
    "DEVEN_ACUMUL_ANIO_ANT", "COSTO_ACTUALIZADO", "MONTO_VIABLE",
    "AVANCE_EJECUCION", "NUM_HABITANTES_BENEF",
]
DETALLE_CAT = [
    "SECTOR", "DEPARTAMENTO", "TIPO_INVERSION", "DES_MODALIDAD",
    "ESTADO", "SITUACION", "MARCO",
]
DETALLE_DATES = [
    "FECHA_REGISTRO", "FECHA_VIABILIDAD",
    "FEC_INI_EJECUCION", "FEC_FIN_EJECUCION",
]
F12B_NUMERIC = [
    "AVANCE_FISICO", "DEVENGADO_ACUMULADO", "AVANCE_EJECUCION",
]
F12B_CAT = ["ULT_ESTADO_SITUACIONAL"]
YYYYMM_COLS = ["PRIMER_DEVENGADO", "ULTIMO_DEVENGADO"]

CLEANING_RULES: list[dict] = []

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def iqr_bounds(s: pl.Series) -> tuple[float, float]:
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def save(fig: plt.Figure, name: str) -> None:
    path = EDA_DIR / f"{name}.png"
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {path.name}")


def note(dataset: str, variable: str, issue: str, strategy: str) -> None:
    CLEANING_RULES.append({
        "Dataset": dataset,
        "Variable": variable,
        "Issue": issue,
        "Strategy": strategy
    })


def load_cast(path, numeric_cols: list[str]) -> pl.DataFrame:
    lf = pl.scan_parquet(path)
    existing = [c for c in numeric_cols if c in lf.collect_schema().names()]
    return lf.with_columns([
        pl.col(c).cast(pl.Float64, strict=False) for c in existing
    ]).collect()


def clean_cui(df: pl.DataFrame) -> set:
    return set(df["CODIGO_UNICO"].str.replace_all('"', "").str.strip_chars().unique())


# ---------------------------------------------------------------------------
# 1. Missing value profiles — all three datasets
# ---------------------------------------------------------------------------

def plot_missing(dfs: dict[str, pl.DataFrame]) -> None:
    print("\n[1] Missing value profiles...")
    fig, axes = plt.subplots(1, len(dfs), figsize=(8 * len(dfs), 10))

    for ax, (name, df) in zip(axes, dfs.items()):
        stats = []
        for col in df.columns:
            s = df[col]
            if s.dtype == pl.String:
                missing = s.is_null().sum() + (s.str.strip_chars() == "").sum()
            else:
                missing = s.is_null().sum()
            stats.append((col, (missing / len(s)) * 100))

        stats = sorted(stats, key=lambda x: -x[1])[:25]
        cols, vals = zip(*stats)

        colors = ["#e74c3c" if v > 50 else "#e67e22" if v > 20 else "#3498db" for v in vals]
        ax.barh(cols, vals, color=colors)
        ax.axvline(20, color="orange", ls="--", alpha=0.6, label="20%")
        ax.axvline(50, color="red",    ls="--", alpha=0.6, label="50%")
        ax.invert_yaxis()
        ax.set_title(f"Missing rates — {name}\n({len(df):,} rows)", fontsize=10)
        ax.set_xlabel("Missing (%)")
        ax.legend(fontsize=8)

        for i, (c, v) in enumerate(zip(cols, vals)):
            ax.text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=7)
            if v == 0:
                note(name, c, "0% missing", "No action")
            elif v < 20:
                note(name, c, f"{v:.1f}% missing", "Retain null")
            elif v < 50:
                note(name, c, f"{v:.1f}% missing", "Flag column, no imputation")
            else:
                note(name, c, f"{v:.1f}% missing", "Structurally sparse, Flag only")

    plt.suptitle("Missing Value Rates — Bronze Layer (All Datasets)", fontsize=13)
    plt.tight_layout()
    save(fig, "01_missing_all_datasets")


# ---------------------------------------------------------------------------
# 2. Join overlap audit — CUI cardinality
# ---------------------------------------------------------------------------

def audit_join_overlap(dfs: dict[str, pl.DataFrame]) -> None:
    print("\n[2] Join overlap audit (CODIGO_UNICO)...")
    det  = clean_cui(dfs["Detalle"])
    f12b = clean_cui(dfs["F12B"])
    cie  = clean_cui(dfs["Cierre"])

    pairs = {
        "Detalle / F12B":  det & f12b,
        "Detalle / Cierre":det & cie,
        "F12B / Cierre":   f12b & cie,
        "All three":       det & f12b & cie,
    }

    print(f"  Detalle unique CUIs  : {len(det):>7,}")
    print(f"  F12B unique CUIs     : {len(f12b):>7,}")
    print(f"  Cierre unique CUIs   : {len(cie):>7,}")
    print(f"  Union (all)          : {len(det | f12b | cie):>7,}")
    for label, s in pairs.items():
        pct = len(s) / len(det) * 100
        print(f"  {label:<22} : {len(s):>7,}  ({pct:.1f}% of Detalle)")

    if len(det & cie) < 10:
        note("Join Audit", "Detalle/Cierre", "Shared projects < 10", "Use F12B as bridge")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(list(pairs.keys()), [len(v) for v in pairs.values()], color="#3498db", alpha=0.85)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_title("CUI Overlap Between Datasets")
    ax.set_ylabel("Shared Projects")
    plt.xticks(rotation=15, ha="right")
    save(fig, "02_cui_overlap")


# ---------------------------------------------------------------------------
# 3. Numeric outlier profiles
# ---------------------------------------------------------------------------

def plot_numeric_outliers(df: pl.DataFrame, cols: list[str], prefix: str, name: str) -> None:
    print(f"\n[3] Numeric outlier profiles — {name}...")
    cols_in = [c for c in cols if c in df.columns]
    if not cols_in:
        return

    n = len(cols_in)
    fig, axes = plt.subplots(n, 2, figsize=(16, 4 * n))
    if n == 1:
        axes = [axes]

    for i, col in enumerate(cols_in):
        s = df[col].drop_nulls()
        if s.len() == 0:
            continue

        lo, hi = iqr_bounds(s)
        n_out   = int(((s < lo) | (s > hi)).sum())
        pct_out = n_out / s.len() * 100

        # Create a single clear plot for each numeric variable
        fig, (ax_box, ax_hist) = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={"height_ratios": (.15, .85)}, sharex=True)
        
        # Horizontal Boxplot to show outliers clearly
        sns.boxplot(x=s.to_numpy(), ax=ax_box, color="#3498db", fliersize=4, linewidth=1.5)
        ax_box.set(xlabel='')
        ax_box.set_title(f"Outlier Analysis: {col} (N={len(s):,})", fontsize=12, fontweight='bold')
        
        # Histogram with KDE
        sns.histplot(x=s.to_numpy(), ax=ax_hist, kde=True, color="#2980b9", alpha=0.4)
        ax_hist.axvline(lo, color="#e74c3c", ls="--", lw=2, alpha=0.7, label=f"Lower Bound ({lo:,.0f})")
        ax_hist.axvline(hi, color="#e74c3c", ls="--", lw=2, alpha=0.7, label=f"Upper Bound ({hi:,.0f})")
        
        # Formatting
        ax_hist.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax_hist.set_ylabel("Frequency")
        ax_hist.legend(loc='upper right', frameon=True)

        neg = int((s < 0).sum())
        if col in ("AVANCE_FISICO", "AVANCE_EJECUCION"):
            absurd = int((s > 100).sum())
            note(name, col, f"{pct_out:.1f}% outliers, {absurd} values >100", "Cap at 100.0")
        elif col in ("COSTO_ACTUALIZADO", "MONTO_VIABLE", "DEVENGADO_ACUMULADO", "DEVEN_ACUMUL_ANIO_ANT"):
            note(name, col, f"{pct_out:.1f}% outliers", "Keep as is (high-value projects)")
        else:
            note(name, col, f"{pct_out:.1f}% outliers, {neg} negatives", "Keep by default")

    fig.suptitle(f"Numeric Outlier Analysis: {name}", fontsize=13)
    plt.tight_layout()
    save(fig, f"{prefix}_numeric_outliers")


# ---------------------------------------------------------------------------
# 4. Temporal activity
# ---------------------------------------------------------------------------

def plot_temporal(df: pl.DataFrame) -> None:
    print("\n[4] Temporal analysis...")
    lf = df.lazy().with_columns([
        pl.col("FECHA_REGISTRO").str.to_datetime(format="%Y-%m-%d %H:%M:%S", strict=False),
        pl.col("FEC_INI_EJECUCION").str.to_datetime(format="%Y-%m-%d %H:%M:%S", strict=False),
        pl.when(pl.col("PRIMER_DEVENGADO").str.len_chars() == 6)
          .then(pl.col("PRIMER_DEVENGADO").str.slice(0, 4).cast(pl.Int32, strict=False))
          .otherwise(pl.lit(None))
          .alias("primer_dev_year"),
    ])

    reg    = lf.filter(pl.col("FECHA_REGISTRO").is_not_null()).with_columns(pl.col("FECHA_REGISTRO").dt.year().alias("y")).group_by("y").agg(pl.len().alias("cnt")).sort("y").collect()
    ex_yr  = lf.filter(pl.col("FEC_INI_EJECUCION").is_not_null()).with_columns(pl.col("FEC_INI_EJECUCION").dt.year().alias("y")).group_by("y").agg(pl.len().alias("cnt")).sort("y").collect()
    dev_yr = lf.filter(pl.col("primer_dev_year").is_not_null()).group_by("primer_dev_year").agg(pl.len().alias("cnt")).sort("primer_dev_year").collect()

    fig, axes = plt.subplots(1, 3, figsize=(21, 5))
    for ax, (xs, ys, color, title) in zip(axes, [
        (reg["y"],                  reg["cnt"],    "#2980b9", "Registrations (fecha_registro)"),
        (ex_yr["y"],                ex_yr["cnt"],  "#27ae60", "Execution Starts (fec_ini_ejecucion)"),
        (dev_yr["primer_dev_year"], dev_yr["cnt"], "#8e44ad", "First Expenditure (primer_devengado)"),
    ]):
        ax.bar(xs.to_list(), ys.to_list(), color=color, alpha=0.85)
        ax.set_title(title)
        ax.set_xlabel("Year")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    plt.suptitle("Temporal Distribution of Investment Activity", fontsize=13)
    plt.tight_layout()
    save(fig, "03_temporal_activity")
    
    # Date Outlier Check (Comprehensive across columns)
    from datetime import datetime
    this_year = datetime.now().year
    
    # Collect columns to check
    df_check = lf.select([
        c for c in ["FECHA_REGISTRO", "FECHA_VIABILIDAD", "FEC_INI_EJECUCION", "FEC_FIN_EJECUCION"]
        if c in lf.collect_schema().names()
    ]).collect()

    for c in df_check.columns:
        s = df_check[c]
        if s.dtype == pl.String:
            s = s.str.to_datetime(strict=False)
        
        future = (s.dt.year() > this_year + 5).sum()
        if future > 0:
            note("Detalle", c, f"{future} extreme future dates (e.g. 2039)", "Nullify in Silver")

    # Logical consistency: Start >= End
    if "FEC_INI_EJECUCION" in df_check.columns and "FEC_FIN_EJECUCION" in df_check.columns:
        ini = df_check["FEC_INI_EJECUCION"]
        fin = df_check["FEC_FIN_EJECUCION"]
        if ini.dtype == pl.String: ini = ini.str.to_datetime(strict=False)
        if fin.dtype == pl.String: fin = fin.str.to_datetime(strict=False)
        
        bad_logic = ((ini >= fin) & ini.is_not_null() & fin.is_not_null()).sum()
        if bad_logic > 0:
            note("Detalle", "Dates", f"{bad_logic} projects with Start >= End", "Flag as INCONSISTENTE in Gold")
    
    note("Temporal", "Dates", "Multiple formats/YYYYMM", "Parse to datetime/Extract year")


# ---------------------------------------------------------------------------
# 5. F12B — status profile + ULT_PROBLEMA text length
# ---------------------------------------------------------------------------

def plot_f12b_profile(df_f12b: pl.DataFrame, df_det: pl.DataFrame) -> None:
    print("\n[5] F12B text and status profile...")
    fig, axes = plt.subplots(1, 2, figsize=(22, 6))

    # Consistency Crosstab: TIENE_AVAN_FISICO vs TIENE_F12B (from Detalle)
    if "TIENE_AVAN_FISICO" in df_det.columns and "TIENE_F12B" in df_det.columns:
        cross = df_det.group_by(["TIENE_AVAN_FISICO", "TIENE_F12B"]).agg(pl.len().alias("cnt")).pivot(on="TIENE_F12B", index="TIENE_AVAN_FISICO", values="cnt")
        # Plotting as a small heatmap or table in axes[1]
        sns.heatmap(cross.to_pandas().set_index("TIENE_AVAN_FISICO"), annot=True, fmt=",.0f", cmap="Blues", cbar=False, ax=axes[0])
        axes[0].set_title("Consistency: TIENE_AVAN_FISICO vs TIENE_F12B")

    # Bar charts instead of pie charts (Using Percentages)
    if "SITUACION" in df_det.columns:
        sit_counts = df_det["SITUACION"].value_counts().sort("count", descending=True).head(10)
        sit_counts = sit_counts.with_columns((pl.col("count") / len(df_det) * 100).alias("pct"))
        
        axes[1].barh(sit_counts["SITUACION"].to_list(), sit_counts["pct"].to_list(), color=sns.color_palette("viridis", len(sit_counts)))
        axes[1].invert_yaxis()
        axes[1].set_title("Situación (Detalle) - % of Total")
        axes[1].set_xlabel("Percentage (%)")
        for i, v in enumerate(sit_counts["pct"]):
            axes[1].text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=9)

    plt.suptitle("F12B Profile & Data Consistency", fontsize=13)
    plt.tight_layout()
    save(fig, "04_f12b_consistency")


# ---------------------------------------------------------------------------
# 6. Write cleaning rules
# ---------------------------------------------------------------------------

def generate_profile_md(dfs: dict[str, pl.DataFrame]) -> None:
    path = PROJECT_ROOT / "reports" / "profile.md"
    print(f"\nGenerating {path.name}...")
    
    with open(path, "w", encoding="utf-8") as f:
        f.write("# 📊 Data Profile & Pipeline Decisions\n\n")
        f.write("## 1. Dataset Overview\n")
        for name, df in dfs.items():
            f.write(f"- **{name}**: {df.height:,} rows, {df.width} columns\n")
        
        f.write("\n## 2. Join Overlap Audit (CODIGO_UNICO)\n")
        det = set(dfs["Detalle"]["CODIGO_UNICO"].unique())
        f12b = set(dfs["F12B"]["CODIGO_UNICO"].unique())
        cie = set(dfs["Cierre"]["CODIGO_UNICO"].unique())
        
        f.write("| Connection | Unique Projects | % of Detalle |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write(f"| **Detalle Total** | {len(det):,} | 100% |\n")
        f.write(f"| **F12B Total** | {len(f12b):,} | {len(f12b)/len(det)*100:.1f}% |\n")
        f.write(f"| **Cierre Total** | {len(cie):,} | {len(cie)/len(det)*100:.1f}% |\n")
        f.write(f"| Bridge F12B-Detalle | {len(det & f12b):,} | {len(det & f12b)/len(det)*100:.1f}% |\n")
        f.write(f"| Bridge F12B-Cierre | {len(f12b & cie):,} | {len(f12b & cie)/len(det)*100:.1f}% |\n")
        f.write(f"| Direct Detalle-Cierre | {len(det & cie):,} | {len(det & cie)/len(det)*100:.1f}% |\n")

        f.write("\n## 3. Data Cleaning & Imputation Plan\n")
        f.write("| Dataset | Variable | Finding / Issue | Strategy |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for rule in CLEANING_RULES:
            f.write(f"| {rule['Dataset']} | `{rule['Variable']}` | {rule['Issue']} | {rule['Strategy']} |\n")
            
        f.write("\n## 4. Key Indicators Distribution\n")
        if "SITUACION" in dfs["Detalle"].columns:
            f.write("\n### Situación (Top 5)\n")
            vc = dfs["Detalle"]["SITUACION"].value_counts().sort("count", descending=True).head(5)
            f.write("| Situación | Count | % |\n| :--- | :--- | :--- |\n")
            for row in vc.to_dicts():
                pct = row['count'] / len(dfs["Detalle"]) * 100
                f.write(f"| {row['SITUACION']} | {row['count']:,} | {pct:.1f}% |\n")

        if "TIPO_INVERSION" in dfs["Detalle"].columns and "TIENE_AVAN_FISICO" in dfs["Detalle"].columns:
            f.write("\n### TIPO_INVERSION vs TIENE_AVAN_FISICO\n")
            f.write("| TIPO_INVERSION | TIENE_AVAN_FISICO | Count | % of Total |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            
            cross = (
                dfs["Detalle"]
                .group_by(["TIPO_INVERSION", "TIENE_AVAN_FISICO"])
                .agg(pl.len().alias("count"))
                .sort(["TIPO_INVERSION", "TIENE_AVAN_FISICO"])
            )
            
            total = len(dfs["Detalle"])
            for row in cross.to_dicts():
                pct = row['count'] / total * 100
                f.write(f"| {row['TIPO_INVERSION']} | {row['TIENE_AVAN_FISICO']} | {row['count']:,} | {pct:.1f}% |\n")

    print(f"✅ Profile report saved to {path}")

def run_eda() -> None:
    print("Preliminary Data Profiling — Bronze layer\n")

    df_det  = load_cast(DETALLE_BRONZE, DETALLE_NUMERIC)
    df_f12b = load_cast(F12B_BRONZE,    F12B_NUMERIC)
    df_cie  = pl.read_parquet(CIERRE_BRONZE)

    print(f"  Detalle : {df_det.height:,} rows x {df_det.width} cols")
    print(f"  F12B    : {df_f12b.height:,} rows x {df_f12b.width} cols")
    print(f"  Cierre  : {df_cie.height:,} rows x {df_cie.width} cols")

    dfs = {"Detalle": df_det, "F12B": df_f12b, "Cierre": df_cie}

    plot_missing(dfs)
    audit_join_overlap(dfs)
    plot_temporal(df_det)
    plot_f12b_profile(df_f12b, df_det)
    generate_profile_md(dfs)

    print("\nPreliminary EDA complete — outputs in reports/eda/")


if __name__ == "__main__":
    run_eda()
