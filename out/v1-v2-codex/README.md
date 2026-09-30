# v1 and v2 — one strategy, two submissions (strategy by Codex)

v1 and v2 contain **byte identical** entries (same `main.py`, same helper files). They differ only in the file modes stored in the ZIP: v1 was built under WSL and every entry carried an execute bit, so the server rejected it; v2 was rebuilt from the same source with Windows Python and passed.
The shared source is stored once, in [`source/`](source/). Only the accepted ZIP is kept; the rejected one is rebuilt exactly from that source and [`v1-zip-manifest.json`](v1-zip-manifest.json).

| | v1 | v2 |
| --- | --- | --- |
| Uploaded file name | `y-agent-v1.zip` | `y-agent-v2.zip` (kept here as [`v2.zip`](v2.zip)) |
| Submitted (KST) | 2026-09-27 19:06 | 2026-09-27 19:07 |
| Submission ID | not shown (the rejection message appeared before any build log object existed) | `01a0e255-952c-722e-bb97-1c9baba1287c` (UUID in the object key of its build log; for v6 the same rule gives the recorded ID) |
| ZIP size | 9,177 bytes | 9,177 bytes |
| ZIP entries | 9, identical bytes to v2 | 9: `_generated.py`, `campus_bot.py`, `example_lv1.py`, `example_lv2.py`, `main.py`, `mybot_template.py`, `protocol.py`, `search.py`, `submission.json` |
| Entry mode | **`0o100777`** (execute bit) | `0o100666` |
| Built with | official `make_submission.py`, WSL Python 3.14 | the same packager, Windows Python 3.12.7 |
| Server result | **rejected**: status `수정 필요`, reason `EXECUTABLE_FILE` (`executable files are not allowed`); cannot be selected, so no practice battle | status `사용 가능`; it was shown as the competition code at that time; local checker `ok: true`, 16 turn win |
| Official medium bot practice (Y) | not possible | 2026-09-27 19:08: **10 wins, 0 draws, 0 losses** |
| Official team matches | none | games 01–19: **4 wins, 15 losses** ([`../OFFICIAL_MATCH_ANALYSIS.md`](../OFFICIAL_MATCH_ANALYSIS.md)) |
| Old names | `out/v1-codex/y-agent-v1.zip` (deleted, see below) | `out/v2-codex/y-agent-v2.zip`, `candidates/existing/v2/` |

Shared entries: `main.py`; the other eight entries are the official kit files (`campus_bot.py`, `protocol.py`, `search.py`, `_generated.py`, the two examples, the template, `submission.json`). The per entry details of the v1 ZIP (names, sizes, modes, dates) are in the manifest.

## How the v1 ZIP was consolidated

The v1 ZIP was deleted from the repository because it is a redundant copy: `python out/tools/evaluation/verify_artifacts.py` rebuilds it from `source/` and the manifest (entry order, stored dates, mode `0o100777`, create system 3, deflate) and compares the result with the uploaded file's identity recorded in the manifest.
This reproduced the uploaded file **bit for bit** on Windows Python 3.12.7, so nothing was lost. The ZIP bytes depend on the zlib build; on another platform the script reports a difference in the compressed bytes as a warning and checks the entries and modes instead.
The demonstration that the local checker misses the problem still works on any ZIP with execute bits: `python out/tools/evaluation/zip_modes.py <zip>` exits non zero, while `run_tests.py --zip` printed `ok: true` for v1.

## How it was developed

Started from the official Lv2 example, which sends many flag bearers (F) to the same nearest building and stalls in the centre. Changes: one F per building (chosen by distance minus building value), forward production at an owned hospital, and warriors (W) that go after enemy flags.
The first version forfeited on its first turn in all 10 initial local games (a generator expression syntax error) and was fixed before any submission. Behaviour: F cap `min(12, len(targets)+2)` filled first, the rest of the resources spent on W;
all W stacks chase the nearest enemy F (otherwise centre buildings); no escort, no garrison; capture reserve 4 (2 when the central plaza is owned).

## Decisive results and limitations

- Local (seeds 0–9, official runner): 10–0 versus Lv2 on both sides and versus Lv1, no forfeit ([`../experiments/1-baseline-and-first-agent%28v2%29/`](../experiments/1-baseline-and-first-agent%28v2%29/)).
- Official: passes the medium bot practice but loses to warrior heavy teams: 4 wins and 15 losses over 19 public games (1 win and 15 losses against opponents that had at least 30 warriors at turn 20).
- It fills 12 flags first and therefore has fewer warriors than the opponents at turns 10–20; the change tried next is [`../v3-codex/`](../v3-codex/). The practice result says nothing about real teams.

## Verify

```sh
python out/tools/evaluation/verify_artifacts.py           # v2 ZIP == source, v1 ZIP rebuilt from the manifest
wsl --cd <repo> python3 bots/dist/starter/run_tests.py --zip out/v1-v2-codex/v2.zip     # official local checker
```
