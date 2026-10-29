# Pest vármegye települési hírlistája

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
