MEESKOND: TOODE |  NÄDAL: 2  |  TEGELANE: Toomas Kask    │
│                                                              
│  ANDMEKVALITEEDI KOONDRAPORT                                                                                               │
│  PEAMISED LEIUD:                                             
│  1. Triin, müügiandmete puhastaja: leitud 5508 probleemi —  korduvad sale_id väärtused (4018), NULL customer_id (1487), tulevikukuuäpäevad (8) eemaldatud. Alles jäi 988 NULL sales_id ehk külalisostu.    
│  2. Jörgen, kliendiandmete puhastaja: leitud 513 probleemi — [128 duplikaatset emaili, 380 NULL väärtusega emaili. Erineva formaadiga linnade arv oli 54, update käsklusega uuendades jäi alles 12 erinevat linna.     
│  3. Sirja, tooteandmete puhastaja: leitud 12 probleemi — duplikaatsed tootenimed.      
│  4. Tuuli, kvaliteedikontrollija: leitud 2396 probleemi — 1487 müüki viitab “olematule kliendile” (IS NULL), 305 juhtu, kus müügihind ja tootehind ei klapi, 592 klienti pole kunagi ostu sooritanud, 12 toodet pole kunagi müüdud.   
│                                                             
│  SUURIM ÜLLATUS:                                             
│  Müügitabeli suur duplikaatide arv, linnade nimekujude lai variatsioon, samas positiivne üllatus, et mõnedes veergudes ei leitud üldse vigu (eriti products tabelis).
                                                                                                               
│  SOOVITUS TOOMASELE:                                         
│  Vaadata üle andmesisestuse loogikad, et tulevikus duplikaate ja vigaseid andmeid vältida. Oleks tarvis ühtset andmesüsteemi.      
│                                                              
│  PUUDUVAD ANDMED:                                            
│  Miinusega summad - kas need on tagastused, sisestusvead, tühistatud ost vms. Tuleks uurida, millega tegemist. Need vajavad eraldi ärireeglite kontrolli. Kas NULL väärtusega kliendiviited ikkagi on kõik külalisostud? 
