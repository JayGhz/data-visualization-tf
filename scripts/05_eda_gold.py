"""
05_eda_gold.py
EDA analítico post-Gold. Lee únicamente desde la capa Gold.
Visualiza los datos listos para negocio para validar y comunicar hallazgos.

Cubre:
  - Distribución de categorías de problema (CATEGORIA_PROBLEMA — NLP)
  - Distribución de BRECHA por LIFECYCLE y SECTOR
  - Análisis de desactualización (DIAS_SIN_REPORTE)
  - Dispersión Ejecución vs Avance Físico (muestra)

Salida: reports/eda_gold/*.png
"""
import polars as pl
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import GOLD_MASTER, PROJECT_ROOT

REPORT_DIR = PROJECT_ROOT / "reports" / "eda_gold"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

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
    margin=dict(l=70, r=60, t=80, b=60),
)


def save(fig: go.Figure, name: str, width: int = 1400, height: int = 680) -> None:
    path = REPORT_DIR / f"{name}.png"
    fig.write_image(str(path), width=width, height=height, scale=2)
    print(f"  -> {path.name}")


def _base(fig: go.Figure, title: str, **kw) -> go.Figure:
    fig.update_layout(**LAYOUT_BASE, title=dict(text=title, x=0.5), **kw)
    fig.update_xaxes(showgrid=True, gridcolor=C["grid"], zeroline=False,
                     linecolor=C["grid"], linewidth=1)
    fig.update_yaxes(showgrid=True, gridcolor=C["grid"], zeroline=False,
                     linecolor=C["grid"], linewidth=1)
    return fig


# ---------------------------------------------------------------------------
# 1. Distribución de categorías de problema
# ---------------------------------------------------------------------------

def plot_problem_categories(df: pl.DataFrame) -> None:
    if "CATEGORIA_PROBLEMA" not in df.columns:
        print("  [omitido] CATEGORIA_PROBLEMA no encontrada — ejecutar Silver primero.")
        return

    print("\n[1] Distribución de categorías de problema...")
    vc = (
        df.filter(pl.col("CATEGORIA_PROBLEMA").is_not_null())
        .group_by("CATEGORIA_PROBLEMA")
        .agg(pl.len().alias("cantidad"))
        .sort("cantidad", descending=True)
    )

    total = vc["cantidad"].sum()
    vc = vc.with_columns((pl.col("cantidad") / total * 100).alias("pct"))

    categorias = vc["CATEGORIA_PROBLEMA"].to_list()
    cantidades  = vc["cantidad"].to_list()
    pcts        = vc["pct"].to_list()
    n           = len(categorias)
    colores     = (SEQ_COLORS * ((n // len(SEQ_COLORS)) + 1))[:n]

    fig = go.Figure(go.Bar(
        x=categorias,
        y=cantidades,
        marker_color=colores,
        text=[f"{c:,.0f}<br>({p:.1f}%)" for c, p in zip(cantidades, pcts)],
        textposition="outside",
        textfont=dict(size=10, color=C["text"]),
    ))

    _base(
        fig,
        f"Distribución de Cuellos de Botella — Clasificación Semántica NLP"
        f"<br><sup>({total:,} proyectos con problemas registrados)</sup>",
    )
    fig.update_layout(
        yaxis=dict(title="Cantidad de Proyectos", tickformat=","),
        xaxis_title="Categoría de Problema",
    )
    save(fig, "01_problem_categories", width=1200, height=620)


# ---------------------------------------------------------------------------
# 2. Distribución de BRECHA por LIFECYCLE y SECTOR
# ---------------------------------------------------------------------------

def plot_brecha(df: pl.DataFrame) -> None:
    if "BRECHA" not in df.columns:
        print("  [omitido] BRECHA no encontrada.")
        return

    print("\n[2] Distribución de BRECHA por LIFECYCLE...")
    sub = df.filter(
        pl.col("BRECHA").is_not_null() &
        pl.col("BRECHA").is_between(-100, 100)
    )

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            "Distribución de BRECHA por Ciclo de Vida",
            "BRECHA Mediana por Sector (Top 10 por volumen)",
        ],
        horizontal_spacing=0.12,
    )

    # Histogramas solapados por lifecycle
    lifecycle_colores = {"ACTIVE": C["blue"], "CLOSED": C["green"]}
    lifecycle_labels  = {"ACTIVE": "Activo", "CLOSED": "Cerrado"}
    for lifecycle, color in lifecycle_colores.items():
        vals = sub.filter(pl.col("LIFECYCLE") == lifecycle)["BRECHA"].to_numpy()
        if len(vals) == 0:
            continue
        fig.add_trace(
            go.Histogram(
                x=vals, nbinsx=60,
                name=lifecycle_labels[lifecycle],
                marker_color=color,
                opacity=0.65,
            ),
            row=1, col=1,
        )

    fig.add_vline(x=0, line_dash="dot", line_color=C["red"],
                  line_width=1.5, annotation_text="Sin brecha",
                  annotation_font_color=C["red"], row=1, col=1)

    # BRECHA mediana por sector
    top_sectores = (
        sub.group_by("SECTOR")
        .agg(pl.col("BRECHA").median().alias("brecha_mediana"), pl.len().alias("n"))
        .sort("n", descending=True)
        .head(10)
    )

    medianas    = top_sectores["brecha_mediana"].to_list()
    bar_colores = [C["coral"] if v > 0 else C["navy"] for v in medianas]

    fig.add_trace(
        go.Bar(
            x=medianas,
            y=top_sectores["SECTOR"].to_list(),
            orientation="h",
            marker_color=bar_colores,
            showlegend=False,
        ),
        row=1, col=2,
    )
    fig.add_vline(x=0, line_dash="dot", line_color=C["gray"],
                  line_width=1, row=1, col=2)
    fig.update_yaxes(autorange="reversed", row=1, col=2)

    _base(fig, "Brecha Ejecución vs Avance Físico (BRECHA)")
    fig.update_layout(
        barmode="overlay",
        legend=dict(x=0.02, y=0.97, bgcolor="rgba(255,255,255,0.8)",
                    bordercolor=C["grid"], borderwidth=1),
    )
    fig.update_xaxes(title_text="BRECHA (%)", row=1, col=1)
    fig.update_xaxes(title_text="BRECHA Mediana (%)", row=1, col=2)
    fig.update_yaxes(title_text="Proyectos", row=1, col=1)
    save(fig, "02_brecha_analysis", width=1500, height=640)


# ---------------------------------------------------------------------------
# 3. Desactualización — DIAS_SIN_REPORTE
# ---------------------------------------------------------------------------

def plot_staleness(df: pl.DataFrame) -> None:
    if "DIAS_SIN_REPORTE" not in df.columns:
        print("  [omitido] DIAS_SIN_REPORTE no encontrada.")
        return

    print("\n[3] Desactualización de reportes (DIAS_SIN_REPORTE)...")
    sub = df.filter(
        pl.col("DIAS_SIN_REPORTE").is_not_null() &
        (pl.col("LIFECYCLE") == "ACTIVE") &
        (pl.col("DIAS_SIN_REPORTE") >= 0)
    )

    vals  = np.clip(sub["DIAS_SIN_REPORTE"].to_numpy(), 0, 1000)
    total = len(sub)

    sin_30  = int((sub["DIAS_SIN_REPORTE"] > 30).sum())
    sin_90  = int((sub["DIAS_SIN_REPORTE"] > 90).sum())
    sin_180 = int((sub["DIAS_SIN_REPORTE"] > 180).sum())
    print(f"    >30 días sin reporte : {sin_30:,}  ({sin_30/total*100:.1f}%)")
    print(f"    >90 días sin reporte : {sin_90:,}  ({sin_90/total*100:.1f}%)")
    print(f"    >180 días sin reporte: {sin_180:,} ({sin_180/total*100:.1f}%)")

    fig = go.Figure(go.Histogram(
        x=vals, nbinsx=80,
        marker_color=C["blue"],
        opacity=0.80,
        name="Proyectos",
    ))

    umbrales = [
        (30,  C["amber"], "30 días"),
        (90,  C["coral"], "90 días (en riesgo)"),
        (180, C["red"],   "180 días (paralizado)"),
    ]
    for x_val, color, label in umbrales:
        fig.add_vline(
            x=x_val, line_dash="dot", line_color=color, line_width=1.8,
            annotation_text=label, annotation_position="top right",
            annotation_font_color=color,
        )

    fig.add_annotation(
        xref="paper", yref="paper", x=0.98, y=0.93,
        text=(
            f"<b>Resumen</b><br>"
            f">30 días: {sin_30:,} ({sin_30/total*100:.1f}%)<br>"
            f">90 días: {sin_90:,} ({sin_90/total*100:.1f}%)<br>"
            f">180 días: {sin_180:,} ({sin_180/total*100:.1f}%)"
        ),
        showarrow=False, align="right",
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor=C["grid"], borderwidth=1,
        font=dict(size=11, color=C["text"]),
    )

    _base(fig, "Días sin Actualización de Reporte — Proyectos Activos")
    fig.update_layout(
        xaxis_title="Días sin Actualización (limitado a 1000)",
        yaxis=dict(title="Cantidad de Proyectos", tickformat=","),
        showlegend=False,
    )
    save(fig, "03_staleness", width=1300, height=640)


# ---------------------------------------------------------------------------
# 4. Dispersión Ejecución vs Avance Físico
# ---------------------------------------------------------------------------

def plot_execution_vs_physical(df: pl.DataFrame) -> None:
    if "AVANCE_FISICO" not in df.columns or "AVANCE_EJECUCION" not in df.columns:
        print("  [omitido] Columnas AVANCE no encontradas.")
        return

    print("\n[4] Dispersión Ejecución vs Avance Físico...")
    sub = (
        df.filter(
            pl.col("AVANCE_FISICO").is_not_null() &
            pl.col("AVANCE_EJECUCION").is_not_null()
        )
        .sample(n=min(15_000, len(df)), seed=42)
    )

    phys  = sub["AVANCE_FISICO"].to_numpy()
    exec_ = sub["AVANCE_EJECUCION"].to_numpy()

    if "LIFECYCLE" in sub.columns:
        lc_vals   = sub["LIFECYCLE"].to_list()
        color_map = {"ACTIVE": C["blue"], "CLOSED": C["teal"]}
        colores   = [color_map.get(lc, C["gray"]) for lc in lc_vals]
    else:
        colores = C["blue"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=phys, y=exec_,
        mode="markers",
        marker=dict(color=colores, size=4, opacity=0.20),
        name="Proyectos",
    ))

    # Línea de alineación perfecta
    fig.add_trace(go.Scatter(
        x=[0, 100], y=[0, 100],
        mode="lines",
        line=dict(color=C["red"], dash="dot", width=2),
        name="Alineación perfecta",
    ))

    fig.add_annotation(x=72, y=22,
                       text="Finanzas ADELANTE del físico",
                       showarrow=False,
                       font=dict(color=C["coral"], size=10))
    fig.add_annotation(x=22, y=72,
                       text="Físico ADELANTE de finanzas",
                       showarrow=False,
                       font=dict(color=C["green"], size=10))

    _base(
        fig,
        "Progreso Físico vs Ejecución Financiera"
        "<br><sup>Muestra de 15 000 proyectos — puntos sobre la diagonal = finanzas por delante</sup>",
    )
    fig.update_layout(
        xaxis=dict(title="Avance Físico (%)", range=[-5, 105]),
        yaxis=dict(title="Avance de Ejecución (%)", range=[-5, 105]),
        legend=dict(x=0.02, y=0.97, bgcolor="rgba(255,255,255,0.8)",
                    bordercolor=C["grid"], borderwidth=1),
    )
    save(fig, "04_execution_vs_physical", width=900, height=900)


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def run_eda_gold() -> None:
    print("EDA Gold — reporte analítico post-pipeline\n")
    df = pl.read_parquet(GOLD_MASTER)
    print(f"  Tabla Gold: {len(df):,} filas x {df.width} columnas\n")

    plot_problem_categories(df)
    plot_brecha(df)
    plot_staleness(df)
    plot_execution_vs_physical(df)

    print("\nEDA Gold completo — resultados en reports/eda_gold/")


if __name__ == "__main__":
    run_eda_gold()
