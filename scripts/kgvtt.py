"""vtt 파싱·타임스탬프·manifest 공용 모듈. clean_vtt.py, check.py, build_index.py가 쓴다."""
import csv, html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW, TR, VAULT = ROOT / 'raw', ROOT / 'transcripts', ROOT / 'vault'
CUE = re.compile(r'(\d+):(\d\d):(\d\d)\.\d+ --> ')
TAG = re.compile(r'<[^>]+>')

def parse_vtt(path):
    """[(start_sec, text)] — 자동 자막의 롤링 중복(다음 큐의 첫 줄 == 앞 큐의 마지막 줄)만 걷어낸다.
    같은 큐 안의 반복은 실제 발화(진행자가 게스트 말을 따라 하는 경우)라 남긴다."""
    lines, start, prev, first = [], None, None, True
    for raw in Path(path).read_text(encoding='utf-8').splitlines():
        m = CUE.match(raw)
        if m:
            h, mi, s = m.groups()
            start = int(h) * 3600 + int(mi) * 60 + int(s)
            first = True
            continue
        if start is None:
            continue
        text = html.unescape(TAG.sub('', raw)).strip()   # &gt;&gt; → >> (화자 교체 표시)
        if not text:
            continue
        if not (first and text == prev):
            lines.append((start, text))
            prev = text
        first = False
    return lines

def word_count(lines):
    return sum(len(t.split()) for _, t in lines)

def fmt(sec):
    h, r = divmod(int(sec), 3600)
    m, s = divmod(r, 60)
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m:02d}:{s:02d}'

def parse_ts(s):
    parts = [int(p) for p in s.strip().split(':')]
    while len(parts) < 3:
        parts.insert(0, 0)
    h, m, s = parts
    return h * 3600 + m * 60 + s

def manifest():
    with open(ROOT / 'manifest.tsv', encoding='utf-8') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    for r in rows:
        r['episode'] = int(r['episode'])
        r['duration'] = int(r['duration'])
    return rows

def raw_vtt(ep):
    return next(RAW.glob(f'ep{ep:03d}-*.en-orig.vtt'), None)

def raw_info(ep):
    p = next(RAW.glob(f'ep{ep:03d}-*.info.json'), None)
    return json.loads(p.read_text(encoding='utf-8')) if p else None
