"""
Roll A: API Query moodul UrbanStyle pipeline'i jaoks.

Mooduli eesmärk:
- pärida sales, customers ja products tabelid Supabase API-st;
- tagastada alati pandas DataFrame;
- kasutada vajadusel kuupäevafiltrit sales tabeli puhul;
- käsitleda API vigu arusaadavalt;
- suurte tabelite jaoks kasutada pagination'it;
- ajutiste API tõrgete puhul proovida uuesti exponential backoff'iga;
- kui Supabase pole kättesaadav, võtta samad andmed datasets/ kaustas olevatest CSV failidest.

Kasutamine:
    python data_fetcher.py
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv

# Supabase import on try/except sees, et programm oskaks anda arusaadava
# veateate ka siis, kui keegi pole veel sõltuvusi paigaldanud.
try:
    from supabase import create_client
except ImportError:  # pragma: no cover - kasulik sõnum juhul, kui teek puudub
    create_client = None  # type: ignore


# __file__ tähendab "selle faili asukoht".
# Nii leiab kood datasets/ kausta üles ka siis, kui skript käivitatakse
# mõnest teisest terminali asukohast.
DATASETS_DIR = Path(__file__).resolve().parent / "datasets"

# Supabase tagastab sageli piiratud arvu ridu korraga.
# 1000 rea kaupa küsimine teeb päringu töökindlaks ka suure tabeli puhul.
DEFAULT_PAGE_SIZE = 1000

# Kui API päring korraks ebaõnnestub, ei anna me kohe alla.
# Proovime sama päringut mitu korda, sest võrgutõrked võivad olla ajutised.
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_SECONDS = 1.0

# Meeskonna kokkulepe: demo ja pipeline kasutavad 2023-2024 andmeid,
# sest need aastad on andmebaasis terviklikud.
DEFAULT_START_DATE = "2023-01-01"
DEFAULT_END_DATE = "2024-12-31"

logger = logging.getLogger(__name__)


class DataFetchError(RuntimeError):
    """Selge domeeniviga, kui andmeid ei saa API-st ega CSV fallback'ist kätte."""


def get_supabase_client() -> Any:
    """
    Loo Supabase klient .env faili põhjal.

    Oodatud muutujad .env failis:
    - SUPABASE_URL
    - SUPABASE_KEY

    Funktsioon ei sisalda API võtmeid koodis, sest juhendi turvanõue ütleb,
    et võtmed tuleb alati lugeda keskkonnamuutujatest.
    """
    # load_dotenv() loeb .env failist SUPABASE_URL ja SUPABASE_KEY.
    # See on turvalisem kui võtmete otse koodi kirjutamine.
    load_dotenv()

    if create_client is None:
        raise DataFetchError(
            "Supabase teek puudub. Paigalda sõltuvused käsuga: pip install -r requirements.txt"
        )

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise DataFetchError(
            "Supabase tunnused puuduvad. Lisa .env faili SUPABASE_URL ja SUPABASE_KEY."
        )

    return create_client(url, key)


def _load_csv_fallback(table_name: str) -> pd.DataFrame:
    """
    Lae varuandmed datasets/ kaustast, kui API päring ebaõnnestub.

    See teeb pipeline'i demo-kindlaks: kui Supabase on maas või API key vale,
    saab töö ikkagi näidata sama kujuga andmetel.
    """
    # table_name on näiteks "sales", seega failiks saab datasets/sales.csv.
    csv_path = DATASETS_DIR / f"{table_name}.csv"
    if not csv_path.exists():
        raise DataFetchError(f"Fallback CSV puudub: {csv_path}")

    logger.warning("Kasutan fallback CSV faili: %s", csv_path)
    return pd.read_csv(csv_path)


def _apply_sales_date_filter(
    df: pd.DataFrame,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    """Rakenda CSV fallback'i puhul sama kuupäevafilter nagu API päringus."""
    if df.empty or "sale_date" not in df.columns:
        return df

    # copy() aitab vältida olukorda, kus muudame kogemata algset DataFrame'i.
    filtered = df.copy()

    # errors="coerce" muudab vigased kuupäevad NaT väärtuseks,
    # mitte ei lõpeta programmi veaga.
    filtered["sale_date"] = pd.to_datetime(filtered["sale_date"], errors="coerce")

    if start_date:
        filtered = filtered[filtered["sale_date"] >= pd.to_datetime(start_date)]
    if end_date:
        filtered = filtered[filtered["sale_date"] <= pd.to_datetime(end_date)]

    return filtered.reset_index(drop=True)


def _execute_with_retry(query: Any, table_name: str, page_start: int) -> Any:
    """
    Käivita Supabase query retry loogikaga.

    Exponential backoff tähendab, et iga järgmine katse ootab kauem:
    1s, 2s, 4s jne. See aitab ajutiste võrgu- või API probleemide korral.
    """
    last_error: Exception | None = None

    for attempt in range(1, DEFAULT_MAX_RETRIES + 1):
        try:
            return query.execute()
        except Exception as exc:  # Supabase client võib visata eri tüüpi vigu
            last_error = exc
            # 1. katse järel ootame 1s, 2. katse järel 2s, 3. katse järel 4s.
            # See ongi exponential backoff.
            wait_seconds = DEFAULT_BACKOFF_SECONDS * (2 ** (attempt - 1))
            logger.warning(
                "API päring ebaõnnestus (%s, read alates %s), katse %s/%s: %s",
                table_name,
                page_start,
                attempt,
                DEFAULT_MAX_RETRIES,
                exc,
            )
            if attempt < DEFAULT_MAX_RETRIES:
                time.sleep(wait_seconds)

    raise DataFetchError(
        f"Supabase päring tabelile '{table_name}' ebaõnnestus pärast "
        f"{DEFAULT_MAX_RETRIES} katset: {last_error}"
    )


def _fetch_table_paginated(
    table_name: str,
    start_date: str | None = None,
    end_date: str | None = None,
    use_fallback: bool = True,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> pd.DataFrame:
    """
    Üldine tabeli pärija, mida kasutavad fetch_sales/customers/products.

    Pagination on vajalik, sest Supabase tagastab vaikimisi piiratud arvu ridu.
    Siin küsime andmed lehekülgedena kuni viimane lehekülg on tühi või väiksem
    kui page_size.
    """
    try:
        client = get_supabase_client()
        all_rows: list[dict[str, Any]] = []
        page_start = 0

        while True:
            page_end = page_start + page_size - 1
            query = client.table(table_name).select("*")

            # Kuupäevafiltrit rakendame ainult sales tabelile,
            # sest customers/products tabelitel ei ole sale_date veergu.
            if table_name == "sales":
                if start_date:
                    query = query.gte("sale_date", start_date)
                if end_date:
                    query = query.lte("sale_date", end_date)

            # range(page_start, page_end) küsib ühe "lehekülje" andmeid.
            # Näiteks 0-999, siis 1000-1999 jne.
            query = query.range(page_start, page_end)
            response = _execute_with_retry(query, table_name, page_start)
            rows = response.data or []
            all_rows.extend(rows)

            logger.info(
                "Tabel %s: laetud read %s-%s, saadi %s rida",
                table_name,
                page_start,
                page_end,
                len(rows),
            )

            # Kui viimasel lehel tuli vähem ridu kui page_size,
            # siis rohkem andmeid ei ole ja tsükkel võib lõppeda.
            if len(rows) < page_size:
                break

            page_start += page_size

        # Supabase tagastab listi dict'e; pandas muudab selle DataFrame'iks,
        # millega Roll B saab edasi töötada.
        df = pd.DataFrame(all_rows)
        if df.empty:
            raise DataFetchError(f"Supabase tagastas tabelile '{table_name}' tühja tulemuse.")

        return df

    except Exception as exc:
        if not use_fallback:
            raise

        logger.warning(
            "Supabase päring tabelile '%s' ei õnnestunud: %s. Proovin CSV fallback'i.",
            table_name,
            exc,
        )
        df = _load_csv_fallback(table_name)
        if table_name == "sales":
            df = _apply_sales_date_filter(df, start_date, end_date)
        if df.empty:
            raise DataFetchError(f"Fallback andmed tabelile '{table_name}' on tühjad.")
        return df


def fetch_sales(
    start_date: str | None = None,
    end_date: str | None = None,
    use_fallback: bool = True,
) -> pd.DataFrame:
    """
    Päri müügiandmed ja tagasta DataFrame.

    Args:
        start_date: valikuline alguskuupäev formaadis YYYY-MM-DD.
        end_date: valikuline lõppkuupäev formaadis YYYY-MM-DD.
        use_fallback: kui True, loeb API vea korral datasets/sales.csv faili.
    """
    return _fetch_table_paginated("sales", start_date, end_date, use_fallback)


def fetch_customers(use_fallback: bool = True) -> pd.DataFrame:
    """Päri kliendiandmed ja tagasta DataFrame."""
    return _fetch_table_paginated("customers", use_fallback=use_fallback)


def fetch_products(use_fallback: bool = True) -> pd.DataFrame:
    """Päri tooteandmed ja tagasta DataFrame."""
    return _fetch_table_paginated("products", use_fallback=use_fallback)


def _print_test_summary(name: str, df: pd.DataFrame) -> None:
    """Prindi juhendis nõutud test: ridade arv ja .head()."""
    print(f"\n=== {name.upper()} ===")
    print(f"Ridade arv: {len(df)}")
    print(df.head())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Põhitest kasutab 2023-2024 perioodi, sest need aastad on baasis terviklikud.
    sales = fetch_sales(start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE)
    customers = fetch_customers()
    products = fetch_products()

    _print_test_summary("sales", sales)
    _print_test_summary("customers", customers)
    _print_test_summary("products", products)

    print("\n=== SALES DATE FILTER ===")
    print(f"Kasutatud periood: {DEFAULT_START_DATE} kuni {DEFAULT_END_DATE}")
