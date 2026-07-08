# Nädal 2: SQL ja tooteandmete puhastamine

## Mida ma tegin
- Minu roll oli müügiandmete puhastamine (roll A)
- Lõin `sales_test` tabeli, mida uurisin SQL päringutega
-  Osalesin meeskonna andmemaastiku koostamisel

## Peamised leiud & õpikohad
- Selgus, et tabelis on 5116 duplikaatset rida ja 5008 probleemi
- Lahendasin probleemid ja kustutasin duplikaadid
- Koostasin SQL päringute abil `sales_test` tabeli puhastamisraporti
- Õppisin SQL cleaning loogikat tundma: DELETE, UPDATE, COALESCE, CASE WHEN 
- Kirjutasin puhastamisskripti: duplikaadid, NULL-id, kuupäevad, negatiivsed väärtused

## Äriline väärtus
5116 duplikaatset rida tähendab, et müügiraport näitas valet ehk liiga suurt käivet. Kui keegi teeks ärisoovituse selle andmestiku põhjal, planeeriks ta laovaru, hinnakirja või kampaaniat vale aluse pealt. 

## Kuidas ma kasutasin AI-d?
Kasutasin AI-d päringute täpsustamiseks ja järelduste ideede põrgatamiseks. Olen avastanud, et Claude on selleks parim.

## Individuaalsed failid
- [Minu SQL päringud](individual/week2_A_sales_cleaning.sql)

## Tiimifailid
- [Tiimi koondraport](team/week2_team_cleaning_report.md)
- [Meeskonnatöö slaidid](https://docs.google.com/presentation/d/1A8KvN7d0f7EDag7m9cagzEe5bE2fw8dw/edit?usp=sharing&ouid=114154652828264470790&rtpof=true&sd=true)
