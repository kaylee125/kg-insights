#!/usr/bin/env python3
"""python3 scripts/clean_vtt.py  — raw/*.vtt 전부를 transcripts/epNNN.md 로. 이미 있으면 덮어씀(결정적)."""
import kgvtt
from kgvtt import fmt, manifest, parse_vtt, raw_vtt

PARA_SEC = 30   # ponytail: 고정 30초 문단, 문장 경계 인식은 자동 자막에 구두점이 없어 의미 없음

def render(row, vid, lines):
    paras, cur, cur_start = [], [], None
    for sec, text in lines:
        if cur and sec - cur_start >= PARA_SEC:
            paras.append((cur_start, ' '.join(cur)))
            cur = []
        if not cur:
            cur_start = sec
        cur.append(text)
    if cur:
        paras.append((cur_start, ' '.join(cur)))
    head = (f"# EP{row['episode']} — {row['title']}\n\n"
            f"video_id: {vid} · duration: {fmt(row['duration'])} · guest: {row['guest']} · url: https://youtu.be/{vid}\n")
    body = '\n\n'.join(f'**[{fmt(s)}](https://youtu.be/{vid}?t={s})** {t}' for s, t in paras)
    return head + '\n' + body + '\n'

if __name__ == '__main__':
    kgvtt.TR.mkdir(exist_ok=True)
    for row in manifest():
        vtt = raw_vtt(row['episode'])
        if not vtt:
            print(f"ep{row['episode']:03d}: no vtt, skipped")
            continue
        vid = vtt.name.split('-', 1)[1].split('.')[0]
        (kgvtt.TR / f"ep{row['episode']:03d}.md").write_text(render(row, vid, parse_vtt(vtt)), encoding='utf-8')
    print('done')
