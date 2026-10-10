#!/usr/bin/env python3
"""python3 scripts/build_index.py  — vault/Index.md 생성"""
from kgvtt import VAULT, manifest

def names(folder):
    return sorted(p.stem for p in (VAULT / folder).glob('*.md') if not p.name.startswith('_'))

eps = '\n'.join(f"- [[{r['note_name']}]]" for r in manifest())
themes = '\n'.join(f'- [[{n}]]' for n in names('Themes'))
concepts = '\n'.join(f'- [[{n}]]' for n in names('Concepts'))
(VAULT / 'Index.md').write_text(
    f'# Knowledge Graph Insights 학습 볼트\n\n출처: https://www.youtube.com/@KnowledgeGraphInsights\n\n'
    f'## 주제\n{themes}\n\n## 에피소드\n{eps}\n\n## 개념\n{concepts}\n', encoding='utf-8')
print('Index.md written')
