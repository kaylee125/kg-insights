#!/usr/bin/env python3
"""python3 scripts/fetch.py  — manifest 전체 수집. 이미 받은 편은 건너뜀. 중단 후 재실행하면 이어받음."""
import csv, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'raw'
RAW.mkdir(exist_ok=True)

def have(tag):
    return any(RAW.glob(f'{tag}-*.en-orig.vtt'))

def fetch(tag, vid):
    cmd = ['uvx', 'yt-dlp', '--skip-download', '--write-auto-subs', '--sub-langs', 'en-orig',
           '--sub-format', 'vtt', '--write-info-json', '--sleep-requests', '2',
           '-o', str(RAW / f'{tag}-%(id)s.%(ext)s'), f'https://www.youtube.com/watch?v={vid}']
    with open(RAW / 'fetch.log', 'a') as log:
        log.write(f'\n=== {tag} {vid} {time.strftime("%F %T")}\n')
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)

failed = []
for row in csv.DictReader(open(ROOT / 'manifest.tsv', encoding='utf-8'), delimiter='\t'):
    tag = f'ep{int(row["episode"]):03d}'
    if have(tag):
        continue
    for vid in (row['video_id'], row['alt_video_id']):
        if not vid:
            continue
        fetch(tag, vid)
        if have(tag):
            break
        print(f'{tag} {vid}: no en-orig vtt', file=sys.stderr)
        for junk in RAW.glob(f'{tag}-{vid}.*'):   # 자막 없는 시도의 info.json은 치움
            junk.unlink()
    else:
        failed.append(tag)
    time.sleep(3)

print('done. failed:', failed or 'none')
sys.exit(1 if failed else 0)
