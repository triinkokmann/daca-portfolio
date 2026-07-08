# Nädal 3: SQL JOINid

## Mida ma tegin
- Minu roll sel nädalal oli leida kliendid ilma ostudeta ehk kadunud kliendid LEFT JOIN + NULL päringutega (rollb B).
- Osalesin meeskonna andmemaastiku koostamisel

## Peamised leiud & õpikohad
- Tuvastasin, et selliseid kliente on UrbanStyle'i andmebaasis 599 ehk ligi iga viies! Kadunud kliendid moodustavad UrbanStyle'i klientidest 19% (3150).
- Uurisin, et kadunud kliendid on registreerunud aastatel 2020-2025. Kõige suurem kliendikadu on toimunud 2023. a augustis (5,2% → 21,2%)  ja 2024. a mais (36,5%).
- Õppisin INNER J OIN, LEFT JOIN, RIGHT JOIN süntaksit 
- Ühendasin 3 tabelit: `sales`, `customers` ja `products`

## Äriline väärtus
19% klientidest pole kunagi ostu sooritanud — see on otsene tulupotentsiaal, mis seisab kasutamata. 599 "kadunud" klienti on juba usaldanud ettevõtet piisavalt, et registreeruda, kuid midagi katkestas ostutee. August 2023 ja mai 2024 kliendikao tipud viitavad konkreetsetele sündmustele (kampaania, konkurent, tooteprobleem) — see on uurimist väärt, mitte lihtsalt statistika. Tagasivõitmiskampaania isegi 20% neist klientidest on odavam kui samapalju uusi kliente hankida.

## Soovitused turundusjuht Annale
- Segmenteeri kadunud kliendid: uuri, mida ütleb vanemate kontaktide kohta ettevõtte GDPR poliitika
- Sea eesmärk, mitu % soovid klientidst "päästa"
- Snalüüsi, kas kadunud klientide peakidel oli käimas mingi kampaania
- Uuri kampaania utm_source'e ehk millised kanalid tõid kõige rohkem mitteostnud kliente
- Paranda klientide onboardingut.

## Individuaalsed failid
- [Minu SQL päringud](individual/week3-ostudeta_kliendid_B-joins.sql)
- [Kadunud klientide makseviisid](individual/week3_results_kadunud_kliendid_makseviisid.png)
- [Kadunud kliendid kuude lõikes](individual/week3_results_kadunud_kliendid_kuud.png)
- [Kadunud kliendid registreerimisaja järgi](individual/week3_results_kadunud_kliendid_regamisaeg.png)
- [Kadunud kliendid linnade lõikes](individual/week3_results_kadunud_kliendid_linnad.png)
- [Kadunud kliendid](individual/week3_results_kadunud_kliendid.png)
  
## Tiimifailid
- [Tiimi koondraport](team/week3_team_joins_report.md)
- [Meeskonnatöö slaidid](https://docs.google.com/presentation/d/1_XV9rattaz3KDWFpchCHEJLrqbvXODSJJUfl8Y793Mg/edit?usp=sharing)
