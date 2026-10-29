import unittest
from prepare_daily import daily_queue


class DailyQueueTests(unittest.TestCase):
    def test_publication_day_and_pmonline_actions(self):
        rows = [{'id': name, 'date': day, 'location': 'Érd'} for name, day in
                [('new', '2026-10-29'), ('picked', '2026-10-29'),
                 ('deleted', '2026-10-29'), ('old', '2026-10-28')]]
        actions = {'version': 1, 'selectedIds': ['picked'], 'deletedIds': ['deleted']}
        result = daily_queue(rows + [rows[0]], actions, '2026-10-29')
        self.assertEqual([row['id'] for row in result], ['new'])
        self.assertEqual(len(rows), 4)

    def test_bad_state_does_not_silently_reintroduce_deleted_items(self):
        with self.assertRaises(ValueError):
            daily_queue([], {'version': 1, 'selectedIds': [], 'deletedIds': 'bad'}, '2026-10-29')
