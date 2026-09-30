# v4 / v5 candidate — provenance uncertain

> **Neither file below is proven to be the website's submission v4 or v5.** The site's v5 is the current competition selection and its source is still not in this repository.
> This folder keeps the source of the better verified of two look alike sources that were received as ZIPs (`main.zip` and `main5.zip`), a **valid submission package of each** built with the official tools (`rebuilt-main.zip`, `rebuilt-main5.zip`), and the evidence for why their identity stays open.
> Both packages are **reconstructions**, not the uploaded files; their bytes cannot be equal to any historical upload (different file dates, and the uploaded ZIPs were larger). Neither has been uploaded.

## What was received (originals were only read, never modified)

Both files sit in `Documents/카카오톡 받은 파일/` (KakaoTalk downloads); the sender is not recorded.

| | `main.zip` | `main5.zip` |
| --- | --- | --- |
| ZIP size | 4,038 bytes | 4,010 bytes |
| Entries | one: `main.py` (mode 0o100666) | one: **`main5.py`** (mode 0o100666) |
| Entry date stored in the ZIP | 2026-09-29 17:57:26 | 2026-09-29 14:14:22 |
| Entry size | 11,204 bytes | 11,166 bytes |
| Policy constants | **`GUARD = 1`, `ENDGAME = 0`** | `GUARD = 2`, `ENDGAME = 15` |

## Full byte level difference

Both sources have 273 lines, LF endings and no other difference than lines 9 and 10 (the ZIP entry names and dates also differ):

```diff
-GUARD = 1          # 건물당 기본 수비 인원
-ENDGAME = 0        # 마지막 몇 턴 수비 강화 (테스트 결과 끄는 게 더 강함)
+GUARD = 2          # 건물당 기본 수비 인원
+ENDGAME = 15       # 마지막 몇 턴은 수비 강화
```

`GUARD` is the number of warriors kept on each owned building on top of the nearby enemy warriors; `ENDGAME` is the number of final turns in which that guard need is doubled (plus one). The comment in `main.zip` says that switching the end game guard off tested stronger.

## What the code does

An independent design (not derived from v2, v3, cap7 or the `indep` agents). Flag bearers (F) only go to targets that a threat map calls safe (enemy warriors within one step plus what the enemy could spawn now), one flag per building, at most five wanted; they flee from threatened cells.
Warriors (W) are produced with what is left after the flags and are split into guards for every owned building, hunters for enemy flags within 8 steps, and one main army that goes to the best goal it can win: an own building with an enemy flag next to it, an enemy flag that is capturing, then a siege of an enemy building, else it waits at the front building.
The code imports only the official `protocol` helper (`DIRS`, `move`, `priority`, `run`, `spawn`) and the standard library, and wraps `decide` so that an exception costs one turn, not the game.

## Protocol compatibility and packaging

- The source uses only fields and helpers of the official `campus_bot.py` / `protocol.py` (`view.turn`, `team`, `opp`, `my_resource`, `opp_resource`, `units`, `buildings`; `init.bases`, `init.passable`).
- **Neither received ZIP is a valid submission on its own.** The official `submission.inspect_zip` rejects both: no `submission.json` at the ZIP root (the helper modules `protocol.py`, `campus_bot.py`, `_generated.py` are also missing). `main5.zip` additionally has no entry named `main.py`.
- **Reconstruction, both variants** (added on request: "make the ZIP file a valid submission: add the submission file"). Each variant was packaged with the official `bots/dist/starter/make_submission.py` under Windows Python 3.12.7, from its received code plus the four official helper files copied from `bots/dist/starter/python/` (byte identical to the helpers inside the submitted v2/v3 ZIPs) and the official `submission.json` (`schemaVersion` 1, `language` `python`). Every entry mode is 0o100666; a build under WSL would store 0o100777 and the server would reject it as `EXECUTABLE_FILE`, like v1.

| package | code in the entry `main.py` | size |
| --- | --- | --- |
| [`rebuilt-main.zip`](rebuilt-main.zip): the `main.zip` variant, `GUARD = 1`, `ENDGAME = 0` | [`source/main.py`](source/main.py), byte identical to the entry `main.py` of `main.zip` (11,204 bytes) | 7,887 bytes |
| [`rebuilt-main5.zip`](rebuilt-main5.zip): the `main5.zip` variant, `GUARD = 2`, `ENDGAME = 15` | the entry `main5.py` of `main5.zip` (11,166 bytes), unchanged; the official option `--entry main5.py` stores it as `main.py` | 7,857 bytes |

  Both ZIPs hold exactly five entries: `_generated.py`, `campus_bot.py`, `main.py`, `protocol.py`, `submission.json`. The `main5.zip` package has no `source/` folder of its own, because its code differs from [`source/main.py`](source/main.py) only in lines 9 and 10; `tools/evaluation/verify_artifacts.py` checks its `main.py` against the received `main5.py` and the helper entries against `source/`.
- Official checks of the two delivered files (`submission.inspect_zip`, then `run_tests.py --zip`, WSL Python 3.14.4, seed 52): both `ok: true`, no issues or warnings, 12 turns 21:0 win, stderr 0 bytes; at most 291 bytes and 17 lines per turn for `rebuilt-main.zip`, 288 bytes and 16 lines for `rebuilt-main5.zip`.

## Can the files be identified with the site's v4 or v5? Not proven

Recorded site rows (browser snapshots kept in the Codex session logs; the sizes shown are the real ZIP sizes, e.g. v3 9.0 KiB = 9,177 bytes and v6 10.2 KiB = 10,465 bytes):

| site submission | file name | size | status |
| --- | --- | --- | --- |
| v4 | `y-agent-v4.zip` | 11.6 KiB | `수정 필요` with the message "파일 구성을 확인해 주세요." (check the file composition); processed 2026-09-29 13:22 KST; the button "이 코드 사용" is disabled (only normally uploaded submissions can be selected) |
| v5 | `v-agent-v4.zip` | 11.2 KiB | `사용 가능`; processed 2026-09-29 13:25 KST; **selected for the competition** (`사용 중`); submission ID `01a0eb68-e2a0-7200-b852-6f81f2906061` (from the build log object key, see below) |

What fits and what does not:

- A full kit style package (nine entries like the v3 ZIP) of either received source would weigh 11.1 KiB (11,392 and 11,362 bytes). That is close to v5 (11.2 KiB) but not equal to it, and 0.5 KiB below v4. Sizes are rounded to 0.1 KiB, so this is a weak fingerprint that can exclude but never confirm.
- The received ZIPs are about 4 KB single file archives, so they are not the uploaded files. Their stored entry dates (14:14 and 17:57 on 09-29) are later than both site processing times (v4 13:22, v5 13:25); a save after the upload would explain that, but a later revision would too. Names and timestamps alone were deliberately **not** used to assign a version.
- v4 (13:22, rejected for its file composition) and v5 (13:25, 0.4 KiB smaller, accepted) were uploaded three minutes apart under near identical names; that fits the belief that they are the same code packaged differently, but it says nothing about which source is inside them.
- Search of the recorded session logs for identity evidence: the build log pages of v2, v3, v5 and v6 carry an object key `build-logs/<team>/<UUID>/<log id>.txt`. The UUID equals the recorded submission ID for v6 (`01a0ebe3-3f4b-74c5-9a44-d57b14b70ab2`), so it is used as the submission ID of v5 above (and of v2 and v3 in their READMEs). The last part of the key is identical for v2, v3, v5 and v6, so it identifies the (identical) build log text, not the ZIP. The build log of v4 was never opened, so v4's ID and the detailed reason for its rejection are not recorded. **Nothing in the logs identifies the contents of the v4 or v5 ZIP.**

**Status: provenance uncertain for both files.** They may be v4/v5 or later revisions of them; no statement in this repository depends on either assumption.

## Local comparison under identical conditions

Official engine and runner in WSL (Python 3.14.4), the two sources packaged identically, seeds 3000–3099 (never used by any earlier experiment), no forfeit and no traceback in the candidate stderr logs. Raw rows: [`comparison/`](comparison/).
Because this code catches every exception, prints `decide error T…` to stderr without a traceback and answers with no commands, silently skipped turns would not show up as forfeits. The whole head to head (200 games) and 6 of the 11 pool opponents (360 games) were therefore run a second time with the stderr of both variants captured: **0 lines of stderr, 0 `decide error`** for either variant, and every re-run row (outcome, score, turns, unit values, timeline snapshots) equals the stored row (200 of 200 and 360 of 360).
Decision procedure: total wins over the shared pool first; if the two differ by fewer than 10 of 330 games, the direct head to head decides. This rule was stated in the working session after the pool result was known and before the head to head was run; it was not written to a file beforehand, so the head to head is best read as the tie break it was.

| Y side, seeds 3000–3029, 30 games per opponent | GUARD=1, ENDGAME=0 (`main.zip`) | GUARD=2, ENDGAME=15 (`main5.zip`) |
| --- | ---: | ---: |
| v2 / v3 / Lv2 / rush / turtle / pack | 30 / 30 / 30 / 30 / 30 / 30 | 30 / 30 / 30 / 30 / 30 / 30 |
| cap7 | 30 | 29 |
| indep-v0 (`base`) | 5 | 8 |
| `front` / `pressure` (indep-v0 variants) | 1 / 0 | 1 / 1 |
| v6 (`indep1`) | 0 | 0 |
| **Total wins of 330** | **216** | **219** |
| Mean score margin | +11.6 | +11.9 |
| Largest own turn time measured by the runner (WSL, 5 games in parallel, so inflated) | 6.0 ms | 19.5 ms |

Pool result: a tie (difference 3 games). Head to head over seeds 3000–3099, both sides (200 games): **GUARD=1, ENDGAME=0 wins 151, 75.5 %** (as Y 68 of 100, as K 83 of 100), 95 % Wilson lower bound 69 %.
K side check, seeds 3000–3009 against v3, cap7, v6 and Lv2 (40 games each): 30 wins for both variants (10 against each earlier agent and Lv2, 0 against v6).

**Decision.** The variant of `main.zip` (GUARD=1, ENDGAME=0) is kept as the better verified final variant: equal on the pool, clearly ahead head to head, consistent with the author's own comment. The variant of `main5.zip` ranks second; its only differences are `GUARD = 2` and `ENDGAME = 15`. It is not discarded: its valid package `rebuilt-main5.zip` is kept as well.
Both are much stronger than v2, v3, cap7 and Lv2 but lose (almost) every game against the `indep` family, so this is a local result about a design that is not comparable to real team results.

## Recreate the rejected variant and re-run the comparison (WSL, repository root)

```sh
python - <<'EOF'
import pathlib, shutil
dst = pathlib.Path("out/_scratch-kakao/guard2-endgame15")          # git ignored scratch folder
shutil.copytree("out/v4-v5-provenance-uncertain/source", dst, dirs_exist_ok=True)
m = dst / "main.py"
b = m.read_bytes()
b = b.replace("GUARD = 1          # 건물당 기본 수비 인원".encode(), "GUARD = 2          # 건물당 기본 수비 인원".encode())
b = b.replace("ENDGAME = 0        # 마지막 몇 턴 수비 강화 (테스트 결과 끄는 게 더 강함)".encode(), "ENDGAME = 15       # 마지막 몇 턴은 수비 강화".encode())
m.write_bytes(b)          # must equal the main5.py inside main5.zip
EOF
bash out/tools/evaluation/wsl_run.sh --tag kakao-h2h --jobs 5 --seeds 3000-3099 --sides Y,K --save-replays lost \
  --cand g1e0="python3 out/v4-v5-provenance-uncertain/source/main.py" --opp g2e15="python3 out/_scratch-kakao/guard2-endgame15/main.py"
python3 bots/dist/starter/run_tests.py --zip out/v4-v5-provenance-uncertain/rebuilt-main.zip --seed 52
python3 bots/dist/starter/run_tests.py --zip out/v4-v5-provenance-uncertain/rebuilt-main5.zip --seed 52
python out/tools/evaluation/verify_artifacts.py
```

Build the two packages again (Windows Python at the repository root; the entry modes must not carry execute bits, so do not build them under WSL). The second command uses the scratch folder created by the recreate snippet above. The entries and their bytes come out the same as in the stored ZIPs; only the file dates stored in the ZIP differ.

```sh
python bots/dist/starter/make_submission.py --source out/v4-v5-provenance-uncertain/source --output out/_scratch-kakao/rebuilt-main.zip
python bots/dist/starter/make_submission.py --source out/_scratch-kakao/guard2-endgame15 --output out/_scratch-kakao/rebuilt-main5.zip
```

The stored rows name the candidates `g1e0` (kept) and `g2e15` (rejected) and refer to the scratch paths `out/_scratch-kakao/guard1-endgame0/` and `.../guard2-endgame15/` that were used at the time; the first is `source/` here.
For the pool, add `--opp` entries for v2, v3, cap7, v6, indep-v0, `front`, `pressure`, Lv2, rush, turtle and pack as in [`../experiments/7-independent-agent(v6)/README.md`](../experiments/7-independent-agent%28v6%29/README.md).
