# 정책 탐색 결과 — 2026-09-28 KST

**Models.** Primary: **cap7** ([`../../v0-unsubmitted/cap7-codex/`](../../v0-unsubmitted/cap7-codex/), Codex). Also: v3 (starting point and baseline, [`../../v3-codex/`](../../v3-codex/)), v2 and the stand in policies "fast attack" and "slow defence" as opponents, and the official Lv2.

## 범위와 자료

- 기준선은 수정하지 않은 `out/v3-codex/v3.zip`이다. v2와 v3 ZIP의 `main.py`는 깃발병 상한 12 → 6 한 줄만 다르다는 검사를 탐색기에 남겼다.
- 공식 `engine`/`runner.InProcessBot`에서 고정 시드와 동일 상대를 사용해 유한한 좌표 탐색을 했다. 별도 학습 가중치나 외부 패키지는 없다. 인프로세스 평가는 시간 제한을 강제하지 않으므로 채택 후보는 실제 프로세스·공식 로컬 제출 검사로 다시 검증했다.
- 상대 풀: v2, v3, 빠른 공격형(깃발병 상한 3·보류 0), 느린 수비형(상한 8·보류 6/4·위험 벌점 8), 공식 Lv2. 마지막 Y 검증은 Lv2의 전승 포화를 제외한 앞의 네 상대를 사용했다. 이 로컬 변형들은 실제 상대 팀의 비공개 봇을 재현하지 않는다.
- `train.json`, `holdout.json`, `train2.json`, `holdout2.json`, `final.json`에 후보별 정책, 상대, 시드, 진영, 승패·점수·20턴/종료 건물과 병력 가치·몰수·턴 시간·출력 최대값을 보존했다. 각 정책·상대 조합은 같은 시드로 v3와 짝지었다.

## 조정한 판단값

| 판단값 | v3 | 검토 후보 | 작용 |
| --- | ---: | ---: | --- |
| `CAP` | 6 | 7 | 깃발병 생산 상한; 남은 자원의 전투병 배분에도 영향 |
| `RESERVE` | 4 | 1 | 중앙광장 미보유 시 생산에 쓰지 않고 남기는 자원 |
| `PLAZA_RESERVE` | 2 | 0 | 중앙광장 보유 시 남기는 자원 |
| `SCORE_WEIGHT` | 1 | 1 | 이동·점령 목표의 건물 점수 가중치 |
| `BONUS` | 2 | 2 | 보급소·병원·학생회관 목표 보너스 |
| `DANGER` | 4 | 4 | 적 전투병이 있는 목표의 벌점 |

건물 점수·유닛 비용·점령 비용 같은 엔진 고정 수치는 바꾸지 않았다. 후반 세 값도 탐색했으나 채택 후보에서는 v3 값을 유지했다. 후보 소스는 `candidate-python/main.py`에 있고, v3 제출 ZIP과 저장소의 v3 소스는 그대로다.

## 탐색과 미사용 시드 비교

| 단계 | 시드·진영·상대 | v3 | 비교 후보 | 판단 |
| --- | --- | ---: | ---: | --- |
| 1차 탐색 | 20–23, Y, 5종 × 4 = 20경기 | 12승 | 상한4 16승; 보류1/0 17승; 보류7/4 17승 | 셋을 다음 단계로 |
| 1차 미사용 | 100–107, Y/K, 5종 × 16 = 80경기 | 52승 | 상한4 43승; 보류1/0 52승; 보류7/4 51승 | 모두 기각 |
| 2차 탐색 | 30–35, Y, 5종 × 6 = 30경기 | 15승 | 종류 보너스 확대 19승; 상한7·보류1/0 20승 | 둘을 다음 단계로 |
| 2차 미사용 | 200–207, Y/K, 5종 × 16 = 80경기 | 54승 | 종류 보너스 확대 53승; 상한7·보류1/0 60승 | 상한7 후보만 유지 |
| 최종 Y 미사용 | 300–319, Y, 4종 × 20 = 80경기 | 40승 | 상한7·보류1/0 **45승** | 검토용 후보 채택 |

2차 미사용 시드의 Y만 보면 v3 28/40, 후보 29/40이다. 두 독립 시드 묶음의 Y 합계는 v3 68/120, 후보 **74/120**이다. 마지막 80경기 평균 점수 차는 Y 기준 v3 +1.62, 후보 +3.11; 20턴 건물은 7.39 → 7.88개, 병력 가치는 217.6 → 220.3이었다. 미사용 시드 전체에서 몰수는 0이다. 관측된 개선 폭은 작으므로 실제 상대 팀 승률 개선으로 해석하지 않는다.

마지막 Y 평가의 상대별 승리는 v2 11→14, v3 7→8, 빠른 공격형 12→11, 느린 수비형 10→12였다. 빠른 공격형의 1승 하락은 남은 위험이다. 상한4 후보는 첫 탐색 16/20으로 앞섰으나 미사용 시드 43/80으로 v3의 52/80에 못 미친 대표 과적합 사례다. 낮은 보류값 단독 후보도 v3·빠른 공격형에는 좋아졌으나 v2·수비형에서 물러나 최종 승수가 같았다.

## 실제 프로세스와 ZIP 검사

- `out/tools/evaluation/subprocess_eval.py`로 검토 후보 Y 대 v3 K, 시드 0–9: **5승·0무·5패, 몰수 0**. 이 시드는 위 미사용 검증의 시드와 다르며 전략 채택 지표보다는 프로세스 안정성 검사다. 기록 최대 턴 시간 529.27ms는 첫 턴의 별도 3초 제한 안이며, 일반 턴 시간 초과에 따른 몰수는 없었다. 경기 원본은 `out/experiments/3-policy-weight-search(cap7)/policy-cap7-v3-subprocess-Y/`에 있다.
- Windows Python의 공식 `make_submission.py`로 `out/v0-unsubmitted/cap7-codex/cap7.zip` 생성. 최상위 항목 6개(`submission.json`과 Python 5개)는 모두 mode `100666`, ZIP의 `main.py`는 후보 소스와 바이트 일치한다.
- WSL Python 3.14.4의 공식 `run_tests.py --zip`: `ok: true`, `issues: []`, `warnings: []`; 무행동 상대 16턴 승리. 검사 중 stdout 최대 한 턴 331바이트·20줄, 최대 한 줄 87바이트, stderr 0. 서버 Python은 3.12.14이므로 서버 검사 결과는 아직 없다. 원본: [`local-zip-check.json`](../../v0-unsubmitted/cap7-codex/local-zip-check.json).
- **온라인 업로드·서버 검사·모의 전투·대회용 코드 선택은 이 Goal에서 수행하지 않았다.** 기존 v3의 공식 중급 봇 10승 및 서버 사용 가능 상태는 이전 제출 결과이며, 이번 검토 ZIP에 적용되는 결과가 아니다.

## 재실행과 LLM 기록

저장소 루트에서 실행한다(정리 후 경로; `policy_search.py`의 함수들은 정리 후 `weight_search.py` 재현에서 실제로 다시 쓰였고, 위 5개 단계 명령 자체는 저장된 `*.json`을 덮어쓰므로 다시 실행하지 않았다). 탐색은 공식 엔진 인프로세스이므로 Windows Python 3.12에서도 된다: `python out/tools/evaluation/policy_search.py train`, `holdout`, `train2`, `holdout2`, `final`을 각각 실행하면 `train.json` 등이 이 폴더에 다시 만들어진다(시드·상대·설정은 위 표와 스크립트 안의 `variants`). 실제 프로세스 검사는 러너의 파이프 때문에 WSL에서 `python3 out/tools/evaluation/subprocess_eval.py out/v0-unsubmitted/cap7-codex/source/main.py out/v3-codex/source/main.py --side Y --seeds 10 --name policy-cap7-v3-subprocess-Y --outdir "out/experiments/3-policy-weight-search(cap7)"`이다(모델·버전: 후보 cap7 대 v3 K, 시드 0–9, WSL Python 3.14.4; 같은 명령의 국지 리플레이는 `policy-cap7-v3-subprocess-Y/replays/`에 생기며 Git에서 제외된다). 제출 검사는 `python3 bots/dist/starter/run_tests.py --zip out/v0-unsubmitted/cap7-codex/cap7.zip`이다.

모델은 Codex GPT-6 계열이다. 이 Goal의 프롬프트(P3)와 앞선 프롬프트(P1, P2)의 원문은 [`../../PROMPT_RECORD.md`](../../PROMPT_RECORD.md)에 있다. 이번 사용자 후속 지시는 다운로드 차단 해결, `Downloads`에 파일을 남기지 않기, 식별 가능한 이름 사용이다. LLM은 정책값 탐색 설계, 공식 엔진 대전·리플레이 집계, 실패 유형 해석, 후보 소스·ZIP 검증과 기록 작성에 사용했다. 타 팀 코드·전략 문서, 외부 가중치·패키지는 사용하지 않았다. 기존 공식 리플레이 19개는 상대명·경기 ID가 포함된 `out/official-replays/`에 있으며 Windows `Downloads/replay*.json` 잔여 파일은 0개였다.
