# Nädal 3: SQL JOINid

## Mida ma tegin
- Minu roll sel nädalal oli leida kliendid ilma ostudeta ehk kadunud kliendid LEFT JOIN + NULL päringutega (rollb B).
- Tuvastasin, et selliseid kliente on UrbanStyle'i andmebaasis 599 ehk ligi iga viies! Kadunud kliendid moodustavad UrbanStyle'i klientidest 19% (3150).
- Uurisin, et kadunud kliendid on registreerunud aastatel 2020-2025. Kõige suurem kliendikadu on toimunud 2023. a augustis (5,2% → 21,2%)  ja 2024. a mais (36,5%).
- Esitasin turundusjuht Annale soovitusi, kuidas kliente tagasi võita võiks.
- Peamised punktid: segmenteeri kadunud kliendid, uuri, mida ütleb vanemate kontaktide kohta ettevõtte GDPR poliitika; sea eesmärk, mitu % soovid klientidst "päästa"; analüüsi, kas kadunud klientide peakidel oli käimas mingi kampaania; uuri kampaania utm_source'e ehk millised kanalid tõid kõige rohkem mitteostnud kliente; paranda klientide onboardingut.
- Osalesin meeskonna andmemaastiku koostamisel

## Peamised õpikohad
- Õppisin INNER JOIN, LEFT JOIN, RIGHT JOIN süntaksit 
- Ühendasin 3 tabelit: `sales`, `customers` ja `products`

## Individuaalsed failid
- [Minu SQL päringud](week3-ostudeta_kliendid_B-joins.sql)
- [Kadunud klientide makseviisid](week3_results_kadunud_kliendid_makseviisid.png)
- [Kadunud kliendid kuude lõikes](week3_results_kadunud_kliendid_kuud.png)
- [Kadunud kliendid registreerimisaja järgi](week3_results_kadunud_kliendid_regamisaeg.png)
- [Kadunud kliendid linnade lõikes](week3_results_kadunud_kliendid_linnad.png)
- [Kadunud kliendid](week3_results_kadunud_kliendid.png)
  
## Tiimifailid
- [Tiimi koondraport](week3_team_joins_report.md)
- [Meeskonnatöö slaidid](https://docs.google.com/presentation/d/1_XV9rattaz3KDWFpchCHEJLrqbvXODSJJUfl8Y793Mg/edit?usp=sharing)
