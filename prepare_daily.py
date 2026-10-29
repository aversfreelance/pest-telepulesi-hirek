"""Prepare the daily manual-picking queue; never makes editorial choices."""
import argparse
from datetime import datetime
import json
from zoneinfo import ZoneInfo
from collect import ROOT, write_json
from publish_review import group_by_settlement


def daily_queue(records, actions, day):
    if actions.get('version') != 1:
        raise ValueError('Unsupported PM Online actions format')
    lists = [actions.get(name) for name in ('selectedIds', 'deletedIds')]
    if any(not isinstance(items, list) or any(not isinstance(item, str) for item in items) for items in lists):
        raise ValueError('selectedIds and deletedIds must be arrays of IDs')
    handled = set(lists[0]) | set(lists[1])
    unique = {}
    for row in records:
        if row.get('date') == day and row.get('id') and row['id'] not in handled:
            unique[row['id']] = row
    return sorted(unique.values(), key=lambda row: (row.get('location') or '', row.get('time') or '', row['id']))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--day', help='Publication day, YYYY-MM-DD; default: today in Hungary')
    parser.add_argument('--actions', default=str(ROOT / 'review/pmonline-actions.json'))
    args = parser.parse_args()
    day = args.day or datetime.now(ZoneInfo('Europe/Budapest')).date().isoformat()
    if datetime.strptime(day, '%Y-%m-%d').date().isoformat() != day:
        raise ValueError('Invalid publication day')
    records = json.loads((ROOT / 'public/news.json').read_text(encoding='utf-8'))
    actions = json.loads(open(args.actions, encoding='utf-8').read())
    queue = daily_queue(records, actions, day)
    write_json(ROOT / 'public/import/pmonline-daily.json', queue)
    write_json(ROOT / f'public/daily/{day}.json', queue)
    write_json(ROOT / 'public/daily-by-settlement.json', group_by_settlement(queue))
    status_path = ROOT / 'public/status.json'
    collection = json.loads(status_path.read_text(encoding='utf-8')) if status_path.exists() else {}
    write_json(ROOT / 'public/daily-status.json', {
        'day': day, 'timezone': 'Europe/Budapest',
        'preparedAt': datetime.now(ZoneInfo('Europe/Budapest')).isoformat(),
        'items': len(queue), 'actionsUpdatedAt': actions.get('updatedAt'),
        'actionsConnected': bool(actions.get('updatedAt')),
        'collectionCheckedAt': collection.get('checkedAt'),
        'collectionComplete': collection.get('complete', False),
        'latestInputPublicationDate': max((row.get('date') or '' for row in records), default=None),
    })
    print(f'{day}: {len(queue)} unhandled news items; PM Online state connected: {bool(actions.get("updatedAt"))}')


if __name__ == '__main__':
    main()
