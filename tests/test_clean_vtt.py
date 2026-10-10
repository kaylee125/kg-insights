import sys, unittest
sys.path.insert(0, 'scripts')
from clean_vtt import render

ROW = dict(episode=7, title='G: T | Episode 7', guest='G', duration=100)
LINES = [(0, 'a b'), (10, 'c'), (29, 'd'), (31, 'e f'), (70, 'g')]

class T(unittest.TestCase):
    def test_paragraphs_every_30s_with_links(self):
        out = render(ROW, 'vid7', LINES)
        self.assertIn('# EP7 — G: T | Episode 7', out)
        self.assertIn('**[00:00](https://youtu.be/vid7?t=0)** a b c d', out)
        self.assertIn('**[00:31](https://youtu.be/vid7?t=31)** e f', out)
        self.assertIn('**[01:10](https://youtu.be/vid7?t=70)** g', out)

    def test_word_count_preserved(self):
        body = [l for l in render(ROW, 'vid7', LINES).splitlines() if l.startswith('**[')]
        self.assertEqual(sum(len(l.split('** ', 1)[1].split()) for l in body), 7)

if __name__ == '__main__':
    unittest.main()
