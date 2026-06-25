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

    grouped = (
        df_copy
        .dropna(subset=["sale_date"])
        .set_index("sale_date")
        .resample("W")
        .agg(
            revenue=("total_price", "sum"),
            order_count=("invoice_id", "nunique"),
            avg_order_value=("total_price", "mean"),
        )
        .reset_index()
        .rename(columns={"sale_date": "week"})
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
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        title=dict(x=0.02),
    )
    fig.update_traces(line=dict(width=3))
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
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=value,
                title={"text": label},
                number={"valueformat": ",.2f"},
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


# --- DACA / UrbanStyle värvipalett (algsest analüüsist) ---
TEAL = "#009B8D"
NAVY = "#1A1A2E"
GRAY = "#6B7280"
LIGHT_GRAY = "#F3F4F6"
WHITE = "#FFFFFF"
BLUE = "#0072B2"
AMBER = "#E69F00"
ORANGE = "#D55E00"

SEGMENT_ORDER = ["VIP Champions", "Loyal", "Potential", "At Risk", "Lost"]
SEGMENT_COLORS = {
    "VIP Champions": TEAL,
    "Loyal": BLUE,
    "Potential": AMBER,
    "At Risk": ORANGE,
    "Lost": GRAY,
}
CHART_WIDTH = 760
CHART_HEIGHT = 430
BASE_LAYOUT = dict(
    plot_bgcolor=WHITE,
    paper_bgcolor=WHITE,
    font=dict(color=NAVY, size=11),
    title=dict(font=dict(color=NAVY, size=17), x=0.02),
)


def add_customer_names(rfm: pd.DataFrame, df_customers: pd.DataFrame) -> pd.DataFrame:
    """Lisab RFM tabelile kliendi nime (või 'ID xxx', kui nimi puudub)."""
    cols = [c for c in ["customer_id", "first_name", "last_name"] if c in df_customers.columns]
    info = df_customers[cols].drop_duplicates(subset=["customer_id"])

    rfm_viz = rfm.merge(info, on="customer_id", how="left")

    if "first_name" in rfm_viz.columns and "last_name" in rfm_viz.columns:
        rfm_viz["customer_name"] = (
            rfm_viz["first_name"].fillna("") + " " + rfm_viz["last_name"].fillna("")
        ).str.strip()
    elif "first_name" in rfm_viz.columns:
        rfm_viz["customer_name"] = rfm_viz["first_name"].fillna("")
    else:
        rfm_viz["customer_name"] = ""

    rfm_viz["customer_id_clean"] = (
        pd.to_numeric(rfm_viz["customer_id"], errors="coerce").astype("Int64").astype(str)
    )
    rfm_viz["customer_name"] = rfm_viz["customer_name"].replace("", pd.NA)
    rfm_viz["customer_name"] = rfm_viz["customer_name"].fillna("ID " + rfm_viz["customer_id_clean"])

    rfm_viz["segment"] = pd.Categorical(rfm_viz["segment"], categories=SEGMENT_ORDER, ordered=True)
    return rfm_viz


def create_segment_distribution_chart(rfm_viz: pd.DataFrame):
    """Bar chart kliendisegmentide jaotusest."""
    counts = rfm_viz["segment"].value_counts().reset_index()
    counts.columns = ["segment", "klientide_arv"]
    counts = counts.sort_values("klientide_arv", ascending=False)

    fig = px.bar(
        counts, x="segment", y="klientide_arv", color="segment",
        color_discrete_map=SEGMENT_COLORS, text="klientide_arv",
        title="UrbanStyle kliendisegmentide jaotus",
        labels={"segment": "Kliendisegment", "klientide_arv": "Klientide arv"},
        category_orders={"segment": counts["segment"].tolist()},
        width=CHART_WIDTH, height=CHART_HEIGHT,
    )
    fig.update_traces(textposition="outside", marker_line_width=0,
                       textfont=dict(size=11, color=NAVY))
    fig.update_layout(**BASE_LAYOUT, showlegend=False,
                       xaxis=dict(title="", tickangle=-10, showgrid=False),
                       yaxis=dict(title="Klientide arv", gridcolor=LIGHT_GRAY),
                       margin=dict(l=70, r=30, t=70, b=75))
    return fig


def create_segment_profile_chart(rfm_viz: pd.DataFrame):
    """Scatter plot: segmentide keskmine recency vs monetary."""
    profile = (
        rfm_viz.groupby("segment", observed=True)
        .agg(avg_recency=("recency_days", "mean"),
             avg_monetary=("monetary", "mean"),
             customers=("customer_id", "count"))
        .reset_index()
    )

    fig = px.scatter(
        profile, x="avg_recency", y="avg_monetary", size="customers",
        color="segment", text="segment", color_discrete_map=SEGMENT_COLORS,
        category_orders={"segment": SEGMENT_ORDER},
        title="RFM segmentide profiil",
        labels={"avg_recency": "Päevi viimasest ostust",
                "avg_monetary": "Keskm. kogukulutus", "customers": "Klientide arv"},
        width=CHART_WIDTH, height=CHART_HEIGHT, size_max=44,
    )
    fig.update_traces(textposition="top center",
                       marker=dict(opacity=0.78, line=dict(width=1, color=WHITE)),
                       textfont=dict(size=10, color=NAVY))
    fig.update_layout(**BASE_LAYOUT, showlegend=False,
                       xaxis=dict(title="Päevi viimasest ostust", gridcolor=LIGHT_GRAY),
                       yaxis=dict(title="Keskm. kogukulutus", gridcolor=LIGHT_GRAY,
                                  tickformat=",.0f"),
                       margin=dict(l=75, r=35, t=70, b=70))
    return fig


def create_top_vip_chart(rfm_viz: pd.DataFrame, top_n: int = 10):
    """Horisontaalne bar chart: top N VIP klienti kogukulutuse järgi."""
    top_vip = (
        rfm_viz[rfm_viz["segment"] == "VIP Champions"]
        .nlargest(top_n, "monetary")
        .sort_values("monetary", ascending=False)
        .copy()
    )
    top_vip["monetary_label"] = top_vip["monetary"].map(lambda x: f"{x/1000:.1f}k")
    vip_order = top_vip["customer_name"].tolist()

    fig = px.bar(
        top_vip, x="monetary", y="customer_name", orientation="h",
        text="monetary_label", color_discrete_sequence=[TEAL],
        title=f"Top {top_n} VIP klienti", width=CHART_WIDTH, height=CHART_HEIGHT,
        labels={"customer_name": "", "monetary": "Kogukulutus"},
    )
    fig.update_traces(textposition="inside", insidetextanchor="end",
                       textfont=dict(color=WHITE, size=11), marker_line_width=0,
                       hovertemplate="<b>%{y}</b><br>Kogukulutus: %{x:,.2f} EUR<extra></extra>")
    fig.update_layout(**BASE_LAYOUT, showlegend=False,
                       xaxis=dict(title="Kogukulutus", gridcolor=LIGHT_GRAY, tickformat=",.0f"),
                       yaxis=dict(title="", showgrid=False, categoryorder="array",
                                  categoryarray=vip_order[::-1]),
                       margin=dict(l=120, r=35, t=70, b=70))
    return fig


def export_segment_lists(rfm: pd.DataFrame, output_dir: str = "output"):
    """
    Ekspordib kogu RFM-tabeli + eraldi VIP ja At-Risk nimekirjad,
    ajatempliga failinimedega.
    """
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    paths = {}
    paths["rfm"] = os.path.join(output_dir, f"rfm-analysis_{date_str}.csv")
    rfm.to_csv(paths["rfm"], index=False)

    vip = rfm[rfm["segment"] == "VIP Champions"]
    paths["vip"] = os.path.join(output_dir, f"vip-customers_{date_str}.csv")
    vip.to_csv(paths["vip"], index=False)

    at_risk = rfm[rfm["segment"] == "At Risk"]
    paths["at_risk"] = os.path.join(output_dir, f"at-risk-customers_{date_str}.csv")
    at_risk.to_csv(paths["at_risk"], index=False)

    logger.info("export_segment_lists: %s", paths)
    return paths


def business_summary(rfm: pd.DataFrame) -> str:
    """Genereerib äritõlgenduse teksti stakeholderile (Marko)."""
    total_revenue = rfm["monetary"].sum()
    vip = rfm[rfm["segment"] == "VIP Champions"]
    at_risk = rfm[rfm["segment"] == "At Risk"]
    lost = rfm[rfm["segment"] == "Lost"]
    potential = rfm[rfm["segment"] == "Potential"]

    vip_revenue_share = vip["monetary"].sum() / total_revenue * 100 if total_revenue else 0

    return (
        f"UrbanStyle'il on {len(vip)} VIP Champions segmenti kuuluvat klienti, "
        f"kes annavad kokku {vip_revenue_share:.1f}% kogukäibest. "
        f"At Risk segmenti kuulub {len(at_risk)} klienti, Lost segmenti {len(lost)} klienti, "
        f"ja Potential segmenti {len(potential)} klienti, keda saab sihitud pakkumistega kasvatada."
    )


if __name__ == "__main__":
    # See plokk käivitub AINULT siis, kui faili jooksutatakse otse
    # (python visualize_export.py). Loob näidisandmed ja kutsub
    # peamised funktsioonid välja, et tulemust kohe näha (output/ kausta).
    print("Käivitan visualize_export.py näidisandmetega...")

    sample_sales = pd.DataFrame({
        "sale_date": pd.date_range("2024-01-01", periods=30),
        "invoice_id": range(1000, 1030),
        "total_price": [100 + i * 5 for i in range(30)],
    })

    df_weekly = calculate_weekly_aggregates(sample_sales)
    fig_weekly = create_weekly_chart(df_weekly)

    sample_kpis = {
        "total_revenue": float(sample_sales["total_price"].sum()),
        "unique_customers": 12,
        "avg_order_value": float(sample_sales["total_price"].mean()),
    }
    fig_kpi = create_kpi_summary(sample_kpis)

    saved = export_charts({"weekly_revenue": fig_weekly, "kpi_summary": fig_kpi})
    print(f"Valmis! Diagrammid salvestatud: {saved}")
