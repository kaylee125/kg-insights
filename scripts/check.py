#!/usr/bin/env python3
"""python3 scripts/check.py fetch|clean|extract|links  — 단계별 완전성 검사. 실패가 있으면 exit 1."""
import re, sys
import kgvtt
from kgvtt import parse_vtt, word_count, parse_ts, raw_vtt, raw_info

RAW, TR, VAULT = kgvtt.RAW, kgvtt.TR, kgvtt.VAULT
MANIFEST = None   # 테스트에서 바꿔 끼움; None이면 manifest.tsv

PARA = re.compile(r'^\*\*\[[\d:]+\]\(\S+\)\*\* (.*)$')
SEG = re.compile(r'^- \[(\d[\d:]*)\s*[–-]\s*(\d[\d:]*)\]')
LINK = re.compile(r'\[\[([^\]|#]+)')

def rows():
    return MANIFEST if MANIFEST is not None else kgvtt.manifest()

def check_fetch(ep):
    vtt, info = raw_vtt(ep), raw_info(ep)
    if not vtt or not info:
        return ['missing vtt or info.json']
    dur, lines, out = info['duration'], parse_vtt(vtt), []
    if not lines:
        return ['empty vtt']
    last = lines[-1][0]
    if dur - last > max(60, dur * 0.03):
        out.append(f'last cue {last}s vs duration {dur}s')
    starts = [0] + [s for s, _ in lines]
    gap = max(b - a for a, b in zip(starts, starts[1:]))
    if gap > 120:
        out.append(f'gap {gap}s between cues')
    wpm = word_count(lines) / (dur / 60)
    if wpm < 100:
        out.append(f'only {wpm:.0f} wpm')
    return out

def check_clean(ep):
    vtt, md = raw_vtt(ep), TR / f'ep{ep:03d}.md'
    if not vtt or not md.exists():
        return ['missing vtt or transcript']
    src = word_count(parse_vtt(vtt))
    got = sum(len(m.group(1).split()) for l in md.read_text(encoding='utf-8').splitlines() if (m := PARA.match(l)))
    return [] if src == got else [f'words {got} in transcript vs {src} in vtt']

def _note(ep):
    return next(VAULT.glob(f'Episodes/EP{ep:02d} *.md'), None)

def check_extract(ep):
    row = next(r for r in rows() if r['episode'] == ep)
    note = _note(ep)
    if not note:
        return ['missing episode note']
    text = note.read_text(encoding='utf-8')
    if f'episode: {ep}' not in text:
        return ['frontmatter episode mismatch']
    body = text.split('## 타임라인', 1)
    if len(body) < 2:
        return ['no 타임라인 section']
    segs = sorted((parse_ts(m.group(1)), parse_ts(m.group(2))) for l in body[1].splitlines() if (m := SEG.match(l)))
    if not segs:
        return ['no timeline segments']
    out, dur = [], row['duration']
    if segs[0][0] > 60:
        out.append(f'timeline starts at {segs[0][0]}s')
    for (a, b), (c, _) in zip(segs, segs[1:]):
        if c - b > 60:
            out.append(f'gap {b}s→{c}s')
    for a, b in segs:
        if b - a > 600:
            out.append(f'segment {a}–{b} longer than 10 min')
    if dur - segs[-1][1] > 180:
        out.append(f'timeline ends at {segs[-1][1]}s vs duration {dur}s')
    return out

def check_links():
    files = {p.stem: p for p in VAULT.rglob('*.md')}
    out = []
    for p in files.values():
        text = p.read_text(encoding='utf-8')
        for target in LINK.findall(text):
            if target.strip() not in files:
                out.append(f'{p.name}: unresolved [[{target}]]')
        if p.parent.name in ('Concepts', 'Themes') and not p.name.startswith('_') and '[[EP' not in text:
            out.append(f'{p.name}: no episode link')
        if p.parent.name == 'Concepts':   # 게스트별 관점 항목마다 타임스탬프 링크 (스펙 성공 기준 3)
            for l in text.splitlines():
                if l.startswith('- [[EP') and 'youtu.be' not in l:
                    out.append(f'{p.name}: no timestamp on "{l[:50]}"')
    return out

if __name__ == '__main__':
    stage = sys.argv[1]
    if stage == 'links':
        fails = check_links()
    else:
        fn = {'fetch': check_fetch, 'clean': check_clean, 'extract': check_extract}[stage]
        fails = []
        for r in rows():
            ep, bad = r['episode'], fn(r['episode'])
            print(f'ep{ep:03d} ' + ('PASS' if not bad else 'FAIL ' + '; '.join(bad)))
            fails += [f'ep{ep:03d}: {b}' for b in bad]
    print('\n'.join(fails))
    print(f'{stage}: {len(fails)} failure(s)')
    sys.exit(1 if fails else 0)
