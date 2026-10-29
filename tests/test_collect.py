import unittest
from datetime import datetime, timezone
from collect import publication, canonical, article_record, image_url, merge_records, feed_candidates


class CollectorTests(unittest.TestCase):
    def test_date_without_time(self):
        self.assertEqual(publication('2026. október 29.'), ('2026-10-29', None))

    def test_timestamp(self):
        self.assertEqual(publication('2026-10-29T08:35:12+01:00'), ('2026-10-29', '08:35'))

    def test_url_keeps_content_query(self):
        self.assertEqual(canonical('https://a.hu/?id=42&utm_source=x#top'), 'https://a.hu/?id=42')

    def test_theme_image_is_not_article_image(self):
        self.assertIsNone(image_url('/wp-content/themes/a/navto-bg.png', 'https://a.hu/'))

    def test_footer_date_does_not_make_page_news(self):
        self.assertIsNone(article_record({'location': 'Teszt', 'sourceName': 'Teszt'},
                                        'https://a.hu/cikk', '<h1>Önkormányzati hírek</h1><footer>2026-10-29</footer>'))

    def test_rss_date_and_link(self):
        items = list(feed_candidates(b'<rss><channel><item><title>News</title><link>https://a.hu/a</link><pubDate>Thu, 29 Oct 2026 08:30:00 +0100</pubDate></item></channel></rss>', 'https://a.hu'))
        self.assertEqual(items[0]['url'], 'https://a.hu/a')
        self.assertEqual(publication(items[0]['date']), ('2026-10-29', '08:30'))

    def test_failed_source_preserves_existing_records(self):
        old = [{'id': 'a', 'date': datetime.now(timezone.utc).date().isoformat(), 'time': None}]
        self.assertEqual(merge_records(old, []), old)

    def test_reimport_updates_instead_of_duplicates(self):
        date = datetime.now(timezone.utc).date().isoformat()
        old = [{'id': 'a', 'date': date, 'title': 'Old'}]
        fresh = [{'id': 'a', 'date': date, 'title': 'New'}]
        self.assertEqual(merge_records(old, fresh), fresh)


if __name__ == '__main__':
    unittest.main()
