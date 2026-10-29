# Reggeli települési hírgyűjtés és szerkesztői válogatás

## A teljes menet

1. A GitHub Actions minden reggel 07:17-kor, magyar helyi idő szerint lekéri a sources.json települési honlapjait. Az első teljes futás az utóbbi hét napot keresi, később csak az aznap megjelent híreket. Kézi javító futásnál a --days kapcsolóval visszamenőleges ablak adható meg.
2. Az időzített asszisztens 09:15-kor magyar idő szerint átnézi az új nyers találatokat, tényleges tartalom alapján értékeli a hírértéket. Ez helyi alkalmazásban futó feladat: a gépnek és az alkalmazásnak működnie kell. Nem használ fizetős AI API-t, de az előfizetés használati keretét fogyasztja.
3. A hírértékű találat csak akkor kerül az active.json fájlba, ha az aktív és a kezelt used.json fájlban sincs még benne. Összevetés: állandó id és követőkódoktól megtisztított teljes hír-URL. A PM Online már megjelent cikkeihez NEM hasonlítunk.
4. A PM Online külön /admin/hirlista oldalán településenként, kereshetően jelenik meg az aktív lista. A Felhasználom gomb a cím, bevezető, település és forráslink alapján szerkeszthető piszkozatot készít. Nem élesít cikket, és a külső képet nem veszi át automatikusan.
5. Felhasználás és kuka esetén a tétel egy GitHub-mentésben átkerül az aktívból a kezelt fájlba. A kezelt fájlban a used és discarded állapot egyaránt megmarad. Félbeszakadt piszkozatkészítés preparing állapotban újrapróbálható, ugyanazzal a piszkozat-azonosítóval.

## Fájlok

- public/news.json: nyers gyűjtés, nem közvetlen szerkesztői ajánlás.
- review/newsworthiness.json: a tartalmi értékelés döntései és rövid indoklásai. include / exclude / review. Ellenőrizetlen hír nem jut az aktív listába.
- public/active.json: a PM Online állandó importlistája. A még el nem intézett hírek másnap is megmaradnak.
- public/used.json: a felhasznált és kukázott hírek tartós emlékezete. A napi gyűjtő nem írja át.
- public/import/pmonline-daily.json: az adott előkészítés új hozzáadásai.
- public/daily/YYYY-MM-DD.json: az adott nap legutóbbi előkészítésének új hozzáadásai; a teljes munkalista mindig az active.json.
- public/status.json és public/daily-status.json: a tényleges gyűjtési lefedettség és a függő értékelések állapota.

Az aktív rekord mezői: id, location, sourceName, url, sourceUrl, title, date, time, image, hasImage, excerpt, newsReason, newsCategory. A date/time a forrás megjelenési ideje; ismeretlen időpont null. A kép URL-je metaadat, nem automatikus képfelhasználási engedély. Teljes forráscikket nem másolunk a nyilvános JSON-ba.

## Indítás

A beállításra kész munkafolyamat: setup/collect.yml. Ezt a GitHubon .github/workflows/collect.yml néven kell elmenteni; a jelenlegi CLI-kapcsolatból hiányzik a workflow jogosultság, ezért a reggeli GitHub-ütemezés még nem aktív. Nyilvános tároló szabványos GitHub-futtatója díjmentes, de a GitHub indítása késhet.

A PM Online-oldal és a háttérkapcsolat külön fejlesztési ágon készül. Élesítés előtt a szerver NEWS_INBOX_GITHUB_TOKEN beállítása szükséges: kizárólag e hírgyűjtő tároló Contents: read/write jogosultságával. A kulcs nem kerülhet a böngészőbe vagy ebbe a tárolóba. Új adatbázistábla nem szükséges; a piszkozatok a PM Online meglévő szerkesztői adatkezelését használják.

## Ellenőrzés

pip install -r requirements.txt
python -m unittest discover -s tests
python collect.py --days 7
python prepare_daily.py

A 174 forrásból nem mindegyik dolgozható fel automatikusan. Az elérhetetlen vagy dátumozásában bizonytalan oldalak külön állapottal szerepelnek; a lista nem teljes lefedettségi ígéret. Hiányzó/hibás aktív vagy kezelt fájlnál az előkészítés leáll, nem nullázza az előzményeket.
