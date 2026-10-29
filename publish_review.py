"""Validate editorial decisions and publish metadata-only import lists."""
import html
import json
import unicodedata
from datetime import datetime, timezone
from collect import ROOT, write_json


def settlement_key(value):
    return ' '.join(unicodedata.normalize('NFC', value or '').casefold().split())


def group_by_settlement(records):
    groups = {}
    for record in records:
        name = ' '.join(unicodedata.normalize('NFC', record.get('location') or '').split())
        key = settlement_key(name)
        if not key:
            name, key = 'Ismeretlen település', '__unknown__'
        group = groups.setdefault(key, {'location': name, 'news': []})
        group['news'].append(record)
    for group in groups.values():
        group['news'].sort(key=lambda row: (row.get('date') or '', row.get('time') or '', row['id']), reverse=True)
    return [groups[key] for key in sorted(groups)]


def main():
    source = json.loads((ROOT / 'public/news.json').read_text(encoding='utf-8'))
    review = json.loads((ROOT / 'review/decisions.json').read_text(encoding='utf-8'))
    decisions = review['decisions']
    by_id = {row['id']: row for row in decisions}
    if len(by_id) != len(decisions) or set(by_id) != {row['id'] for row in source}:
        raise ValueError('Every current input ID must have exactly one editorial decision.')
    if not review.get('comparisonCheckedAt') or not review.get('comparisonSource'):
        raise ValueError('The PM Online comparison must be documented before publishing.')
    selected, pending = [], []
    fields = ('id', 'location', 'sourceName', 'sourceUrl', 'url', 'title', 'date', 'time', 'image', 'hasImage')
    for row in source:
        decision = by_id[row['id']]
        if decision.get('status') not in ('include', 'review', 'exclude') or not decision.get('reason'):
            raise ValueError('Invalid editorial decision: ' + row['id'])
        if decision.get('sourceTitle') != row['title'] or decision.get('sourceDate') != row['date']:
            raise ValueError('Input changed after review: ' + row['id'])
        record = {key: row.get(key) for key in fields}
        record['title'] = html.unescape(record['title'])
        if decision['status'] == 'include':
            if not record['url'] or not record['title'] or not record['location'] or not record['date']:
                raise ValueError('Missing import metadata: ' + row['id'])
            selected.append(record)
        elif decision['status'] == 'review':
            pending.append({**record, 'reviewReason': decision['reason']})
    selected_groups = group_by_settlement(selected)
    selected = [row for group in selected_groups for row in group['news']]
    write_json(ROOT / 'public/import/pmonline-news.json', selected)
    write_json(ROOT / 'public/import/pmonline-news-by-settlement.json', selected_groups)
    write_json(ROOT / 'public/news-by-settlement.json', group_by_settlement(source))
    write_json(ROOT / 'public/review-required-by-settlement.json', group_by_settlement(pending))
    write_json(ROOT / 'public/review-required.json', pending)
    write_json(ROOT / 'public/editorial-status.json', {
        'reviewedAt': datetime.now(timezone.utc).isoformat(), 'inputCount': len(source),
        'selected': len(selected), 'reviewRequired': len(pending),
        'excluded': len(source) - len(selected) - len(pending),
        'comparisonSource': review['comparisonSource'],
        'comparisonCheckedAt': review['comparisonCheckedAt'],
        'comparisonLimitations': review.get('comparisonLimitations', '')})
    print(f'Selected: {len(selected)}, review required: {len(pending)}')


if __name__ == '__main__':
    main()
