# Aktív és felhasznált hírlista

Az összehasonlításnak pontosan két állomány az alapja:

- public/active.json: még feldolgozásra váró hírek; ez a PM Online állandó importcíme.
- public/used.json: már felhasznált/lezárt hírek emlékezete. A törölt/elutasított tételek is itt maradjanak, ha nem szabad újra felajánlani őket.

Nem kell és nem szabad lekérni a PM Online megjelent cikkeit, API-ját vagy archívumát a duplikációszűréshez. A régi review/pmonline-actions.json és review/decisions.json nem az aktuális összevetés alapja.

## Frissítés

1. Frissítsd biztonságosan az aversfreelance/pest-telepulesi-hirek checkoutot a main ágról. A gyűjtést a GitHub végzi; ne indíts új települési gyűjtést.
2. Olvasd a public/news.json találatait és a legfrissebb aktív és felhasznált fájlt. Hiányzó vagy hibás állapotnál állj meg; ne kezeld üres előzményként.
3. Futtasd a python prepare_daily.py parancsot. A magyar helyi napon megjelent találatokat állandó id és követőkódoktól megtisztított teljes hír-URL alapján ellenőrzi mindkét listában. Ami egyikben sincs, az aktívhoz adódik. A korábbi függő aktív tételek másnap is megmaradnak. Ha mindkét listában szerepel valami, a felhasznált állapot elsőbbséget kap.
4. A public/import/pmonline-daily.json az adott futás új tételeit tartalmazza. A public/daily/YYYY-MM-DD.json az aznapi legutóbbi futás új tételei, nem változtathatatlan teljes napi archívum. Az állandó teljes munkalista az active.json.
5. Ellenőrzés után csak a saját aktív/napi/státusz változásaidat töltsd fel. Ha a távoli aktív vagy felhasznált lista közben változott, frissíts és futtasd újra az összevetést; soha ne kényszeríts felülírást. A program a felhasznált fájlt nem módosítja.

A kiválasztás/felhasználás és az elutasítás/törlés a PM Online-ban történik. Feldolgozáskor a rekord kerüljön át az aktívból a felhasználtba. A törlés ne törölje a hír azonosítóját az emlékezetből, mert akkor visszakerülhetne. Az állapotátvitel visszakötése a PM Online-ból még nincs kész; ne állítsd működőnek, és ne találj ki felhasználói döntéseket. A két új fájl induláskor üres; a korábbi szerkesztői próbadöntések nem felhasználói döntések.

Ne szűrj ki hírt pusztán hírérték vagy címhasonlóság alapján; a végső kiválasztást a felhasználó végzi. Ne publikálj teljes cikket vagy belső tartalmat, ne írj a PM Online adatbázisába, és ne vezess be fizetős szolgáltatást. A GitHub-gyűjtő workflow-jogosultsági akadálya továbbra is külön feladat. Üres napi lista hiányos gyűjtés mellett nem bizonyít hírmentes napot.
