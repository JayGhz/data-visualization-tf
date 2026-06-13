"""
02_eda_preliminary.py
Perfilado de datos de la capa Bronze. Ejecutar DESPUÉS de 01_bronze.py, ANTES de 03_silver.py.

Cubre:
  - Tasas de valores faltantes por dataset
  - Auditoría de solapamiento por CUI
  - Perfiles de valores atípicos numéricos
  - Distribución temporal de la actividad de inversión
  - Perfil de estado F12B y consistencia

Salida: reports/eda/*.png + docs/Profiling.md
"""
import polars as pl
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import (
    DETALLE_BRONZE, F12B_BRONZE, CIERRE_BRONZE,
    PROJECT_ROOT,
)

EDA_DIR = PROJECT_ROOT / "reports" / "eda"
EDA_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Paleta elegante (fondo blanco) ----------
C = {
    "navy":    "#1A3A5C",
    "blue":    "#2E86AB",
    "teal":    "#3AAFA9",
    "green":   "#2D936C",
    "amber":   "#D4A017",
    "red":     "#C0392B",
    "coral":   "#E05A4E",
    "purple":  "#6C5B7B",
    "gray":    "#7F8C8D",
    "light":   "#ECF0F1",
    "text":    "#2C3E50",
    "grid":    "#E8E8E8",
    "bg":      "#FFFFFF",
    "surface": "#F9FAFB",
}

SEQ_COLORS = [
    "#1A3A5C", "#2E86AB", "#3AAFA9", "#2D936C",
    "#8BC34A", "#D4A017", "#E05A4E", "#C0392B",
    "#6C5B7B", "#95A5A6",
]

LAYOUT_BASE = dict(
    paper_bgcolor=C["bg"],
    plot_bgcolor=C["surface"],
    font=dict(color=C["text"], size=12),
    title_font=dict(size=14, color=C["navy"]),
    margin=dict(l=70, r=50, t=80, b=60),
)

DETALLE_NUMERIC = [
    "DEV_ANIO_ACTUAL", "AVANCE_FISICO", "PIM_ANIO_ACTUAL",
    "DEVEN_ACUMUL_ANIO_ANT", "COSTO_ACTUALIZADO", "MONTO_VIABLE",
    "AVANCE_EJECUCION", "NUM_HABITANTES_BENEF",
]
F12B_NUMERIC = [
    "AVANCE_FISICO", "DEVENGADO_ACUMULADO", "AVANCE_EJECUCION",
]

CLEANING_RULES: list[dict] = []


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def iqr_bounds(s: pl.Series) -> tuple[float, float]:
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def save(fig: go.Figure, name: str, width: int = 1400, height: int = 750) -> None:
    path = EDA_DIR / f"{name}.png"
    fig.write_image(str(path), width=width, height=height, scale=2)
    print(f"  -> {path.name}")


def note(dataset: str, variable: str, issue: str, strategy: str) -> None:
    CLEANING_RULES.append({
        "Dataset": dataset,
        "Variable": variable,
        "Issue": issue,
        "Strategy": strategy,
    })


def load_cast(path, numeric_cols: list[str]) -> pl.DataFrame:
    lf = pl.scan_parquet(path)
    existing = [c for c in numeric_cols if c in lf.collect_schema().names()]
    return lf.with_columns([
        pl.col(c).cast(pl.Float64, strict=False) for c in existing
    ]).collect()


def clean_cui(df: pl.DataFrame) -> set:
    return set(df["CODIGO_UNICO"].str.replace_all('"', "").str.strip_chars().unique())


def _base(fig: go.Figure, title: str, **kw) -> go.Figure:
    fig.update_layout(**LAYOUT_BASE, title=dict(text=title, x=0.5), **kw)
    fig.update_xaxes(showgrid=True, gridcolor=C["grid"], zeroline=False,
                     linecolor=C["grid"], linewidth=1)
    fig.update_yaxes(showgrid=True, gridcolor=C["grid"], zeroline=False,
                     linecolor=C["grid"], linewidth=1)
    return fig


# ---------------------------------------------------------------------------
# 1. Perfiles de valores faltantes
# ---------------------------------------------------------------------------

def plot_missing(dfs: dict[str, pl.DataFrame]) -> None:
    print("\n[1] Perfiles de valores faltantes...")

    names = list(dfs.keys())
    fig = make_subplots(
        rows=1, cols=len(names),
        subplot_titles=[f"{nm}  ({len(dfs[nm]):,} filas)" for nm in names],
        horizontal_spacing=0.08,
    )

    for col_idx, (name, df) in enumerate(dfs.items(), start=1):
        stats = []
        for c in df.columns:
            s = df[c]
            missing = (
                s.is_null().sum() + (s.str.strip_chars() == "").sum()
                if s.dtype == pl.String else s.is_null().sum()
            )
            stats.append((c, (missing / len(s)) * 100))

        stats = sorted(stats, key=lambda x: -x[1])[:25]
        cols_n, vals = zip(*stats)

        bar_colors = [
            C["red"] if v > 50 else C["amber"] if v > 20 else C["blue"]
            for v in vals
        ]

        fig.add_trace(
            go.Bar(
                x=list(vals), y=list(cols_n),
                orientation="h",
                marker_color=bar_colors,
                text=[f"{v:.1f}%" for v in vals],
                textposition="outside",
                textfont=dict(size=8, color=C["text"]),
                showlegend=False,
            ),
            row=1, col=col_idx,
        )
        for x_val, color in [(20, C["amber"]), (50, C["red"])]:
            fig.add_vline(x=x_val, line_dash="dot", line_color=color,
                          opacity=0.6, row=1, col=col_idx)

        for c, v in zip(cols_n, vals):
            if v == 0:
                note(name, c, "0% faltante", "Sin acción")
            elif v < 20:
                note(name, c, f"{v:.1f}% faltante", "Conservar nulo")
            elif v < 50:
                note(name, c, f"{v:.1f}% faltante", "Marcar columna, sin imputación")
            else:
                note(name, c, f"{v:.1f}% faltante", "Estructuralmente disperso, solo marcar")

    fig.update_yaxes(autorange="reversed")
    _base(fig, "Tasas de Valores Faltantes — Capa Bronze (Todos los Datasets)")
    save(fig, "01_missing_all_datasets", width=1800, height=750)


# ---------------------------------------------------------------------------
# 2. Auditoría de solapamiento CUI
# ---------------------------------------------------------------------------

def audit_join_overlap(dfs: dict[str, pl.DataFrame]) -> None:
    print("\n[2] Auditoría de solapamiento CUI...")
    det  = clean_cui(dfs["Detalle"])
    f12b = clean_cui(dfs["F12B"])
    cie  = clean_cui(dfs["Cierre"])

    pairs = {
        "Detalle / F12B":   det & f12b,
        "Detalle / Cierre": det & cie,
        "F12B / Cierre":    f12b & cie,
        "Los tres":         det & f12b & cie,
    }

    for label, s in pairs.items():
        pct = len(s) / len(det) * 100
        print(f"  {label:<22} : {len(s):>7,}  ({pct:.1f}% de Detalle)")

    if len(det & cie) < 10:
        note("Auditoría Join", "Detalle/Cierre",
             "Proyectos compartidos < 10", "Usar F12B como puente")

    labels = list(pairs.keys())
    values = [len(v) for v in pairs.values()]

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=[C["navy"], C["blue"], C["teal"], C["green"]],
        text=[f"{v:,}" for v in values],
        textposition="outside",
        textfont=dict(size=12, color=C["text"]),
    ))
    _base(fig, "Solapamiento de CUI entre Datasets")
    fig.update_layout(yaxis_title="Proyectos Compartidos", xaxis_title="")
    save(fig, "02_cui_overlap", width=1000, height=580)


# ---------------------------------------------------------------------------
# 3. Perfiles de valores atípicos numéricos
# ---------------------------------------------------------------------------

def plot_numeric_outliers(df: pl.DataFrame, cols: list[str], prefix: str, name: str) -> None:
    print(f"\n[3] Perfiles de valores atípicos — {name}...")
    cols_in = [c for c in cols if c in df.columns]
    if not cols_in:
        return

    n = len(cols_in)
    fig = make_subplots(
        rows=n, cols=2,
        column_widths=[0.25, 0.75],
        horizontal_spacing=0.06,
        vertical_spacing=0.06 if n <= 4 else 0.04,
        subplot_titles=[
            title
            for col in cols_in
            for title in (f"{col} — Diagrama de Caja", f"{col} — Distribución")
        ],
    )

    for i, col in enumerate(cols_in, start=1):
        s = df[col].drop_nulls()
        if s.len() == 0:
            continue

        lo, hi = iqr_bounds(s)
        n_out   = int(((s < lo) | (s > hi)).sum())
        pct_out = n_out / s.len() * 100
        arr     = s.to_numpy()

        # Diagrama de caja
        fig.add_trace(
            go.Box(
                x=arr, orientation="h",
                marker_color=C["blue"],
                line_color=C["navy"],
                fillcolor="rgba(46,134,171,0.20)",
                showlegend=False,
            ),
            row=i, col=1,
        )

        # Histograma
        fig.add_trace(
            go.Histogram(
                x=arr, nbinsx=60,
                marker_color=C["blue"],
                opacity=0.75,
                showlegend=False,
            ),
            row=i, col=2,
        )
        for x_val, lbl in [(lo, f"Límite inf. ({lo:,.0f})"),
                            (hi, f"Límite sup. ({hi:,.0f})")]:
            fig.add_vline(
                x=x_val, line_dash="dash", line_color=C["red"],
                opacity=0.7, row=i, col=2,
            )

        # Notas de limpieza
        neg = int((s < 0).sum())
        if col in ("AVANCE_FISICO", "AVANCE_EJECUCION"):
            absurd = int((s > 100).sum())
            note(name, col, f"{pct_out:.1f}% atípicos, {absurd} valores >100", "Limitar a 100")
        elif col in ("COSTO_ACTUALIZADO", "MONTO_VIABLE",
                     "DEVENGADO_ACUMULADO", "DEVEN_ACUMUL_ANIO_ANT"):
            note(name, col, f"{pct_out:.1f}% atípicos",
                 "Conservar (proyectos de alto valor)")
        else:
            note(name, col, f"{pct_out:.1f}% atípicos, {neg} negativos",
                 "Conservar por defecto")

    _base(
        fig,
        f"Análisis de Valores Atípicos — {name}",
        height=max(350 * n, 500),
    )
    save(fig, f"{prefix}_numeric_outliers", width=1400, height=max(380 * n, 550))


# ---------------------------------------------------------------------------
# 4. Actividad temporal
# ---------------------------------------------------------------------------

def plot_temporal(df: pl.DataFrame) -> None:
    print("\n[4] Análisis temporal...")
    lf = df.lazy().with_columns([
        pl.col("FECHA_REGISTRO").str.to_datetime(format="%Y-%m-%d %H:%M:%S", strict=False),
        pl.col("FEC_INI_EJECUCION").str.to_datetime(format="%Y-%m-%d %H:%M:%S", strict=False),
        pl.when(pl.col("PRIMER_DEVENGADO").str.len_chars() == 6)
          .then(pl.col("PRIMER_DEVENGADO").str.slice(0, 4).cast(pl.Int32, strict=False))
          .otherwise(pl.lit(None))
          .alias("primer_dev_year"),
    ])

    reg    = (lf.filter(pl.col("FECHA_REGISTRO").is_not_null())
              .with_columns(pl.col("FECHA_REGISTRO").dt.year().alias("y"))
              .group_by("y").agg(pl.len().alias("cnt")).sort("y").collect())
    ex_yr  = (lf.filter(pl.col("FEC_INI_EJECUCION").is_not_null())
              .with_columns(pl.col("FEC_INI_EJECUCION").dt.year().alias("y"))
              .group_by("y").agg(pl.len().alias("cnt")).sort("y").collect())
    dev_yr = (lf.filter(pl.col("primer_dev_year").is_not_null())
              .group_by("primer_dev_year").agg(pl.len().alias("cnt"))
              .sort("primer_dev_year").collect())

    series = [
        (reg["y"].to_list(),                  reg["cnt"].to_list(),   C["navy"],  "Registros (Fecha Registro)"),
        (ex_yr["y"].to_list(),                ex_yr["cnt"].to_list(), C["blue"],  "Inicio de Ejecución"),
        (dev_yr["primer_dev_year"].to_list(), dev_yr["cnt"].to_list(), C["teal"], "Primer Devengado"),
    ]

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=[s[3] for s in series],
        horizontal_spacing=0.08,
    )
    for col_idx, (xs, ys, color, _) in enumerate(series, start=1):
        fig.add_trace(
            go.Bar(x=xs, y=ys, marker_color=color, showlegend=False),
            row=1, col=col_idx,
        )
        fig.update_yaxes(tickformat=",", row=1, col=col_idx)

    _base(fig, "Distribución Temporal de la Actividad de Inversión")
    save(fig, "04_temporal_activity", width=1600, height=550)

    # Verificación de fechas atípicas
    from datetime import datetime
    this_year = datetime.now().year
    df_check = lf.select([
        c for c in ["FECHA_REGISTRO", "FECHA_VIABILIDAD",
                    "FEC_INI_EJECUCION", "FEC_FIN_EJECUCION"]
        if c in lf.collect_schema().names()
    ]).collect()

    for c in df_check.columns:
        s = df_check[c]
        if s.dtype == pl.String:
            s = s.str.to_datetime(strict=False)
        future = (s.dt.year() > this_year + 5).sum()
        if future > 0:
            note("Detalle", c, f"{future} fechas futuras extremas",
                 "Anular en Silver")

    if ("FEC_INI_EJECUCION" in df_check.columns
            and "FEC_FIN_EJECUCION" in df_check.columns):
        ini = df_check["FEC_INI_EJECUCION"]
        fin = df_check["FEC_FIN_EJECUCION"]
        if ini.dtype == pl.String:
            ini = ini.str.to_datetime(strict=False)
        if fin.dtype == pl.String:
            fin = fin.str.to_datetime(strict=False)
        bad = ((ini >= fin) & ini.is_not_null() & fin.is_not_null()).sum()
        if bad > 0:
            note("Detalle", "Fechas",
                 f"{bad} proyectos con Inicio >= Fin",
                 "Marcar como INCONSISTENTE en Gold")

    note("Temporal", "Fechas", "Múltiples formatos / YYYYMM",
         "Parsear a datetime / Extraer año")


# ---------------------------------------------------------------------------
# 5. Perfil F12B — consistencia
# ---------------------------------------------------------------------------

def plot_f12b_profile(df_f12b: pl.DataFrame, df_det: pl.DataFrame) -> None:
    print("\n[5] Perfil F12B y consistencia de datos...")

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            "Consistencia: TIENE_AVAN_FISICO vs TIENE_F12B",
            "Distribución por Situación (Detalle) — % del Total",
        ],
        horizontal_spacing=0.12,
    )

    # Mapa de calor — tabla cruzada de consistencia
    if "TIENE_AVAN_FISICO" in df_det.columns and "TIENE_F12B" in df_det.columns:
        cross = (
            df_det
            .group_by(["TIENE_AVAN_FISICO", "TIENE_F12B"])
            .agg(pl.len().alias("cnt"))
            .pivot(on="TIENE_F12B", index="TIENE_AVAN_FISICO", values="cnt")
        )
        pdf      = cross.to_pandas().set_index("TIENE_AVAN_FISICO")
        z        = pdf.values.tolist()
        x_labels = list(pdf.columns)
        y_labels = list(pdf.index)

        fig.add_trace(
            go.Heatmap(
                z=z, x=x_labels, y=y_labels,
                colorscale=[
                    [0.0, "#EBF5FB"],
                    [0.5, "#2E86AB"],
                    [1.0, "#1A3A5C"],
                ],
                text=[[f"{val:,.0f}" if val is not None else "–"
                       for val in row] for row in z],
                texttemplate="%{text}",
                textfont=dict(size=11),
                showscale=False,
            ),
            row=1, col=1,
        )

    # Barras horizontales — distribución por SITUACION
    if "SITUACION" in df_det.columns:
        sit = (
            df_det["SITUACION"].value_counts()
            .sort("count", descending=True)
            .head(10)
        )
        pcts  = (sit["count"] / len(df_det) * 100).to_list()
        names = sit["SITUACION"].to_list()

        fig.add_trace(
            go.Bar(
                x=pcts, y=names,
                orientation="h",
                marker_color=C["blue"],
                text=[f"{v:.1f}%" for v in pcts],
                textposition="outside",
                textfont=dict(size=9, color=C["text"]),
                showlegend=False,
            ),
            row=1, col=2,
        )
        fig.update_yaxes(autorange="reversed", row=1, col=2)
        fig.update_xaxes(title_text="Porcentaje (%)", row=1, col=2)

    _base(fig, "Perfil F12B y Consistencia de Datos")
    save(fig, "05_f12b_consistency", width=1400, height=620)


# ---------------------------------------------------------------------------
# 6. Reporte de limpieza (Markdown)
# ---------------------------------------------------------------------------

def generate_profile_md(dfs: dict[str, pl.DataFrame]) -> None:
    path = PROJECT_ROOT / "docs" / "Profiling.md"
    print(f"\nGenerando {path.name}...")

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Perfil de Datos y Decisiones de Pipeline\n\n")
        f.write("## 1. Resumen de Datasets\n")
        for name, df in dfs.items():
            f.write(f"- **{name}**: {df.height:,} filas, {df.width} columnas\n")

        f.write("\n## 2. Auditoría de Solapamiento CUI\n")
        det  = set(dfs["Detalle"]["CODIGO_UNICO"].unique())
        f12b = set(dfs["F12B"]["CODIGO_UNICO"].unique())
        cie  = set(dfs["Cierre"]["CODIGO_UNICO"].unique())

        f.write("| Conexión | Proyectos únicos | % de Detalle |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write(f"| **Total Detalle** | {len(det):,} | 100% |\n")
        f.write(f"| **Total F12B** | {len(f12b):,} | {len(f12b)/len(det)*100:.1f}% |\n")
        f.write(f"| **Total Cierre** | {len(cie):,} | {len(cie)/len(det)*100:.1f}% |\n")
        f.write(f"| Puente F12B-Detalle | {len(det & f12b):,} | {len(det & f12b)/len(det)*100:.1f}% |\n")
        f.write(f"| Puente F12B-Cierre | {len(f12b & cie):,} | {len(f12b & cie)/len(det)*100:.1f}% |\n")
        f.write(f"| Directo Detalle-Cierre | {len(det & cie):,} | {len(det & cie)/len(det)*100:.1f}% |\n")

        f.write("\n## 3. Plan de Limpieza e Imputación\n")
        f.write("| Dataset | Variable | Hallazgo / Problema | Estrategia |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for rule in CLEANING_RULES:
            f.write(f"| {rule['Dataset']} | `{rule['Variable']}` | {rule['Issue']} | {rule['Strategy']} |\n")

        f.write("\n## 4. Distribución de Indicadores Clave\n")
        if "SITUACION" in dfs["Detalle"].columns:
            f.write("\n### Situación (Top 5)\n")
            vc = dfs["Detalle"]["SITUACION"].value_counts().sort("count", descending=True).head(5)
            f.write("| Situación | Cantidad | % |\n| :--- | :--- | :--- |\n")
            for row in vc.to_dicts():
                pct = row["count"] / len(dfs["Detalle"]) * 100
                f.write(f"| {row['SITUACION']} | {row['count']:,} | {pct:.1f}% |\n")

        if "TIPO_INVERSION" in dfs["Detalle"].columns and "TIENE_AVAN_FISICO" in dfs["Detalle"].columns:
            f.write("\n### TIPO_INVERSION vs TIENE_AVAN_FISICO\n")
            f.write("| Tipo Inversión | Tiene Avance Físico | Cantidad | % del Total |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            cross = (
                dfs["Detalle"]
                .group_by(["TIPO_INVERSION", "TIENE_AVAN_FISICO"])
                .agg(pl.len().alias("count"))
                .sort(["TIPO_INVERSION", "TIENE_AVAN_FISICO"])
            )
            total = len(dfs["Detalle"])
            for row in cross.to_dicts():
                pct = row["count"] / total * 100
                f.write(f"| {row['TIPO_INVERSION']} | {row['TIENE_AVAN_FISICO']} | {row['count']:,} | {pct:.1f}% |\n")

    print(f"Reporte guardado en {path}")


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def run_eda() -> None:
    print("Perfilado Preliminar de Datos — Capa Bronze\n")

    df_det  = load_cast(DETALLE_BRONZE, DETALLE_NUMERIC)
    df_f12b = load_cast(F12B_BRONZE,    F12B_NUMERIC)
    df_cie  = pl.read_parquet(CIERRE_BRONZE)

    print(f"  Detalle : {df_det.height:,} filas x {df_det.width} columnas")
    print(f"  F12B    : {df_f12b.height:,} filas x {df_f12b.width} columnas")
    print(f"  Cierre  : {df_cie.height:,} filas x {df_cie.width} columnas")

    dfs = {"Detalle": df_det, "F12B": df_f12b, "Cierre": df_cie}

    plot_missing(dfs)
    audit_join_overlap(dfs)
    plot_numeric_outliers(df_det,  DETALLE_NUMERIC, "03_detalle", "Detalle")
    plot_numeric_outliers(df_f12b, F12B_NUMERIC,    "03_f12b",   "F12B")
    plot_temporal(df_det)
    plot_f12b_profile(df_f12b, df_det)
    generate_profile_md(dfs)

    print("\nEDA preliminar completo — resultados en reports/eda/")


if __name__ == "__main__":
    run_eda()
