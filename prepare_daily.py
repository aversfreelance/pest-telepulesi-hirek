"""Append unseen daily news to active; compare only active and used files."""
import argparse
from datetime import datetime
import json
from zoneinfo import ZoneInfo
from collect import ROOT, write_json, canonical
from publish_review import group_by_settlement


def identity_keys(record):
    if not isinstance(record, dict) or not isinstance(record.get('id'), str) or not record['id']:
        raise ValueError('Each record must have a non-empty string id')
    keys = {'id:' + record['id']}
    url = record.get('url') or record.get('sourceUrl')
    if url:
        keys.add('url:' + canonical(url))
    return keys


def merge_active(records, active, used, day):
    if not all(isinstance(value, list) for value in (records, active, used)):
        raise ValueError('Input, active and used must be JSON arrays')
    seen = set()
    for row in used:
        seen.update(identity_keys(row))
    merged, added = [], []
    for row in active:
        keys = identity_keys(row)
        if not keys & seen:
            merged.append(row)
        seen.update(keys)
    for row in records:
        keys = identity_keys(row)
        if row.get('date') != day:
            continue
        duplicate = bool(keys & seen)
        seen.update(keys)
        if not duplicate:
            merged.append(row)
            added.append(row)
    key = lambda row: (row.get('location') or '', row.get('date') or '', row.get('time') or '', row['id'])
    return sorted(merged, key=key), sorted(added, key=key)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--day', help='Publication day YYYY-MM-DD; default today in Hungary')
    args = parser.parse_args()
    day = args.day or datetime.now(ZoneInfo('Europe/Budapest')).date().isoformat()
    if datetime.strptime(day, '%Y-%m-%d').date().isoformat() != day:
        raise ValueError('Invalid publication day')
    records = json.loads((ROOT / 'public/news.json').read_text(encoding='utf-8'))
    active_path, used_path = ROOT / 'public/active.json', ROOT / 'public/used.json'
    active = json.loads(active_path.read_text(encoding='utf-8'))
    used = json.loads(used_path.read_text(encoding='utf-8'))
    merged, added = merge_active(records, active, used, day)
    write_json(active_path, merged)
    write_json(ROOT / 'public/import/pmonline-daily.json', added)
    write_json(ROOT / f'public/daily/{day}.json', added)
    write_json(ROOT / 'public/daily-by-settlement.json', group_by_settlement(added))
    status_path = ROOT / 'public/status.json'
    collection = json.loads(status_path.read_text(encoding='utf-8')) if status_path.exists() else {}
    write_json(ROOT / 'public/daily-status.json', {
        'day': day, 'timezone': 'Europe/Budapest',
        'preparedAt': datetime.now(ZoneInfo('Europe/Budapest')).isoformat(),
        'items': len(added), 'activeItems': len(merged), 'usedItems': len(used),
        'comparisonFiles': ['public/active.json', 'public/used.json'],
        'collectionCheckedAt': collection.get('checkedAt'),
        'collectionComplete': collection.get('complete', False),
        'latestInputPublicationDate': max((row.get('date') or '' for row in records), default=None),
    })
    print(f'{day}: {len(added)} added; {len(merged)} active, {len(used)} used')


if __name__ == '__main__':
    main()
