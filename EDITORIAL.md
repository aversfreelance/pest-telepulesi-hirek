# Szerkesztői válogatás

A GitHub gyűjt, az időzített asszisztens pedig a `public/news.json` találatait tartalmilag átválogatja. Ez a lépés nem indít új települési gyűjtést és nem ír vagy publikál teljes cikket a PM Online-ban.

1. Olvasd a legfrissebb GitHub-listát és annak változásait. A meglévő fájlokat ne töröld pusztán hálózati hiba miatt.
2. Kérd le a PM Online aktuális cikkjegyzékét: `https://www.pmonline.hu/api/articles-summaries`. Ez jelenleg legfeljebb 1000 rekordot ad. A cím, bevezető, település, esemény, szereplők és időpont alapján keress témabeli egyezést. A nyilvános cikkjegyzékkel nem bizonyítható minden belső piszkozat ellenőrzése. Ha a megvizsgált időszakot nem fedi le, használj további hozzáférhető archívumot, vagy tedd ellenőrzendővé a jelöltet. Hibás/üres jegyzék esetén ne állítsd, hogy megtörtént a duplikációellenőrzés.
3. Olvasd el a jelölt hír saját tartalmát; a navigáció, kapcsolódó cikkek és lábléc nem a cikk része. Ha a lényegi információ csak képen vagy csatolmányban van és nem tudod ellenőrizni, maradjon ellenőrzendő.
4. Értékeld a helyi jelentőséget, újdonságot, aktualitást és lakossági hatást. Fejlesztés, fontos döntés, jelentős szolgáltatásváltozás, helyi eredmény vagy rendkívüli esemény bekerülhet. Ne legyen automatikus kizárás pusztán a „közlemény” vagy „pályázat” szó miatt. Rutin fogadóóra, reklám, köszöntés és lejárt egyszeri tájékoztatás általában kimarad.
5. A már megírt azonos eseményt szűrd ki akkor is, ha más a címe. Érdemi új fejlemény önálló hír lehet, rövid indoklással. A bizonytalan egyezés ellenőrzendő. Az importálásra korábban átadott, még meg nem írt hír maradjon a listában ugyanazzal az azonosítóval; az id szerinti import nem készíthet új példányt.
6. Minden bemeneti id-hez rögzíts döntést a `review/decisions.json` fájlban: `include`, `review` vagy `exclude`, rövid magyar indokkal. A nyilvános döntési fájlba ne másolj belső vagy még meg nem jelent PM Online-cikket, teljes forrásszöveget, személyes adatot vagy hitelesítési adatot.
7. Futtasd a `python publish_review.py` parancsot. A PM Online bemenete kizárólag a `public/import/pmonline-news.json`. A kimenet a kért eredeti mezőket és az állandó id-t tartalmazza, teljes cikkmásolat nélkül. Az ellenőrzendő rekordok külön `public/review-required.json` fájlba kerülnek.
8. Csak a válogatás saját fájljait töltsd fel az `aversfreelance/pest-telepulesi-hirek` tárolóba, a legfrissebb ággal összeegyeztetve. Ne módosítsd a gyűjtő időzítését és ne írj a PM Online adatbázisába. Sikertelen ellenőrzésnél ne cseréld le a hitelesített importot ellenőrizetlen adatokkal.

Az első próba 10 albertirsai forrásrekordból készült; ez nem a 174 forrás teljes feldolgozása. Az automatikus gyűjtés GitHub-jogosultsági akadálya ettől külön feladat.
