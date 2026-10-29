# Pest vármegye települési hírlistája

## Aktuális működés: aktív és felhasznált

A PM Online állandó importcíme: `public/active.json`. A feldolgozott vagy elutasított hírek nyilvántartása: `public/used.json`. Mindkettő egyszerű JSON-lista a hírmetaadatokkal és az állandó azonosítóval.

A `python prepare_daily.py` a magyar helyi napon megjelent új találatot csak akkor adja az aktívhoz, ha az id-ja és a megtisztított hír-URL-je egyik listában sem szerepel. A függő aktív hírek másnap is megmaradnak. Az összehasonlítás nem olvassa a PM Online cikkeit. A felhasznált listát a gyűjtő nem írja át.

Felhasználáskor vagy végleges elutasításkor a PM Online-nak át kell mozgatnia a rekordot az aktívból a felhasználtba. Ennek visszakötése még nincs kész. A `public/import/pmonline-daily.json` csak az adott futásban hozzáadott új tételek listája. Az induló két állomány üres; a mai próba nem tartalmaz mai megjelenésű hírt.

## Korábbi megoldások – az aktuális munkamenethez az active.json használandó

### Korábbi napi import és kézi kiválasztás

A jelenlegi javasolt PM Online-bemenet: `public/import/pmonline-daily.json`. Egyszerű JSON-lista, a magyar helyi napon megjelent, még nem kiválasztott és nem törölt hírekkel. A napi archív fájl `public/daily/YYYY-MM-DD.json`, a döntések külön `review/pmonline-actions.json` fájlba kerülnek. Előkészítés: `python prepare_daily.py`.

A kiválasztást és törlést a felhasználó végzi a PM Online felületén. Az elutasítások azonosítóit meg kell őrizni, hogy a következő import ne hozza vissza a törölt híreket. A jelenlegi állapotfájl üres minta, a PM Online-ból való visszaírás még nincs bekötve. A napi állapotot a `public/daily-status.json` mutatja; üres napi lista hiányos gyűjtés mellett nem bizonyítja, hogy aznap nem volt hír. A korábbi, két rekordos szerkesztői importfájl megmarad próbaanyagként; a napi munkához az új címet kell használni.

Önálló, nyilvános GitHub-tároló, fizetős szolgáltatás nélkül. A program a 174 korábban aktívnak talált forrásból gyűjt hírmetaadatokat. A forráslista nem jelent 174 hibátlanul feldolgozható weboldalt: az ellenőrzés eredménye a `public/status.json` fájlban látható, a `needs_review` és `error` állapotú források további beállítást igényelnek.

## PM Online bemenet

A `public/news.json` egy egyszerű JSON-lista, a sport- és programajánló mezőneveihez igazítva:

- `id`: állandó azonosító, az ismételt import frissítse ezt a rekordot.
- `location`: település.
- `sourceName`: honlap neve.
- `url`, `sourceUrl`: a konkrét hír teljes internetes címe.
- `title`: hír címe.
- `date`: a forrás szerinti megjelenési nap, `YYYY-MM-DD`.
- `time`: a forrás szerinti megjelenési idő, `HH:mm`, időpont nélkül `null`.
- `hasImage`: talált-e a gyűjtő a hírhez használható képet.
- `image`: a talált kép teljes címe, vagy `null`.

A JSON-ban az URL szöveg; kattintható linket a PM Online felülete jelenít meg belőle. A képfelismerés a honlap által jelölt cikkképet vizsgálja; a logókat, sablonképeket kiszűri, de a változatos oldalak miatt szerkesztői ellenőrzés indokolt. A lista nem tartalmaz átvett teljes cikkeket.

## Frissítés és import

A GitHub Actions naponta 07:17 és 17:17 órakor, magyar helyi idő szerint fut, és kézzel is indítható. Az időzített indítás GitHub-terhelés miatt késhet. A szabványos futtatók nyilvános tárolóban ingyenesek. A GitHub inaktív nyilvános tárolók időzítését leállíthatja; a futásokat figyelni kell.

A gyűjtő az utóbbi 31 nap dátummal ellátott híreit tartja meg. Hibás vagy elérhetetlen forrás esetén a korábbi, még ebbe az időablakba eső hírek megmaradnak. A dátum nélküli oldalak kimaradnak, az időpontot nem találja ki. Legfeljebb 20 cikkjelöltet ellenőriz forrásonként és futásonként; ez nem teljes archívumletöltés.

A PM Online a GitHub nyers `public/news.json` címét olvassa, és `id` alapján beszúr/frissít. Az ajánló meglévő importálójának formáját követjük, de ez **hírlista**, ezért külön hírimport-mezőillesztés szükséges; a tároló elkészítése önmagában nem kapcsolja be a PM Online automatikus importját.

## Helyi ellenőrzés

```sh
pip install -r requirements.txt
python -m unittest discover -s tests
python collect.py
```

Egy rövid próba: `python collect.py --limit 3`. Az aktuális állapot és hibák a `public/status.json` fájlba kerülnek. Teljes gyűjtési hiba esetén a program hibával leáll, a korábbi hírlistát nem írja felül.
