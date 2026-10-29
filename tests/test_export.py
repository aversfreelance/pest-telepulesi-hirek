import unittest
from export_import import build_import


def record(id='new', **extra):
    return dict({'id': id, 'location': 'Érd', 'sourceName': 'Városi hírek',
                 'url': 'https://a.hu/' + id, 'title': 'Helyi hír',
                 'date': '2026-10-29', 'time': None, 'image': None, 'hasImage': False}, **extra)


class ImportExportTests(unittest.TestCase):
    def test_used_and_discarded_records_never_reappear_even_with_new_id(self):
        used = [record('used', usageStatus='used'), record('discarded', usageStatus='discarded')]
        active = [record(), record('alias', url='https://a.hu/used?utm_source=x'), record('discarded')]
        self.assertEqual([r['id'] for r in build_import(active, used)], ['new'])
        self.assertEqual(len(active), 3)
        self.assertEqual(len(used), 2)

    def test_missing_time_is_null_and_headline_entities_are_decoded(self):
        result = build_import([record(title='Hír &#8211; folytatás')], [])[0]
        self.assertIsNone(result['time'])
        self.assertEqual(result['title'], 'Hír – folytatás')
        self.assertEqual(result['url'], result['sourceUrl'])

    def test_invalid_import_cannot_silently_replace_a_good_file(self):
        for bad in [record(url='javascript:alert(1)'), record(date='2026-02-30'),
                    record(time='25:00'), record(hasImage=True)]:
            with self.assertRaises(ValueError):
                build_import([bad], [])
