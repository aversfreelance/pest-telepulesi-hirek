# JSON-import leírása

## Letöltés

Állandó cím:
https://raw.githubusercontent.com/aversfreelance/pest-telepulesi-hirek/main/public/import/news.json

Az egész dokumentum egy JSON-tömb, nincs körülötte adatcsomagoló objektum. A szöveg UTF-8, BOM nélkül. A hiányzó kép és időpont JSON null, a képjelző valódi boolean. Üres találatlista: [].

## Mezők

- id: állandó hír-azonosító. Ismételt beolvasásnál ez alapján frissíts, ne készíts új példányt.
- location: település neve.
- sourceName: a forráshonlap neve.
- url: a konkrét hír teljes http/https címe. A fogadó felület ebből készíthet kattintható linket.
- sourceUrl: ugyanaz a hír-URL, az ajánlók meglévő mezőnevéhez igazodva.
- title: a forráshír címe.
- date: megjelenési nap, YYYY-MM-DD.
- time: megjelenési idő, HH:mm, vagy null, ha a forrás nem adja meg. Időzónát tartalmazó forrásidőnél a magyar helyi időt használjuk.
- hasImage: true vagy false.
- image: a forrás által jelzett cikkép teljes címe, vagy null.
- excerpt: rövid szerkesztői összefoglaló.
- newsCategory: téma, például kozlekedes, egeszsegugy vagy oktatas.
- newsReason: rövid magyar indok, amiért a találatot hírértékűnek ítéltük.
- collectedAt: ha rendelkezésre áll, a gyűjtés időpontja ISO-formátumban. Ez nem a megjelenés ideje.

A fájl metaadatokat és rövid összefoglalót ad, nem kész, publikált cikket. A forráskép URL-je információ a képről; a kimenet nem tölti le és nem másolja át a képet.

## Felhasznált és elutasított tételek visszaadása

A kezelt állomány külön JSON-tömb: public/used.json. Az exportált kezelt rekordnál legalább az eredeti id maradjon meg; a teljes hír-URL (url vagy sourceUrl) megőrzése is ajánlott. Így megváltozott id mellett is felismerhető ugyanaz a hír. A rekordhoz hozzáadható:

- usageStatus: used (felhasznált) vagy discarded (kuka/elutasított).
- handledAt: a felhasználói döntés ISO-időpontja.

Mindkét állapot kizárja az újbóli ajánlást. A törlés nem jelentheti a kezelt azonosító elfelejtését. Új exportnál a teljes korábbi kezelt előzmény maradjon meg, ne csak az aznapi döntések. A used.json fájl nem tartalmazhat belső cikket, hozzáférési kulcsot vagy felhasználói adatot.

A fogadó rendszer döntései csak akkor jutnak vissza a gyűjtőhöz, ha a használt export a public/used.json fájlba kerül. Ezt a visszaadást ennek a projektnek nincs joga a PM Online módosításával megvalósítani. A fogadó rendszer a saját kezelt azonosítóival is szűrje a beolvasást, amíg a GitHub-fájl frissítése meg nem történik.

## Ellenőrzés

A python export_import.py az aktív és kezelt állományból előállítja az importfájlt. Az ismert id-ket és azonos, követőkódoktól megtisztított hír-URL-eket kihagyja. Ellenőrzi a kötelező mezőket, URL-eket, dátumot, időt és a képjelző egyezését. A rekordok településenként rendezve szerepelnek, de az import egyetlen egyszerű tömb.

A napi automatikus gyűjtés még nincs engedélyezve; a rendelkezésre álló valódi induló válogatás 26 hír. A hírérték szerinti új értékelés után a prepare_daily.py az importot automatikusan újra előállítja.
