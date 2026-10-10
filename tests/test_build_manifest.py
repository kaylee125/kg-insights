import sys, unittest
sys.path.insert(0, 'scripts')
from build_manifest import rows

SAMPLE = [
    "TZZyOTmConw\t2026\tJessica Talisman: The Ontology Pipeline Knowledge Engineering Framework | Episode 57",
    "7S0JQ639kh8\t2026\tJessica Talisman: The Ontology Pipeline Knowledge Engineering Framework – Episode 57",
    "yL8qJIRrBLQ\t2060\tFrançois Scharffe and Thomas Deeley: The Knowledge Graph Conference – Episode 1",
]

class T(unittest.TestCase):
    def test_dedup_and_order(self):
        r = rows(SAMPLE)
        self.assertEqual([x['episode'] for x in r], [1, 57])
        ep57 = r[1]
        self.assertEqual(ep57['video_id'], 'TZZyOTmConw')
        self.assertEqual(ep57['alt_video_id'], '7S0JQ639kh8')
        self.assertEqual(ep57['duration'], 2026)
        self.assertEqual(ep57['guest'], 'Jessica Talisman')
        self.assertEqual(ep57['note_name'], 'EP57 Jessica Talisman - The Ontology Pipeline Knowledge Engineering Framework')

    def test_no_alt(self):
        self.assertEqual(rows(SAMPLE)[0]['alt_video_id'], '')

    def test_skips_title_without_episode(self):
        r = rows(SAMPLE + ["abc123\t100\tChannel trailer"])
        self.assertEqual(len(r), 2)

    def test_title_without_colon_has_empty_guest(self):
        r = rows(["abc123\t100\tLive Q&A session | Episode 99"])
        self.assertEqual(r[0]['guest'], '')
        self.assertEqual(r[0]['note_name'], 'EP99 Live Q&A session')

    def test_note_name_is_filename_safe(self):
        r = rows(["abc123\t100\tA. Person: Why \"RDF/OWL\" still matters? | Episode 5"])
        self.assertNotRegex(r[0]['note_name'], r'[\\/:*?"<>|]')

if __name__ == '__main__':
    unittest.main()
