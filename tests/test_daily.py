import unittest
from prepare_daily import merge_active


def row(id, day='2026-10-29', url=None):
    return {'id': id, 'date': day, 'location': 'Érd', 'url': url or 'https://a.hu/' + id}


class ActiveQueueTests(unittest.TestCase):
    def test_only_unseen_today_items_added_and_old_pending_survives(self):
        active = [row('pending', '2026-10-28')]
        used = [row('used')]
        inputs = [row('new'), row('new'), row('pending'), row('used'), row('yesterday', '2026-10-28')]
        merged, added = merge_active(inputs, active, used, '2026-10-29')
        self.assertEqual({x['id'] for x in merged}, {'pending', 'new'})
        self.assertEqual([x['id'] for x in added], ['new'])
        again, additions = merge_active(inputs, merged, used, '2026-10-29')
        self.assertEqual(again, merged)
        self.assertEqual(additions, [])
        self.assertEqual(len(active), 1)
        self.assertEqual(len(used), 1)

    def test_used_wins_and_tracking_url_cannot_reintroduce_item(self):
        used = [row('used', url='https://a.hu/cikk?id=42')]
        inputs = [row('different-id', url='https://a.hu/cikk?id=42&utm_source=x#top'),
                  row('different-article', url='https://a.hu/cikk?id=43')]
        merged, added = merge_active(inputs, [row('used')], used, '2026-10-29')
        self.assertEqual([x['id'] for x in merged], ['different-article'])
        self.assertEqual(merged, added)

    def test_invalid_history_fails_instead_of_resetting_it(self):
        with self.assertRaises(ValueError):
            merge_active([], [], {}, '2026-10-29')
        with self.assertRaises(ValueError):
            merge_active([], [], [{}], '2026-10-29')
