"""Municipal news metadata collector. Never imports article bodies."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
from pathlib import Path
import re
from time import monotonic, sleep
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from dateutil.parser import isoparse

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'public/news.json'
STATUS = ROOT / 'public/status.json'
HEADERS = {'User-Agent': 'PestTelepulesiHirek/1.0 (public municipal news metadata)'}
MONTHS = ['január', 'február', 'március', 'április', 'május', 'június',
          'július', 'augusztus', 'szeptember', 'október', 'november', 'december']


def fetch(url):
    with urlopen(Request(url, headers=HEADERS), timeout=18) as response:
        data = response.read(5_000_001)
        if len(data) > 5_000_000:
            raise ValueError('Page exceeds 5 MB')
        return data, response.geturl()


def canonical(url):
    p = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
             if not k.startswith('utm_') and k not in ('fbclid', 'gclid')]
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip('/') or '/',
                       urlencode(query), ''))


def publication(value):
    """Return only a supplied publication date/time; never invent midnight."""
    if not value:
        return None, None
    value = re.sub(r'\s+', ' ', str(value)).strip()
    for index, month in enumerate(MONTHS, 1):
        value = re.sub(rf'(\d{{4}})\.?\s+{month}\s+(\d{{1,2}})\.?',
                       lambda m: f'{m[1]}-{index:02d}-{int(m[2]):02d}', value,
                       flags=re.I)
    value = re.sub(r'(\d{4})[./](\d{2})[./](\d{2})\.?', r'\1-\2-\3', value)
    match = re.search(r'\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?', value)
    try:
        parsed = isoparse(match[0]) if match else parsedate_to_datetime(value)
        return parsed.date().isoformat(), parsed.strftime('%H:%M') if re.search(r'\d{2}:\d{2}', value) else None
    except (ValueError, TypeError, OverflowError):
        return None, None


def structured_articles(soup):
    def walk(value):
        if isinstance(value, list):
            for item in value:
                yield from walk(item)
        elif isinstance(value, dict):
            types = value.get('@type', [])
            if isinstance(types, str):
                types = [types]
            if any(t in ('Article', 'NewsArticle', 'BlogPosting') for t in types):
                yield value
            for child in value.values():
                if isinstance(child, (dict, list)):
                    yield from walk(child)
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            yield from walk(json.loads(script.string or script.get_text()))
        except (ValueError, TypeError):
            pass


def image_url(value, base):
    if isinstance(value, list):
        return next((url for v in value if (url := image_url(v, base))), None)
    if isinstance(value, dict):
        value = value.get('url') or value.get('contentUrl')
    if not isinstance(value, str) or not value.strip():
        return None
    value = urljoin(base, value.strip())
    if urlsplit(value).scheme not in ('http', 'https'):
        return None
    if re.search(r'logo|favicon|sprite|placeholder|avatar|/icons?/|banner|/themes/|navto|default[-_]?image', value, re.I):
        return None
    return value


def article_record(source, url, raw, hint=None):
    hint = hint or {}
    soup = BeautifulSoup(raw, 'html.parser')
    data = next(structured_articles(soup), {})
    def meta(*keys):
        for key in keys:
            node = soup.find('meta', attrs={'property': key}) or soup.find('meta', attrs={'name': key})
            if node and node.get('content'):
                return node['content']
        return None
    heading = soup.find('h1')
    title = data.get('headline') or (heading.get_text(' ', strip=True) if heading else None) or hint.get('title')
    if not title or len(title.strip()) < 8:
        return None
    supplied = data.get('datePublished') or meta('article:published_time', 'datePublished', 'date')
    if not supplied:
        node = soup.select_one('[itemprop="datePublished"], time.entry-date, time.published, .posted-on time, article time[datetime]')
        if node:
            supplied = node.get('datetime') or node.get('content') or node.get_text(' ', strip=True)
    date, time = publication(supplied or hint.get('date'))
    # Undated pages cannot be reliably classified as fresh news.
    if not date:
        return None
    today = datetime.now(timezone.utc).date()
    if not today - timedelta(days=31) <= datetime.fromisoformat(date).date() <= today:
        return None
    image = image_url(data.get('image'), url) or image_url(meta('og:image'), url)
    if not image:
        node = soup.select_one('article .entry-content img, article .post-thumbnail img, .article-content img, [itemprop="articleBody"] img')
        if node:
            image = image_url(node.get('data-src') or node.get('src'), url)
    url = canonical(url)
    return {'id': 'hir-' + hashlib.sha256((source['location'] + '|' + url).encode()).hexdigest()[:20],
            'location': source['location'], 'sourceName': source['sourceName'],
            'sourceUrl': url, 'url': url, 'title': re.sub(r'\s+', ' ', title).strip(),
            'date': date, 'time': time, 'image': image, 'hasImage': bool(image)}


def feed_candidates(raw, base):
    root = ET.fromstring(raw)
    def tag(node):
        return node.tag.rsplit('}', 1)[-1]
    for item in root.iter():
        if tag(item) not in ('item', 'entry'):
            continue
        values = {}
        for child in item:
            name = tag(child)
            if name == 'link' and child.get('rel', 'alternate') == 'alternate':
                values['url'] = urljoin(base, child.get('href') or child.text or '')
            if name in ('pubDate', 'published'):
                values['date'] = child.text
            if name == 'title':
                values['title'] = ''.join(child.itertext())
        if values.get('url'):
            yield values


def collect_source(source):
    errors, records, candidates = [], [], []
    started = monotonic()
    try:
        raw, base = fetch(source['url'])
        soup = BeautifulSoup(raw, 'html.parser')
        feeds = [urljoin(base, n['href']) for n in soup.select('link[rel="alternate"][href]')
                 if any(kind in n.get('type', '') for kind in ('rss', 'atom'))]
        for feed in feeds[:1]:
            try:
                feed_raw, feed_base = fetch(feed)
                candidates.extend(feed_candidates(feed_raw, feed_base))
            except Exception as exc:
                errors.append('feed: ' + str(exc))
        for node in soup.select('article h2 a[href], article h3 a[href], h2.entry-title a[href], h2 a[href], h3 a[href]'):
            link = urljoin(base, node['href'])
            if urlsplit(link).netloc.removeprefix('www.') != urlsplit(base).netloc.removeprefix('www.'):
                continue
            if re.search(r'\.(pdf|jpe?g|png|docx?|zip)(?:\?|$)', link, re.I):
                continue
            candidates.append({'url': link, 'title': node.get_text(' ', strip=True)})
        seen = {canonical(base)}
        for candidate in candidates:
            if monotonic() - started > 75:
                errors.append('Per-source time budget reached; remaining candidates deferred.')
                break
            url = canonical(candidate['url'])
            if url in seen:
                continue
            seen.add(url)
            if len(seen) > 21:
                break
            try:
                sleep(0.2)
                page, final_url = fetch(url)
                record = article_record(source, final_url, page, candidate)
                if record:
                    records.append(record)
            except Exception as exc:
                errors.append(url + ': ' + str(exc))
        state = ('partial' if errors else 'ok') if records else 'needs_review'
    except Exception as exc:
        errors.append(str(exc))
        state = 'error'
    return records, {'location': source['location'], 'url': source['url'], 'state': state,
                     'articles': len(records), 'candidates': len(candidates), 'errors': errors}


def merge_records(old, fresh):
    cutoff = (datetime.now(timezone.utc).date() - timedelta(days=31)).isoformat()
    merged = {item['id']: item for item in old if item.get('date', '') >= cutoff}
    merged.update({item['id']: item for item in fresh})
    return sorted(merged.values(), key=lambda item: (item['date'], item.get('time') or '', item['id']), reverse=True)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    sources = json.loads((ROOT / 'sources.json').read_text(encoding='utf-8'))
    if args.limit:
        sources = sources[:args.limit]
    fresh, statuses = [], []
    with ThreadPoolExecutor(max_workers=6) as pool:
        jobs = [pool.submit(collect_source, source) for source in sources]
        for job in as_completed(jobs):
            records, status = job.result()
            fresh.extend(records)
            statuses.append(status)
            print(f"{status['location']}: {status['state']} ({len(records)})", flush=True)
            # Preserve usable progress even if a later source times out.
            old_progress = json.loads(OUTPUT.read_text(encoding='utf-8')) if OUTPUT.exists() else []
            if records:
                write_json(OUTPUT, merge_records(old_progress, records))
            write_json(STATUS, {'checkedAt': datetime.now(timezone.utc).isoformat(),
                               'complete': False, 'sourceCount': len(sources),
                               'checkedSources': len(statuses), 'freshRecords': len(fresh),
                               'sources': sorted(statuses, key=lambda row: row['location'])})
    old = json.loads(OUTPUT.read_text(encoding='utf-8')) if OUTPUT.exists() else []
    if fresh:
        write_json(OUTPUT, merge_records(old, fresh))
    write_json(STATUS, {'checkedAt': datetime.now(timezone.utc).isoformat(),
                        'complete': True, 'checkedSources': len(statuses),
                        'sourceCount': len(sources), 'freshRecords': len(fresh),
                        'sources': sorted(statuses, key=lambda row: row['location'])})
    if not fresh:
        raise SystemExit('No dated news collected; existing feed preserved. See public/status.json.')


if __name__ == '__main__':
    main()
