import unittest
from publish_review import group_by_settlement


class SettlementGroupingTests(unittest.TestCase):
    def test_normalizes_names_without_merging_different_settlements(self):
        rows = [
            {'id': 'a', 'location': ' Érd ', 'date': '2026-10-28'},
            {'id': 'b', 'location': 'E\u0301RD', 'date': '2026-10-29'},
            {'id': 'c', 'location': 'Érdliget', 'date': '2026-10-29'},
            {'id': 'd', 'location': '', 'date': '2026-10-29'},
        ]
        groups = group_by_settlement(rows)
        self.assertEqual(len(groups), 3)
        erd = next(group for group in groups if group['location'] == 'Érd')
        self.assertEqual([row['id'] for row in erd['news']], ['b', 'a'])
        self.assertEqual(sum(len(group['news']) for group in groups), 4)
        self.assertEqual(len(rows), 4)


if __name__ == '__main__':
    unittest.main()
