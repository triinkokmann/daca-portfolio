"""
ROLL C: Visualization + Saving
Loob Plotly diagrammid töödeldud andmetest ja ekspordib tulemused
failidesse (CSV + HTML).
"""

import os
import logging
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


def calculate_weekly_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rühmitab andmed nädalate kaupa ja arvutab nädalase käibe (revenue),
    unikaalsete tellimuste arvu (order_count) ning keskmise tellimuse
    väärtuse (avg_order_value).
    """
    if df.empty:
        return df

    df_copy = df.copy()
    df_copy['sale_date'] = pd.to_datetime(df_copy['sale_date'], errors='coerce')
    df_copy['total_price'] = pd.to_numeric(df_copy['total_price'], errors='coerce').fillna(0.0)
    df_copy['invoice_id'] = df_copy['invoice_id'].astype(str)

    df_copy = df_copy.dropna(subset=["sale_date"])
    df_copy["week"] = df_copy["sale_date"].dt.to_period("W-SUN").apply(lambda period: period.start_time)

    grouped = (
        df_copy
        .groupby("week", as_index=False)
        .agg(
            revenue=("total_price", "sum"),
            order_count=("invoice_id", "nunique"),
            avg_order_value=("total_price", "mean"),
        )
        .sort_values("week")
    )
    return grouped


def create_weekly_chart(df_weekly: pd.DataFrame):
    """
    Loob Plotly joondiagrammi nädalastest tululiikumistest.

    Eeldab, et df_weekly sisaldab veerge 'week' ja 'revenue'
    (vt transform.calculate_weekly_aggregates).
    """
    if df_weekly is None or df_weekly.empty:
        raise ValueError("create_weekly_chart: df_weekly on tühi või None")

    fig = px.line(
        df_weekly,
        x="week",
        y="revenue",
        markers=True,
        title="UrbanStyle — nädalane tulu",
        labels={"week": "Nädal", "revenue": "Tulu (EUR)"},
    )
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=6),
        hovertemplate="Nädal algab %{x|%Y-%m-%d}<br>Käive: %{y:,.2f} EUR<extra></extra>",
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        title=dict(x=0.02),
        xaxis=dict(
            tickformat="%Y-%m-%d",
            tickangle=-45,
            title="Nädala algus",
        ),
        yaxis=dict(
            title="Käive (EUR)",
            tickformat=",.0f",
        ),
        hovermode="x unified",
    )
    return fig


def create_kpi_summary(kpis: dict):
    """
    Loob Plotly indicator-kaartide rea peamiste KPI-de näitamiseks.

    Eeldab dict'i kujul nagu transform.calculate_kpis() tagastab:
    {'total_revenue': ..., 'unique_customers': ..., 'avg_order_value': ...}
    """
    if not kpis:
        raise ValueError("create_kpi_summary: kpis dict on tühi")

    labels_map = {
        "total_revenue": "Kogutulu (EUR)",
        "unique_customers": "Unikaalseid kliente",
        "avg_order_value": "Keskmine tellimuse väärtus (EUR)",
    }

    fig = go.Figure()
    n = len(kpis)
    width = 1.0 / n

    for i, (key, value) in enumerate(kpis.items()):
        label = labels_map.get(key, key)
        value_format = ",.0f" if key == "unique_customers" else ",.2f"
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=value,
                title={"text": label},
                number={"valueformat": value_format},
                domain={"x": [i * width, (i + 1) * width], "y": [0, 1]},
            )
        )

    fig.update_layout(
        title="UrbanStyle — KPI kokkuvõte",
        paper_bgcolor="white",
        height=250,
    )
    return fig


def export_results(df: pd.DataFrame, output_dir: str = "output", prefix: str = "results"):
    """
    Salvestab DataFrame'i CSV-faili ajatempliga failinimega.

    Tagastab kasutatud faili tee, et pipeline saaks sellele viidata.
    """
    if df is None:
        raise ValueError("export_results: df on None")

    os.makedirs(output_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(output_dir, f"{prefix}_{date_str}.csv")

    df.to_csv(filepath, index=False)
    logger.info("Eksporditud %d rida faili %s", len(df), filepath)
    return filepath


def export_charts(figures: dict, output_dir: str = "output"):
    """
    Salvestab Plotly figuurid HTML-failidena.

    figures: dict kujul {"failinimi_ilma_laiendita": fig}
    Tagastab loodud failiteede nimekirja.
    """
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    saved_paths = []
    for name, fig in figures.items():
        filepath = os.path.join(output_dir, f"{name}_{date_str}.html")
        fig.write_html(filepath)
        logger.info("Diagramm salvestatud: %s", filepath)
        saved_paths.append(filepath)

    return saved_paths


if __name__ == "__main__":
    # See plokk käivitub AINULT siis, kui faili jooksutatakse otse
    # (python visualize_export.py). Loob näidisandmed ja kutsub
    # peamised funktsioonid välja, et tulemust kohe näha (output/ kausta).
    print("Käivitan visualize_export.py päris müügiandmetega...")

    from data_fetcher import DEFAULT_END_DATE, DEFAULT_START_DATE, fetch_sales
    from transform import calculate_kpis

    sample_sales = fetch_sales(start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE)

    df_weekly = calculate_weekly_aggregates(sample_sales)
    fig_weekly = create_weekly_chart(df_weekly)
    sample_kpis = calculate_kpis(sample_sales)
    fig_kpi = create_kpi_summary(sample_kpis)

    saved = export_charts({"weekly_revenue": fig_weekly, "kpi_summary": fig_kpi})
    print(f"Valmis! Diagrammid salvestatud: {saved}")

    csv_path = export_results(sample_sales, prefix="naidis_results")
    print(f"Valmis! CSV salvestatud: {csv_path}")
