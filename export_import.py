"""Standalone UTF-8 JSON export. No connection to any importing application."""
from datetime import date, time
import html
import json
import re
from urllib.parse import urlsplit
from collect import ROOT, canonical, write_json


def valid_url(value):
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return parsed.scheme in ('https', 'http') and bool(parsed.hostname) and not parsed.username and not parsed.password


def record_keys(row):
    if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id']:
        raise ValueError('Every active/used entry must have an id')
    keys = {'id:' + row['id']}
    url = row.get('url') or row.get('sourceUrl')
    if url:
        if not valid_url(url):
            raise ValueError('Invalid source URL: ' + row['id'])
        keys.add('url:' + canonical(url))
    return keys


def build_import(active, used):
    if not isinstance(active, list) or not isinstance(used, list):
        raise ValueError('Active and used files must be JSON arrays')
    seen = set()
    for row in used:
        seen.update(record_keys(row))
    result = []
    for row in active:
        keys = record_keys(row)
        duplicate = bool(keys & seen)
        seen.update(keys)
        if duplicate:
            continue
        for field in ('location', 'sourceName', 'title', 'date'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f'Missing {field}: {row["id"]}')
        date.fromisoformat(row['date'])
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', row['date']):
            raise ValueError('Invalid date format: ' + row['id'])
        supplied_time = row.get('time')
        if supplied_time is not None:
            if not isinstance(supplied_time, str) or not re.fullmatch(r'\d{2}:\d{2}', supplied_time):
                raise ValueError('Invalid time format: ' + row['id'])
            time.fromisoformat(supplied_time)
        url = row.get('url') or row.get('sourceUrl')
        if not valid_url(url):
            raise ValueError('Missing article URL: ' + row['id'])
        image = row.get('image') or None
        if image is not None and not valid_url(image):
            raise ValueError('Invalid image URL: ' + row['id'])
        if type(row.get('hasImage')) is not bool or row['hasImage'] != bool(image):
            raise ValueError('Inconsistent image indicator: ' + row['id'])
        item = {field: row[field].strip() for field in ('id', 'location', 'sourceName', 'date')}
        item.update(url=url, sourceUrl=url, title=html.unescape(row['title']).strip(),
                    time=supplied_time, hasImage=row['hasImage'], image=image)
        for field in ('excerpt', 'newsCategory', 'newsReason'):
            value = row.get(field, '')
            if not isinstance(value, str):
                raise ValueError('Invalid ' + field + ': ' + row['id'])
            item[field] = html.unescape(value).strip()
        if isinstance(row.get('collectedAt'), str):
            item['collectedAt'] = row['collectedAt']
        result.append(item)
    return sorted(result, key=lambda row: (row['location'].casefold(), row['date'], row['time'] or '', row['id']))


def export_files():
    active = json.loads((ROOT / 'public/active.json').read_text(encoding='utf-8'))
    used = json.loads((ROOT / 'public/used.json').read_text(encoding='utf-8'))
    records = build_import(active, used)
    write_json(ROOT / 'public/import/news.json', records)
    print(f'Import-ready JSON: {len(records)} records')
    return records


if __name__ == '__main__':
    export_files()
