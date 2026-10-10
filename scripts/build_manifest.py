#!/usr/bin/env python3
"""uvx yt-dlp --flat-playlist --print "%(id)s\t%(duration)s\t%(title)s" <channel> | python3 scripts/build_manifest.py > manifest.tsv"""
import re, sys

COLS = ['episode', 'video_id', 'alt_video_id', 'duration', 'title', 'guest', 'note_name']
EP = re.compile(r'\s*[|–-]\s*Episode\s+(\d+)\s*$')
UNSAFE = re.compile(r'[\\/:*?"<>|]')

def rows(lines):
    by_ep = {}
    for line in lines:
        vid, dur, title = line.rstrip('\n').split('\t', 2)
        m = EP.search(title)
        if not m:
            print(f'skip (no episode number): {vid} {title}', file=sys.stderr)
            continue
        ep = int(m.group(1))
        if ep in by_ep:
            by_ep[ep]['alt_video_id'] = by_ep[ep]['alt_video_id'] or vid
            continue
        head = EP.sub('', title)
        guest, _, topic = head.partition(':')
        if not topic:
            guest, topic = '', head
        name = f'EP{ep:02d} {guest.strip()} - {topic.strip()}' if guest else f'EP{ep:02d} {topic.strip()}'
        by_ep[ep] = dict(episode=ep, video_id=vid, alt_video_id='', duration=int(float(dur)),
                         title=title, guest=guest.strip(), note_name=UNSAFE.sub('', name).strip())
    return [by_ep[k] for k in sorted(by_ep)]

if __name__ == '__main__':
    print('\t'.join(COLS))
    for r in rows(sys.stdin):
        print('\t'.join(str(r[c]) for c in COLS))
