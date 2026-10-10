# kg-insights

YouTube 채널 *Knowledge Graph Insights*(58개 에피소드)의 스크립트를 수집·정제하고, AI로 2차 가공해 학습용 마크다운(Obsidian) 볼트를 만드는 개인 파이프라인.

- 목표와 성공 기준: [`docs/specs/2026-09-30-kg-insights-vault-design.md`](docs/specs/2026-09-30-kg-insights-vault-design.md)
- 실행 기록과 결정 사항: [`docs/plans/2026-10-01-kg-insights-vault-ledger.md`](docs/plans/2026-10-01-kg-insights-vault-ledger.md)

## 구성
| 경로 | 역할 |
|---|---|
| `manifest.tsv` | 에피소드 목록 |
| `scripts/fetch.py` | 자막 수집(이어받기) |
| `scripts/clean_vtt.py`, `kgvtt.py` | VTT를 읽기 좋은 텍스트로 정제 |
| `scripts/build_manifest.py`, `build_index.py` | 목록과 색인 생성 |
| `scripts/check.py` | 모든 에피소드 노트가 영상 전 구간을 다뤘는지, 원문 위치로 되돌아갈 수 있는지 검사 |
| `scripts/episode_prompt.md` | 에피소드 노트 생성 프롬프트 |

테스트: `python3 -m unittest discover -s tests`

## 이 저장소에 없는 것
원본 스크립트(`raw/`, `transcripts/`)와 그것을 가공한 볼트(`vault/`)는 채널 제작자의 콘텐츠라서 올리지 않았다. 수집 스크립트로 각자 로컬에서 다시 만든다.
