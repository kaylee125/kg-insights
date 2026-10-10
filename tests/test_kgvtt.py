import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, 'scripts')
from kgvtt import parse_vtt, word_count, fmt, parse_ts

VTT = """WEBVTT
Kind: captions
Language: en-orig

00:00:01.000 --> 00:00:03.000 align:start position:0%
hello there


00:00:03.000 --> 00:00:05.000 align:start position:0%
hello there
general<00:00:04.000><c> kenobi</c>

00:00:05.000 --> 00:00:07.000 align:start position:0%
general kenobi


01:02:03.000 --> 01:02:05.000 align:start position:0%
late line

01:02:06.000 --> 01:02:08.000 align:start position:0%
&gt;&gt; speaker change &amp; entity

01:02:10.000 --> 01:02:12.000 align:start position:0%
&gt;&gt; it was the nineties
&gt;&gt; it was the nineties
"""

class T(unittest.TestCase):
    def setUp(self):
        self.p = Path(tempfile.mkdtemp()) / 'x.vtt'
        self.p.write_text(VTT, encoding='utf-8')

    def test_parse_dedups_rolling_lines(self):
        self.assertEqual(parse_vtt(self.p)[:3],
                         [(1, 'hello there'), (3, 'general kenobi'), (3723, 'late line')])

    def test_parse_unescapes_html_entities(self):
        self.assertEqual(parse_vtt(self.p)[3], (3726, '>> speaker change & entity'))

    def test_keeps_genuine_repeat_within_one_cue(self):
        # 롤링 중복은 "다음 큐의 첫 줄 == 앞 큐의 마지막 줄"뿐이다. 같은 큐 안의 반복은 실제 발화(진행자가 게스트 말을 따라함).
        self.assertEqual(parse_vtt(self.p)[4:], [(3730, '>> it was the nineties'), (3730, '>> it was the nineties')])

    def test_word_count(self):
        self.assertEqual(word_count(parse_vtt(self.p)), 21)

    def test_ts_roundtrip_over_hour(self):
        self.assertEqual(fmt(3723), '1:02:03')
        self.assertEqual(fmt(65), '01:05')
        self.assertEqual(parse_ts('1:02:03'), 3723)
        self.assertEqual(parse_ts('01:05'), 65)

if __name__ == '__main__':
    unittest.main()
