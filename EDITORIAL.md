# Szerkesztői válogatás

## Aktuális működés: napi lista, kiválasztás a PM Online-ban

A felhasználó a kézi kiválasztást (cherry picking) és elutasítást/törlést a PM Online-ban szeretné végezni. Az alábbi régi szerkesztői válogatási eljárást az új napi bemenetnél NE futtasd: a hírérték alapján ne távolíts el híreket a napi listából, és ne kezeld a korábbi próbadöntéseket a felhasználó döntéseiként.

A GitHub nyers hírlistájából a `python prepare_daily.py` készíti a `public/import/pmonline-daily.json` egyszerű importlistát. Alapértelmezésben a magyar helyi napon **megjelent** hírekből dolgozik; a forrás közzétételi napja számít. A `public/daily/YYYY-MM-DD.json` napi fájl és a `public/daily-by-settlement.json` csoportosított nézet is elkészül. A napi fájl az adott nap legfrissebb, még nem kezelt listája, nem változtathatatlan pillanatfelvétel. Üres lista önmagában nem bizonyítja, hogy minden forrást sikerült ellenőrizni: a `public/daily-status.json` mutatja a gyűjtés és a PM Online-állapot ismert frissességét.

A PM Online kiválasztási és törlési döntéseit a `review/pmonline-actions.json` őrzi: `version: 1`, `updatedAt`, `selectedIds`, `deletedIds`. A kiválasztott és a törölt rekordok azonosítója tartósan maradjon meg, akkor is, amikor az eredeti hír már nincs a napi listában. A hír felületről való eltüntetése nem jelentheti az elutasítási emlékezet törlését. Visszaállításhoz a PM Online-nak az adott id-t ki kell vennie a megfelelő döntési listából. A fájl csak azonosítókat és technikai frissítési időpontot tartalmazzon, belső cikket és felhasználói adatot ne.

Az állapotfájl induló értéke üres, `updatedAt: null`: **a PM Online-ból történő automatikus visszaírás még nincs bekötve**. Ezt ne állítsd működőnek. Hiteles új állapotot ne találj ki, és meglévő valódi döntéseket ne írj felül üres mintával. Az állapot a PM Online-ból ellenőrzött exporttal vagy később hitelesített háttérkapcsolattal érkezhet. GitHub-hozzáférési kulcs ne kerüljön böngészős kódba.

Azonos id egy napi listában csak egyszer szerepel. Eltérő id-jú, de azonos témájú híreket lehet jelezni ellenőrzésre településenként és térségi szinten, de a végső választást a felhasználó végzi. A korábban megírt témák vizsgálatának ismert korlátai továbbra is érvényesek.

Időzített feladatként frissítsd a GitHub-bemenetet és a hiteles PM Online-állapotot, készítsd el és töltsd fel a napi kimeneteket. Ne indíts új települési gyűjtést és ne írj a PM Online adatbázisába. Csak a saját napi kimeneti fájlokat töltsd fel, a közben érkező változásokkal összeegyeztetve. A gyűjtés korábbi GitHub workflow-jogosultsági akadályát ne állítsd megoldottnak.

## Korábbi, automatikus szerkesztői próba – háttéranyag

A GitHub gyűjt, az időzített asszisztens pedig a `public/news.json` találatait tartalmilag átválogatja. Ez a lépés nem indít új települési gyűjtést és nem ír vagy publikál teljes cikket a PM Online-ban.

1. Olvasd a legfrissebb GitHub-listát és annak változásait. A meglévő fájlokat ne töröld pusztán hálózati hiba miatt.
2. Kérd le a PM Online aktuális cikkjegyzékét: `https://www.pmonline.hu/api/articles-summaries`. Ez jelenleg legfeljebb 1000 rekordot ad. A cím, bevezető, település, esemény, szereplők és időpont alapján keress témabeli egyezést. A nyilvános cikkjegyzékkel nem bizonyítható minden belső piszkozat ellenőrzése. Ha a megvizsgált időszakot nem fedi le, használj további hozzáférhető archívumot, vagy tedd ellenőrzendővé a jelöltet. Hibás/üres jegyzék esetén ne állítsd, hogy megtörtént a duplikációellenőrzés.

   **Településenkénti ellenőrzés:** csoportosítsd a forráshíreket a `location`, a PM Online-cikkeket a `city` és a tartalomban ténylegesen érintett települések alapján. Először az azonos településen belüli gyűjtött hírek egyezéseit, majd az adott település már megírt cikkeit ellenőrizd. A neveknél hagyd figyelmen kívül a kis-/nagybetűt, a fölösleges szóközöket és a Unicode írásmód eltéréseit, de ne mosd össze a különböző településeket. Egy több települést érintő cikk minden érintett település összevetésében szerepeljen. Az üres `city` mező nem bizonyítja, hogy nincs helyi vonatkozás: vizsgáld a címet és bevezetőt is.

   Ezután legyen **települések közötti közös témavizsgálat** is: ugyanaz a térségi útlezárás, beruházás vagy más közös esemény ne kerüljön be többször. A puszta címhasonlóság nem elég a kizáráshoz; a helyszín, időpont, szereplők és konkrét történés egyezzen. Különböző napi áramszünetek vagy hasonló nevű, de különálló beruházások nem automatikus duplikációk. Biztos ismétlésnél válaszd az elsődleges, legrészletesebb forrást, és rögzítsd a többi rekord kizárási okát. A csoportosítás nem pótolja a hiányzó archívumot.
3. Olvasd el a jelölt hír saját tartalmát; a navigáció, kapcsolódó cikkek és lábléc nem a cikk része. Ha a lényegi információ csak képen vagy csatolmányban van és nem tudod ellenőrizni, maradjon ellenőrzendő.
4. Értékeld a helyi jelentőséget, újdonságot, aktualitást és lakossági hatást. Fejlesztés, fontos döntés, jelentős szolgáltatásváltozás, helyi eredmény vagy rendkívüli esemény bekerülhet. Ne legyen automatikus kizárás pusztán a „közlemény” vagy „pályázat” szó miatt. Rutin fogadóóra, reklám, köszöntés és lejárt egyszeri tájékoztatás általában kimarad.
5. A már megírt azonos eseményt szűrd ki akkor is, ha más a címe. Érdemi új fejlemény önálló hír lehet, rövid indoklással. A bizonytalan egyezés ellenőrzendő. Az importálásra korábban átadott, még meg nem írt hír maradjon a listában ugyanazzal az azonosítóval; az id szerinti import nem készíthet új példányt.
6. Minden bemeneti id-hez rögzíts döntést a `review/decisions.json` fájlban: `include`, `review` vagy `exclude`, rövid magyar indokkal. A nyilvános döntési fájlba ne másolj belső vagy még meg nem jelent PM Online-cikket, teljes forrásszöveget, személyes adatot vagy hitelesítési adatot.
7. Futtasd a `python publish_review.py` parancsot. A PM Online bemenete kizárólag a `public/import/pmonline-news.json`. A kimenet a kért eredeti mezőket és az állandó id-t tartalmazza, teljes cikkmásolat nélkül. Az ellenőrzendő rekordok külön `public/review-required.json` fájlba kerülnek.

   A program külön települési csoportokat is kiír: `public/news-by-settlement.json` (gyűjtött hírek), `public/import/pmonline-news-by-settlement.json` (kiválasztott hírek), `public/review-required-by-settlement.json` (ellenőrzendők). Ezek alakja `[{"location": "Albertirsa", "news": [...]}]`. Az alap importlista egyszerű JSON-tömb marad, településenként rendezve. A fájlok csoportosítása önmagában nem tartalmi duplikációszűrés; ezt a fenti szerkesztői összevetés végzi.
8. Csak a válogatás saját fájljait töltsd fel az `aversfreelance/pest-telepulesi-hirek` tárolóba, a legfrissebb ággal összeegyeztetve. Ne módosítsd a gyűjtő időzítését és ne írj a PM Online adatbázisába. Sikertelen ellenőrzésnél ne cseréld le a hitelesített importot ellenőrizetlen adatokkal.

Az első próba 10 albertirsai forrásrekordból készült; ez nem a 174 forrás teljes feldolgozása. Az automatikus gyűjtés GitHub-jogosultsági akadálya ettől külön feladat.
