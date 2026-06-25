# Week 8 Pipeline Demo — UrbanStyle

## Eesmärk

Meeskonna eesmärk oli muuta UrbanStyle OÜ iganädalane käsitsi analüüs automaatseks Python pipeline'iks.

Pipeline teeb neli sammu:

1. Extract — pärib andmed Supabase API-st.
2. Transform — puhastab andmed ja arvutab KPI-d.
3. Visualize — loob graafikud.
4. Export — salvestab CSV ja HTML väljundid.

## Rollid

- Roll A, Sirja: API Query — `data_fetcher.py`
- Roll B, Jörgen: Data Processing — `transform.py`
- Roll C, Tuuli: Visualization + Saving — `visualize_export.py`
- Roll D, Triin: Automation Script — `pipeline.py`

## Käivitamine

```bash
python pipeline.py
```

## Demo Väljund

Pipeline jooksis edukalt läbi:

```text
URBANSTYLE ETL PIPELINE
ETAPP 1: EXTRACT OK
ETAPP 2: TRANSFORM OK
ETAPP 3: VISUALIZE OK
ETAPP 4: EXPORT OK

PIPELINE LÕPETATUD
Aeg: 5.5s
Käive: 2,691,235.81 EUR
Kliente: 2464
AOV: 287.80 EUR
CSV: output/pipeline_results_YYYYMMDD_HHMMSS.csv
```

## Loodud Failid

Pipeline salvestab tulemused `output/` kausta:

- `pipeline_results_YYYYMMDD_HHMMSS.csv`
- `weekly_revenue_YYYYMMDD_HHMMSS.html`
- `kpi_summary_YYYYMMDD_HHMMSS.html`

## Peamine Järeldus Markole

2023-2024 puhastatud andmete põhjal oli UrbanStyle kogukäive umbes 2.69 miljonit eurot, unikaalseid kliente oli 2464 ja keskmine tellimuse väärtus oli 287.80 eurot.

## Mis Otsus Selle Põhjal Muutub?

Iganädalast müügiülevaadet ei pea enam käsitsi koostama. Sama töövoog saab käia ühe käsuga ning tulemused on kohe CSV ja HTML kujul jagatavad.

## Mis Juhtub, Kui Supabase On Maas?

Pipeline proovib kõigepealt Supabase API-st andmeid pärida. Kui API ei vasta, kasutab `datasets/` kaustas olevaid CSV fallback-faile.

## Edasijõudnute Elemendid

- Pagination suurte API tabelite jaoks.
- Retry loogika API tõrgete korral.
- CSV fallback Supabase tõrke korral.
- Failipõhine logging `logs/` kausta.
- Konfiguratsioon `config.yaml` failis.

## AI Kasutamine

AI aitas kontrollida moodulite omavahelist sobivust, leida veerunimede erinevusi B ja C osa vahel, parandada pagination'i loogikat ning muuta pipeline'i terminaliväljund demo jaoks selgemaks.
