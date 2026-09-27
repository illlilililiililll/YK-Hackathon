# 2026 연고전 AI 해커톤 개발 기록

## 2026-09-27 (KST)

- 모델: Codex (GPT-6 계열; 현재 대화에 세부 모델 식별자는 표시되지 않음).
- 프롬프트: [원문 Goal](GOAL_PROMPT.md). 후속 사용자 응답: `Allow access to file URLs`, `설정 완료`(Chrome 업로드 권한 설정).
- LLM 활용: 공개 규칙 및 공식 스타터 킷 대조, 예제 분석, 전략 가설·코드 작성, 로컬 전투·리플레이 해석, 제출 형식 검증. 타 팀 코드·전략, 외부 가중치·패키지 미사용.
- 공식 `/rules` 페이지(19:00 KST 전후)와 새로 받은 Python 샘플 ZIP 및 개발 도구 ZIP 확인. 개발 도구의 저장소 대응 파일은 수정한 `python/main.py` 외 모두 바이트 단위 일치. Python 3.12.14, 일반 턴 300ms, 첫 턴 3s, stdout 64KiB/4096줄, ZIP 최상위 `submission.json`/`main.py` 확인.
- 로컬 Ubuntu WSL Python 3.14.4 사용. 서버 Python 3.12.14와 버전 차이 있음. 공식 `run_tests.py --self-test` 4항목 통과.

### 기준선과 가설

| 버전·조건 | Y 승·무·패 | 몰수 | 평균 최종 점수 Y:K | 평균 종료 턴 | 최대 후보 턴 시간 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 공식 Lv2 대 공식 Lv2, 시드 0–9 | 0·10·0 | 0 | 14.3:14.3 | 160 | 94.36ms |
| 후보 v1 대 공식 Lv2, Y, 시드 0–9 | 10·0·0 | 0 | 34.2:0 | 39.9 | 87.79ms |
| 공식 Lv2 대 후보 v1, K, 시드 0–9 | 0·0·10 | 0 | 0:34.2 | 42.8 | 111.01ms |
| 후보 v1 대 공식 Lv1, Y, 시드 0–9 | 10·0·0 | 0 | 34.8:0 | 23.6 | 79.25ms |

가설: Lv2는 다수 깃발병을 같은 가장 가까운 건물로 보내 중앙 점령이 정체된다. 시드 0의 160턴 종료 때 중앙광장·중앙 건물 7곳이 중립이었다. 건물별 깃발병 1명 배정, 병원 전진 생산, 적 깃발병으로 전투병 이동을 적용했다. 수정 후 10개 시드에서 Y/K 모두 Lv2 상대로 전승했다.

첫 코드 작성에서 `sorted()`의 생성식 문법 오류로 초기 10경기 모두 첫 턴 몰수가 발생했다. 문법을 수정하고 같은 조건에서 10승 0몰수를 확인했다. 이 실패는 후보 채택 전 검사 사례다.

### 제출본 v1

- 소스: `bots/dist/starter/python/main.py`; `protocol.py`, `campus_bot.py`, `search.py`, `_generated.py`는 공식 배포본 재사용.
- ZIP: `out/y-agent-v1.zip` (9,177 bytes), SHA-256 `8A9090F107D4AB3162948298B684A4CC052C0754EC0845986DFC456738A28890`.
- 공식 `make_submission.py`로 생성, WSL `run_tests.py --zip` 결과 `ok: true`, `issues: []`, `warnings: []`; 시드 0 무행동 상대 16턴 즉시승, 검사 대상 stdout 최대 370 bytes/turn·22 lines/turn, 최대 줄 87 bytes, stderr 0.
- 로컬 상세 결과·리플레이: `out/baseline-lv2-self-Y/`, `out/v1-vs-lv2-Y/`, `out/v1-vs-lv2-K/`, `out/v1-vs-lv1-Y/`.
- 온라인 v1: 19:06 KST 제출했으나 서버 `수정 필요`/`EXECUTABLE_FILE`(`executable files are not allowed`). WSL이 Windows 드라이브 파일을 mode `100777`로 ZIP에 기록한 것이 원인. 서버에서 선택 불가하여 이 실패본의 모의 전투는 실행 불가.

### 최종 제출본 v2 및 공식 모의 전투

- 전략 소스 변경 없음. Windows Python 3.12.7에서 같은 공식 `make_submission.py`로 재포장해 ZIP 항목 mode `100666` 확인. ZIP: `out/y-agent-v2.zip`, SHA-256 `97E8EDE84225DD8AFA08A6FD245AFA9D294F20845B001F1A528802EB2BE0AF06`.
- v2 ZIP은 WSL 공식 `run_tests.py --zip`에서 `ok: true`, `issues: []`, `warnings: []`, 16턴 즉시승. stdout 최대 370 bytes/turn·22 lines/turn, 최대 줄 87 bytes, stderr 0.
- 19:07 KST 공식 제출 v2(`y-agent-v2.zip`, Python 3.12): 상태 `사용 가능`, `대회에 사용할 코드: v2` / `사용 중`. 빌드 로그: `Source validated and image assembled. Actual game protocol smoke is pending.` 다음 모의 전투에서 프로토콜 정상 실행 확인.
- 19:08 KST 선택된 v2, Y 연세, 공식 `중 · 수료 기준` 모의 전투 10경기 완료: **10승 0무 0패**, 수료 기준 통과, `정상 실행`/`ok`, 기록된 실행 오류 없음. 표시된 실행 진단: 기록된 턴 응답 41회, 평균 25ms, stdout 11.2KiB·643줄. 경기별 리플레이 10개가 사이트 `/practice` 결과에 연결됨(첫 경기 ID `01a0e256-b1f1-7a75-9823-73c8cd3eb23c`).

로컬 시간은 WSL/Windows 호스트와 서버의 CPU 환경이 달라 서버 턴 시간을 보장하지 않는다. 서버 확인이 목표 완료에 필요하다.
