# Importálható települési hírlista

## Közvetlen JSON-cím

https://raw.githubusercontent.com/aversfreelance/pest-telepulesi-hirek/main/public/import/news.json

Ez az egyetlen ajánlott importcím. Egyszerű UTF-8 JSON-listát ad, településenként rendezve. A rekordok a hírérték szerint kiválasztott aktív hírek; a felhasznált vagy elutasított tételek kimaradnak.

A mezők leírása és a kezelt állomány formátuma: IMPORT.md.

## Működés

- public/news.json: a települési honlapokról gyűjtött nyers hírek.
- review/newsworthiness.json: a tartalmi értékelés, rövid magyar indoklással.
- public/active.json: még feldolgozásra váró, kiválasztott hírek.
- public/used.json: felhasznált és elutasított hírek tartós nyilvántartása.
- public/import/news.json: ellenőrzött, importálható kimenet.

Az első gyűjtés hét napot tekintett át. Utána csak az adott magyar helyi napon megjelent találatok kerülhetnek hozzáadásra. A korábbi függő aktív hírek megmaradnak. A duplikációszűrés kizárólag az aktív és kezelt állományhoz hasonlít, azonosító és megtisztított teljes hír-URL alapján.

A felhasználó a fogadó rendszerben választja ki vagy utasítja el a hírt. Az ott feldolgozott tételekről külön used.json exportot kell visszaadni ennek a tárolónak; amíg ez nem történik meg, a gyűjtő nem tud az ottani döntésekről. Ez a projekt kizárólag JSON-t állít elő, a fogadó rendszer kódját és adatait nem módosítja.

## Ütemezés állapota

A reggeli gyűjtésre kész beállítás: setup/collect.yml. A tervezett indítás 07:17, Europe/Budapest idő szerint. GitHub workflow-ként még engedélyezni kell; a jelenlegi kapcsolathoz hiányzik a workflow-jogosultság, ezért ez az automatikus gyűjtés még nem aktív.

A hírértéket értékelő helyi feladat naponta egyszer fut 09:15-kor magyar idő szerint. Ehhez működő gép és alkalmazás kell; külön fizetős AI API nincs. A 174 forrás feldolgozhatóságának tényleges állapotát a public/status.json mutatja. Az első teljes ellenőrzés 50 forrásból tudott friss hírt kinyerni; a többi további ellenőrzést igényel.

## Helyi használat

pip install -r requirements.txt
python -m unittest discover -s tests
python export_import.py

Új értékelt találatok hozzáadásához: python prepare_daily.py. Ez az exportot is frissíti. Az export ellenőrzi az adatokat, és hibás aktív/kezelt fájl esetén nem írja felül a korábbi importfájlt.

## Határ

A PM Online kódjához, GitHub-tárolójához, tárhelyéhez, adatbázisához vagy API-jához ebből a feladatból tilos hozzányúlni. A fogadó oldali fejlesztést a felhasználó külön, Cursorban végzi. A korábbi ilyen fejlesztés vissza lett vonva, a próbaoldal törölve lett.
