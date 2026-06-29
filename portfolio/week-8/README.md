# Nädal 8: Python, API-d ja ETL-pipeline

## Mida ma tegin
- Minu roll sel nädalal oli Roll D: Automation Script — kirjutasin pipeline.py, mis orkestreerib meeskonna nelja rolli üheks terviklikuks ETL pipeline'iks.
- Pipeline ühendab rollid A, B ja C kindlas järjekorras: Extract → Transform → Visualize → Export, ning seda käivitatakse ühe käsuga: python pipeline.py

### Peamised leiud & õpikohad / AI kasutamine
- ETL arhitektuur — pipeline.py ise ei sisalda äriloogikat, vaid kutsub õiges järjekorras välja teiste rollide funktsioonid. See tähendab, et kui Roll B muudab midagi, piisab muudatusest transform.py-s — pipeline.py jääb samaks.
- Veakäsitlus astmeliselt — Extract etapis on kaheastmeline fallback: esmalt proovib Supabase API-d, ebaõnnestumise korral laeb kohalikud CSV failid. Transform etapp peatab pipeline'i ja saadab teavituse, Visualize etapp aga lubab jätkata ka vea korral (CSV eksport on oluline, diagramm mitte).
- Logimine — kõik etapid kirjutavad logid logs/pipeline_YYYYMMDD.log faili koos kellaaegadega, et hiljem saaks täpselt näha, mis hetkel mingi probleem tekkis.
- Konfiguratsioon — kuupäevavahemik ja väljundkaust on config.yaml failis, mitte koodis hardcoded — parameetreid saab muuta ilma koodi puutumata.
- Turvalisus — API URL ja võti on .env failis — need ei lähe koodi ega GitHubi. Repos on ainult .env.example näidis tühjade väärtustega.
- Claude aitas koodi kirjutada, läbi mõelda Pipeline'i struktuuri. Selgitas, miks logging.basicConfig peab kutsuma enne moodulite importimist (Python initsialiseerib logimise esimesel kutsel, hiljem ei saa enam muuta).

## Individuaalsed failid
- [Pipeline](individual/pipeline.py)

## Tiimifailid
[Meeskonna tervilik pipeline'i demo ja tulemused](team/week8_pipeline_demo.md)
