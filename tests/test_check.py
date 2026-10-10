import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, 'scripts')
import kgvtt, check

def cue(sec, text):
    h, r = divmod(sec, 3600); m, s = divmod(r, 60)
    return f'{h:02d}:{m:02d}:{s:02d}.000 --> {h:02d}:{m:02d}:{s+1:02d}.000\n{text}\n\n'

def vtt(step, total, wps=3):
    # 큐마다 텍스트가 달라야 한다. 같으면 parse_vtt의 연속 중복 제거에 합쳐진다.
    body = ''.join(cue(t, ' '.join(f'w{t}_{i}' for i in range(wps * step))) for t in range(0, total, step))
    return 'WEBVTT\n\n' + body

class Base(unittest.TestCase):
    def setUp(self):
        d = Path(tempfile.mkdtemp())
        for name in ('RAW', 'TR', 'VAULT'):
            setattr(kgvtt, name, d / name.lower()); setattr(check, name, d / name.lower())
            getattr(kgvtt, name).mkdir()
        (kgvtt.VAULT / 'Episodes').mkdir(); (kgvtt.VAULT / 'Concepts').mkdir()
        self.d = d
        check.MANIFEST = [dict(episode=7, video_id='vid7', duration=600, note_name='EP07 G - T')]

    def put_raw(self, text, duration=600):
        (kgvtt.RAW / 'ep007-vid7.en-orig.vtt').write_text(text, encoding='utf-8')
        (kgvtt.RAW / 'ep007-vid7.info.json').write_text(json.dumps({'duration': duration}))

class Fetch(Base):
    def test_fetch_pass(self):
        self.put_raw(vtt(10, 600))
        self.assertEqual(check.check_fetch(7), [])

    def test_fetch_truncated_fails(self):
        self.put_raw(vtt(10, 300))          # 자막이 5분에서 끝남
        self.assertTrue(any('last cue' in r for r in check.check_fetch(7)))

    def test_fetch_gap_fails(self):
        self.put_raw('WEBVTT\n\n' + cue(0, 'w w w') + ''.join(cue(t, ' '.join(f'w{t}_{i}' for i in range(30))) for t in range(200, 600, 10)))
        self.assertTrue(any('gap' in r for r in check.check_fetch(7)))

    def test_fetch_missing_fails(self):
        self.assertTrue(any('missing' in r for r in check.check_fetch(7)))

class Clean(Base):
    def test_clean_word_count_match(self):
        self.put_raw(vtt(10, 600))
        n = kgvtt.word_count(kgvtt.parse_vtt(kgvtt.raw_vtt(7)))
        (kgvtt.TR / 'ep007.md').write_text('# EP7\n\nmeta\n\n**[00:00](u)** ' + ' '.join(['w'] * n) + '\n')
        self.assertEqual(check.check_clean(7), [])

    def test_clean_word_count_mismatch(self):
        self.put_raw(vtt(10, 600))
        (kgvtt.TR / 'ep007.md').write_text('# EP7\n\n**[00:00](u)** w w w\n')
        self.assertTrue(any('words' in r for r in check.check_clean(7)))

def note(timeline):
    return '---\nepisode: 7\nduration: "10:00"\n---\n## 핵심 인사이트\n- x\n## 타임라인\n' + timeline + '\n## 다룬 개념\n'

class Extract(Base):
    def test_extract_pass(self):
        (kgvtt.VAULT / 'Episodes' / 'EP07 G - T.md').write_text(note('- [00:00–04:00] a\n- [04:00–08:30] b\n- [08:30–10:00] c'))
        self.assertEqual(check.check_extract(7), [])

    def test_extract_single_huge_segment_fails(self):
        check.MANIFEST[0]['duration'] = 1200
        (kgvtt.VAULT / 'Episodes' / 'EP07 G - T.md').write_text(note('- [00:00–20:00] everything'))
        self.assertTrue(any('longer than' in r for r in check.check_extract(7)))

    def test_extract_stops_early_fails(self):
        (kgvtt.VAULT / 'Episodes' / 'EP07 G - T.md').write_text(note('- [00:00–04:00] a\n- [04:00–06:00] b'))
        self.assertTrue(any('ends at' in r for r in check.check_extract(7)))

    def test_extract_gap_fails(self):
        (kgvtt.VAULT / 'Episodes' / 'EP07 G - T.md').write_text(note('- [00:00–04:00] a\n- [06:00–10:00] b'))
        self.assertTrue(any('gap' in r for r in check.check_extract(7)))

    def test_extract_accepts_hyphen_and_hour(self):
        check.MANIFEST[0]['duration'] = 4000
        (kgvtt.VAULT / 'Episodes' / 'EP07 G - T.md').write_text(note('- [00:00-09:00] a\n- [09:00-18:00] b\n- [18:00-27:00] c\n- [27:00-36:00] d\n- [36:00-45:00] e\n- [45:00-54:00] f\n- [54:00-1:03:00] g\n- [1:03:00-1:06:40] h'))
        self.assertEqual(check.check_extract(7), [])

class Links(Base):
    def test_links_resolve(self):
        (kgvtt.VAULT / 'Episodes' / 'EP07 G - T.md').write_text('see [[Ontology]] and [[Ontology|온톨로지]]')
        (kgvtt.VAULT / 'Concepts' / 'Ontology.md').write_text('from [[EP07 G - T]]')
        self.assertEqual(check.check_links(), [])

    def test_unresolved_link_fails(self):
        (kgvtt.VAULT / 'Episodes' / 'EP07 G - T.md').write_text('see [[Nowhere]]')
        self.assertTrue(any('Nowhere' in r for r in check.check_links()))

    def test_concept_without_episode_link_fails(self):
        (kgvtt.VAULT / 'Concepts' / 'Ontology.md').write_text('no sources here')
        self.assertTrue(any('Ontology' in r and 'episode link' in r for r in check.check_links()))

    def test_concept_bullet_without_timestamp_fails(self):
        (kgvtt.VAULT / 'Episodes' / 'EP07 G - T.md').write_text('x')
        (kgvtt.VAULT / 'Concepts' / 'Ontology.md').write_text(
            '## 게스트별 관점\n- [[EP07 G - T]] (G): said it — [01:00](https://youtu.be/vid7?t=60)\n- [[EP07 G - T]] (G): said it again, no link\n')
        out = check.check_links()
        self.assertEqual(len([r for r in out if 'timestamp' in r]), 1)

if __name__ == '__main__':
    unittest.main()
