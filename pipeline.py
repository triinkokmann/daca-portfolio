"""
Roll D: Automation Script (pipeline.py)
Orkestreerib Extract -> Transform -> Visualize -> Export
ühe käsuga: python pipeline.py

See fail on meeskonna pipeline'i orkestreerija — ta ise ei sisalda
äriloogikat, vaid kutsub õiges järjekorras välja rollide A, B ja C
funktsioonid. Kui mõni etapp muutub, piisab muudatusest vastava rolli
failis; pipeline.py jääb samaks.
"""

import logging
import os
import sys
import time
from datetime import datetime

# Logimine seadistatakse ENNE moodulite importi, sest Python lubab
# basicConfig kutsuda ainult üks kord — kui moodulid imporditakse enne,
# võtavad nad logimise ära ja pipeline'i logid ei jõua faili.
os.makedirs("logs", exist_ok=True)
log_filename = datetime.now().strftime("logs/pipeline_%Y%m%d.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=log_filename,
    encoding="utf-8",
)

import yaml

# Loe konfiguratsioon failist
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# Roll A moodul — andmete pärimine Supabase API-st.
# DEFAULT_START_DATE ja DEFAULT_END_DATE on meeskonna kokkulepe:
# kasutame 2023-2024 andmeid, sest need aastad on baasis terviklikud.
from data_fetcher import (
    fetch_sales, fetch_customers, fetch_products,
    DEFAULT_START_DATE, DEFAULT_END_DATE
)

# Roll B moodul — andmete puhastamine ja koondamine.
# calculate_weekly_aggregates kasutame B versioonist Transform etapis,
# sest seal on veergude nimed ühtsed teiste B funktsioonidega.
from transform import (
    clean_data, calculate_weekly_aggregates,
    calculate_kpis, merge_datasets
)

# Roll C moodul — visualiseerimine ja eksport.
# weekly_for_chart on C-spetsiifiline versioon nädalate koondamisest,
# mis kasutab veerunimesid 'week' ja 'revenue' — Plotly ootab just neid.
# Sellepärast impordi alias'ega, et mitte segamini ajada B versiooniga.
from visualize_export import (
    calculate_weekly_aggregates as weekly_for_chart,
    create_weekly_chart, create_kpi_summary,
    export_results, export_charts
)

# Näita logid ka terminalis
logger = logging.getLogger(__name__)


def run_pipeline(
    start_date: str = DEFAULT_START_DATE,
    end_date: str = DEFAULT_END_DATE,
    output_dir: str = "output",
) -> dict:
    """
    Käivitab täieliku ETL pipeline'i:
    Extract -> Transform -> Visualize -> Export

    Args:
        start_date: Perioodi algus (vaikimisi meeskonna kokkulepe 2023-01-01)
        end_date:   Perioodi lõpp (vaikimisi 2024-12-31)
        output_dir: Kaust, kuhu CSV ja HTML failid salvestatakse

    Tagastab kokkuvõtte dict'ina, mis sisaldab KPI-sid ja salvestatud failiteed.
    Tõstab RuntimeError, kui kriitilised etapid (Extract, Transform, Export) ebaõnnestuvad.
    """
    results = {}

    # ── ETAPP 1: EXTRACT ──────────────────────────────────────────
    # Extract on pipeline'i esimene ja kõige haavatavam samm —
    # sõltub välisest teenusest (Supabase). Sellepärast on siin
    # kaheastmeline veakäsitlus: esmalt proovime API-d, siis CSV fallback'i.
    logger.info("=== ETAPP 1: EXTRACT (periood %s kuni %s) ===", start_date, end_date)
    t0 = time.time()
    try:
        df_sales_raw = fetch_sales(start_date=start_date, end_date=end_date)
        df_customers_raw = fetch_customers()
        # Tooteandmed laetakse samuti, et pipeline oleks valmis
        # tulevasteks analüüsideks või teiste moodulite kasutuseks.
        df_products_raw = fetch_products()
        logger.info(
            "Extract OK — müük: %d rida, kliendid: %d, tooted: %d (%.1fs)",
            len(df_sales_raw), len(df_customers_raw), len(df_products_raw),
            time.time() - t0
        )
    except Exception as exc:
        # API viga — võib olla ajutine võrgutõrge või vale API key.
        # Logime vea ja proovime kohalikke CSV faile (datasets/ kaust).
        logger.error("Extract EBAÕNNESTUS: %s", exc)
        logger.info("Proovin uuesti fallback-andmetega...")
        try:
            df_sales_raw = fetch_sales(start_date=start_date, end_date=end_date, use_fallback=True)
            df_customers_raw = fetch_customers(use_fallback=True)
            # Laeme ka toodete fallback-andmed, et andmekogumid oleksid täielikud.
            df_products_raw = fetch_products(use_fallback=True)
            logger.info("Extract OK (fallback CSV) — %d müügirida", len(df_sales_raw))
        except Exception as exc2:
            # Ka fallback ebaõnnestus — pole mõtet jätkata, tõstame vea.
            logger.error("Extract ebaõnnestus ka fallback'iga: %s", exc2)
            raise RuntimeError(f"Extract täielikult ebaõnnestunud: {exc2}") from exc2

    # ── ETAPP 2: TRANSFORM ────────────────────────────────────────
    # Transform on pipeline'i "aju" — siin muutuvad toorandmed
    # Marko jaoks kasutatavaks infoks. Vea korral ei saa jätkata,
    # sest järgmised etapid sõltuvad siinsete funktsioonide väljundist.
    logger.info("=== ETAPP 2: TRANSFORM ===")
    t1 = time.time()
    try:
        # Puhastame müügi- ja kliendiandmed eraldi — duplikaadid välja,
        # kuupäevad õigesse formaati.
        df_sales = clean_data(df_sales_raw)
        df_customers = clean_data(df_customers_raw)
        logger.info("Puhastamine OK — duplikaadid eemaldatud")

        # Nädalased koondandmed — Marko tahab trendijoonist, mitte üksikuid tehinguid.
        df_weekly = calculate_weekly_aggregates(df_sales)
        logger.info("Nädalakoondandmed OK — %d nädalat", len(df_weekly))

        # KPI-d tagastatakse dict'ina, et neid saaks kasutada nii
        # visualiseerimises (indicator kaardid) kui ka lõppkokkuvõttes.
        kpis = calculate_kpis(df_sales)
        logger.info(
            "KPI-d OK — käive: %.2f EUR, kliente: %d, AOV: %.2f EUR",
            kpis["total_revenue"], kpis["unique_customers"], kpis["avg_order_value"]
        )

        # Liidame müügi- ja kliendiandmed customer_id järgi,
        # et eksporditud CSV sisaldaks kliendi nime, mitte ainult ID-d.
        df_merged = merge_datasets(df_sales, df_customers)
        logger.info(
            "Liitmine OK — %d rida, %d veergu (%.1fs)",
            df_merged.shape[0], df_merged.shape[1], time.time() - t1
        )
        results["kpis"] = kpis
    except Exception as exc:
        # Transform vea korral saadame teavituse ja peatame pipeline'i.
        # Vigased andmed eksportida ei tohi — Marko teeks vale otsuse.
        logger.error("Transform EBAÕNNESTUS: %s — pipeline peatub", exc)
        _send_alert(f"Transform ebaõnnestus: {exc}")
        raise

    # ── ETAPP 3: VISUALIZE ────────────────────────────────────────
    # Visualiseerimine on ainus etapp, mille viga ei peata pipeline'i.
    # Põhjus: kui diagramm ei teki, on CSV eksport ikkagi kasulik.
    # Sellepärast salvestame vea hoiatusena (warning), mitte kriitilisena.
    logger.info("=== ETAPP 3: VISUALIZE ===")
    t2 = time.time()
    try:
        # C mooduli weekly_for_chart ootab veerunimesid 'week' ja 'revenue',
        # mitte 'sale_date' ja 'total_revenue' nagu B versioon tagastab.
        # Sellepärast kutsume C-spetsiifilist funktsiooni, mitte B oma.
        df_weekly_chart = weekly_for_chart(df_sales)
        fig_weekly = create_weekly_chart(df_weekly_chart)
        fig_kpi = create_kpi_summary(kpis)
        logger.info("Diagrammid loodud (%.1fs)", time.time() - t2)
    except Exception as exc:
        logger.warning("Visualiseerimine ebaõnnestus (jätkame ekspordiga): %s", exc)
        # None väärtused kontrollib Export etapp — kui fig on None, ei ekspordita.
        fig_weekly = None
        fig_kpi = None

    # ── ETAPP 4: EXPORT ───────────────────────────────────────────
    # Eksport salvestab tulemused output/ kausta ajatempliga failinimedega.
    # export_results() lisab failinimele ajatempli,
    # et varasemaid tulemusi üle ei kirjutataks.
    logger.info("=== ETAPP 4: EXPORT ===")
    t3 = time.time()
    try:
        csv_path = export_results(df_merged, output_dir=output_dir, prefix="pipeline_results")
        logger.info("CSV salvestatud: %s", csv_path)

        # Kogume ainult need diagrammid, mis visualiseerimises tekkisid.
        # Kui mõni fig on None (vea tõttu), jätame selle vahele.
        figures = {}
        if fig_weekly is not None:
            figures["weekly_revenue"] = fig_weekly
        if fig_kpi is not None:
            figures["kpi_summary"] = fig_kpi
        if figures:
            html_paths = export_charts(figures, output_dir=output_dir)
            logger.info("HTML diagrammid salvestatud: %s", html_paths)

        results["csv"] = csv_path
        logger.info("Export OK (%.1fs)", time.time() - t3)
    except Exception as exc:
        logger.error("Export EBAÕNNESTUS: %s", exc)
        raise

    return results


def _send_alert(message: str) -> None:
    """
    Saadab teavituse pipeline'i vea korral.

    Praegu kirjutab logi — tootmiskeskkonnas asenda see
    smtplib e-mailiga või Google Workspace Chat webhook'iga.

    Näide webhook'iga:
        import requests
        requests.post(WEBHOOK_URL, json={"text": f"⚠️ UrbanStyle pipeline: {message}"})
    """
    logger.warning("TEAVITUS: %s", message)


if __name__ == "__main__":
    # __main__ blokk käivitub ainult siis, kui faili jooksutatakse otse
    # (python pipeline.py), mitte siis kui see imporditakse teise moodulina.
    print("=" * 55)
    print("  URBANSTYLE ETL PIPELINE")
    print(f"  Käivitatud: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    pipeline_start = time.time()

    try:
        results = run_pipeline(
            start_date=config["pipeline"]["start_date"],
            end_date=config["pipeline"]["end_date"],
            output_dir=config["pipeline"]["output_dir"],
        )
        elapsed = time.time() - pipeline_start

        print(f"\n✅ VALMIS ({elapsed:.1f}s) | Käive: {results['kpis']['total_revenue']:,.0f} EUR | Kliente: {results['kpis']['unique_customers']} | CSV: {results.get('csv', '—')}")

    except Exception as exc:
        elapsed = time.time() - pipeline_start
        print(f"\n❌ EBAÕNNESTUS ({elapsed:.1f}s): {exc}")
        # logger.exception lisab automaatselt täieliku traceback'i logi,
        # mis aitab hiljem täpselt välja selgitada, kus viga tekkis.
        logger.exception("Pipeline crash")
        sys.exit(1)

    print("=" * 55)
