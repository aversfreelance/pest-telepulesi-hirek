"""Append unseen daily news to active; compare only active and used files."""
import argparse
from datetime import datetime, timedelta
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


def merge_active(records, active, used, day, days=1):
    if not all(isinstance(value, list) for value in (records, active, used)):
        raise ValueError('Input, active and used must be JSON arrays')
    seen = set()
    for row in used:
        seen.update(identity_keys(row))
    merged, added = [], []
    cutoff = (datetime.fromisoformat(day).date() - timedelta(days=days - 1)).isoformat()
    for row in active:
        keys = identity_keys(row)
        if not keys & seen:
            merged.append(row)
        seen.update(keys)
    for row in records:
        keys = identity_keys(row)
        if not cutoff <= row.get('date', '') <= day:
            continue
        duplicate = bool(keys & seen)
        seen.update(keys)
        if not duplicate:
            merged.append(row)
            added.append(row)
    key = lambda row: (row.get('location') or '', row.get('date') or '', row.get('time') or '', row['id'])
    return sorted(merged, key=key), sorted(added, key=key)


def newsworthy_records(records, review):
    if review.get('version') != 1 or not isinstance(review.get('decisions'), list):
        raise ValueError('Invalid newsworthiness review file')
    by_id = {}
    for decision in review['decisions']:
        if decision.get('id') in by_id or decision.get('decision') not in ('include', 'exclude', 'review'):
            raise ValueError('Duplicate or invalid newsworthiness decision')
        by_id[decision['id']] = decision
    accepted, pending = [], []
    for row in records:
        decision = by_id.get(row['id'])
        if not decision or decision.get('sourceTitle') != row['title'] or decision.get('sourceDate') != row['date']:
            pending.append(row)
            continue
        if decision['decision'] == 'include':
            if not decision.get('reason'):
                raise ValueError('Included news needs an editorial reason')
            accepted.append({**row, 'newsReason': decision['reason'],
                             'newsCategory': decision.get('category', 'helyi-hir'),
                             'excerpt': decision.get('excerpt') or row.get('excerpt', '')})
        elif decision['decision'] == 'review':
            pending.append(row)
    return accepted, pending


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--day', help='Publication day YYYY-MM-DD; default today in Hungary')
    parser.add_argument('--days', type=int, help='Override initial seven-day / subsequent daily window')
    args = parser.parse_args()
    day = args.day or datetime.now(ZoneInfo('Europe/Budapest')).date().isoformat()
    if datetime.strptime(day, '%Y-%m-%d').date().isoformat() != day:
        raise ValueError('Invalid publication day')
    records = json.loads((ROOT / 'public/news.json').read_text(encoding='utf-8'))
    state_path = ROOT / 'data/editorial-state.json'
    state = json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else {}
    days = args.days or (1 if state.get('bootstrapCompletedAt') else 7)
    if not 1 <= days <= 31:
        parser.error('--days must be between 1 and 31')
    cutoff = (datetime.fromisoformat(day).date() - timedelta(days=days - 1)).isoformat()
    candidates = [row for row in records if cutoff <= row.get('date', '') <= day]
    review = json.loads((ROOT / 'review/newsworthiness.json').read_text(encoding='utf-8'))
    accepted, pending = newsworthy_records(candidates, review)
    active_path, used_path = ROOT / 'public/active.json', ROOT / 'public/used.json'
    active = json.loads(active_path.read_text(encoding='utf-8'))
    used = json.loads(used_path.read_text(encoding='utf-8'))
    merged, added = merge_active(accepted, active, used, day, days)
    write_json(active_path, merged)
    write_json(ROOT / 'public/import/pmonline-daily.json', added)
    write_json(ROOT / f'public/daily/{day}.json', added)
    write_json(ROOT / 'public/daily-by-settlement.json', group_by_settlement(added))
    status_path = ROOT / 'public/status.json'
    collection = json.loads(status_path.read_text(encoding='utf-8')) if status_path.exists() else {}
    reviewed = {d['id']: d for d in review['decisions']}
    fully_assessed = all(row['id'] in reviewed and
                         reviewed[row['id']].get('sourceTitle') == row['title'] and
                         reviewed[row['id']].get('sourceDate') == row['date'] for row in candidates)
    if candidates and fully_assessed and collection.get('complete'):
        state['bootstrapCompletedAt'] = state.get('bootstrapCompletedAt') or datetime.now(ZoneInfo('Europe/Budapest')).isoformat()
        write_json(state_path, state)
    write_json(ROOT / 'public/newsworthiness-pending.json', pending)
    write_json(ROOT / 'public/daily-status.json', {
        'day': day, 'timezone': 'Europe/Budapest',
        'preparedAt': datetime.now(ZoneInfo('Europe/Budapest')).isoformat(),
        'items': len(added), 'activeItems': len(merged), 'usedItems': len(used),
        'comparisonFiles': ['public/active.json', 'public/used.json'],
        'windowDays': days, 'newsworthinessPending': len(pending),
        'collectionCheckedAt': collection.get('checkedAt'),
        'collectionComplete': collection.get('complete', False),
        'latestInputPublicationDate': max((row.get('date') or '' for row in records), default=None),
    })
    print(f'{day}: {len(added)} added; {len(merged)} active, {len(used)} used')


if __name__ == '__main__':
    main()
