# Nädal 4: SQL agregatsioonid

## Mida ma tegin
- Minu roll sel nädalal oli uurida analüüsida inventuuristatstikat - analüüsin tootekategooriaid, laoseisu ja müüdud vs laos suhteid. Kasutasin GROUP BY, HAVING ja window funktsioone, et leida probleemsed kategooriad. 
- Avastasin, et kõige kasumlikum kategooria on jalanõud, mis moodustab 26,3%-ga üle veerandi ettevõtte kogukäibest. 
- Kõrgeima kasumimarginaaliga on küll aksessuaarde müük (33,6%), kuid nende müügimaht on võrreldes teistega väike. 
- Tähelepanu vajavad 12 toodet, mida pole kunagi müüdud. Samuti madala keskmise müügiga naisteriiete kategooria. 
- Tootekategooriate TOP 3 toodete müük on suhteliselt ühtlane, mis tähendab, et müük on hästi hajutatud, kategooriate vahel ei ole suuri kääre. Ettevõte ei sõltu ühest-paarist "supertootest". Riskid on hajutatud.
- Soovitaks Urbanstyle'il vaada üle ja kitsendada tooteportfelli ning turunduskampaaniates panustada hästi müüvatele kategooriatele, jalanõud ja meesteriided. 


## Peamised õpikohad / kuidas kasutasin AI-d
- Arendasin ärilist mõtlemist, kuidas oma andmete illustreerimiseks kasutada diagramme. Valisin õige diagrammi - tulpdiagrammi koos tootekategooriate käibe, kulude ja kasumi illustreerimiseks ning joondiagrammi kasumimarginaali lisamiseks.
- Kasutasin GROUP BY, HAVING, COUNT, SUM, AVG, CTE päringuid 
- Arvutasin KPI-d ja tegin varude auditi: tuvastatud ~40 anomaaliat 
- Kasutasin oma sisendi põhjal Claude'i diagrammi visualiseerimiseks, samuti pikemate päringute kirjutamise ja ülevaatamise abistamiseks ning kvaliteedikontrolliks. 

## Individuaalsed failid /individual
- [Minu SQL päringud](individual/week4_inventuuristatistika_aggregation.sql)

## Tiimifailid
- [Tiimi koondraport](team/week4_team_aggregation_report.md)
- [Meeskonnatöö slaidid](https://docs.google.com/presentation/d/1d_Kse5csm-8SxNL4vULd8zEjzDnpZsU9GCmHDmwn1n0/edit?usp=sharing)
