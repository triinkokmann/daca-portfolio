# Roll A: API Query

Minu roll on teha `data_fetcher.py` moodul, mis pärib UrbanStyle OÜ andmed Supabase API-st ja tagastab `pandas.DataFrame` objektid.

## Failid

- `data_fetcher.py` - kolm põhifunktsiooni: `fetch_sales()`, `fetch_customers()`, `fetch_products()`.
- `.env.example` - näidis, millised Supabase muutujad peavad `.env` failis olemas olema.
- `datasets/sales.csv`, `datasets/customers.csv`, `datasets/products.csv` - fallback andmed, kui Supabase ei ole kättesaadav.

## Kuidas käivitada

```bash
pip install -r requirements.txt
cp .env.example .env
# lisa .env faili päris SUPABASE_URL ja SUPABASE_KEY
python data_fetcher.py
```

Kui Supabase API võti on vale, internet puudub või Supabase on ajutiselt maas, kasutab moodul automaatselt `datasets/` kaustas olevaid CSV faile.

Töö demo kasutab müügiandmete puhul perioodi `2023-01-01` kuni `2024-12-31`, sest need aastad on baasis terviklikud. Funktsioon `fetch_sales()` toetab endiselt ka teisi kuupäevavahemikke.

## Baastaseme nõuded

- `fetch_sales(start_date, end_date)` pärib müügiandmed ja toetab kuupäevafiltrit.
- `fetch_customers()` pärib kliendiandmed.
- `fetch_products()` pärib tooteandmed.
- Kõik kolm funktsiooni tagastavad `DataFrame` objekti.
- Iga päring on try/except veakäsitlusega.
- Käsurea test prindib iga tabeli ridade arvu ja `head()` väljundi.

## Edasijõudnute nõuded

- Pagination: API-st loetakse andmed 1000 rea kaupa, kuni kõik read on käes.
- Retry loogika: ajutise API vea korral proovitakse päringut kuni 3 korda.
- Exponential backoff: korduskatsete vahel ootab kood 1s, 2s ja 4s.
- Fallback: Supabase vea korral loetakse andmed CSV failidest, et pipeline ei jääks seisma.

## AI kasutamine

AI aitas muuta A-osa tootmisvalmimaks: lisasin pagination'i, retry exponential backoff'iga, selge veakäsitluse ja CSV fallback'i. Samuti aitas AI struktureerida koodi nii, et seda saab meeskonna `pipeline.py` failis otse importida.
