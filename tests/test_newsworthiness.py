import unittest
from prepare_daily import newsworthy_records, merge_active


class NewsworthinessTests(unittest.TestCase):
    def test_unreviewed_or_changed_title_cannot_enter_active(self):
        rows = [{'id': 'a', 'title': 'New title', 'date': '2026-10-29'}]
        review = {'version': 1, 'decisions': [{'id': 'a', 'sourceTitle': 'Old title',
                  'sourceDate': '2026-10-29', 'decision': 'include', 'reason': 'Important'}]}
        accepted, pending = newsworthy_records(rows, review)
        self.assertEqual(accepted, [])
        self.assertEqual(pending, rows)

    def test_review_does_not_override_used_and_bootstrap_includes_older_news(self):
        row = {'id': 'a', 'title': 'Title', 'date': '2026-10-25', 'url': 'https://a.hu/a'}
        review = {'version': 1, 'decisions': [{'id': 'a', 'sourceTitle': 'Title',
                  'sourceDate': '2026-10-25', 'decision': 'include', 'reason': 'Important'}]}
        accepted, pending = newsworthy_records([row], review)
        self.assertEqual(len(accepted), 1)
        self.assertEqual(pending, [])
        self.assertEqual(merge_active(accepted, [], [row], '2026-10-29', 7), ([], []))
        self.assertEqual(len(merge_active(accepted, [], [], '2026-10-29', 7)[0]), 1)
        self.assertEqual(merge_active(accepted, [], [], '2026-10-29', 1), ([], []))
