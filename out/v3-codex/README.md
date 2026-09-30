# v3 — flag cap 12 → 6 (strategy by Codex)

| item | value |
| --- | --- |
| Server submission | **v3** (submission #3), 2026-09-28 11:24 KST, Python 3.12, `사용 가능`; later shown on the site as the competition code (that selection was not made by an AI session) |
| Uploaded as | file `y-agent-v3.zip`; submission #3 on the site, ID `01a0e5d4-21d7-71f6-af7d-6cbb85b5caf0` (UUID in the object key of its build log); kept here as [`v3.zip`](v3.zip) |
| ZIP | 9,177 bytes; Windows Python 3.12.7, entry mode `0o100666`; the entry names inside are unchanged (`main.py`, `submission.json`, …) |
| Source | [`source/`](source/) = the ZIP contents. `main.py` differs from v2's only in `min(12, len(targets) + 2)` → `min(6, len(targets) + 2)` |
| Live copy | `bots/dist/starter/python/main.py` in the working tree is byte identical to `source/main.py`; it is part of the official kit directory and was left there on purpose (several scripts load it) |
| Strategy developed by | **Codex** (GPT-6 family) — [`../PROMPT_RECORD.md`](../PROMPT_RECORD.md) |
| Local check | [`local-submission-check.json`](local-submission-check.json): official `run_tests.py --zip` (WSL, Python 3.14.4) `ok: true`, no issues/warnings, 16-turn win, stdout ≤ 315 B / 19 lines per turn, stderr 0 |
| Old names | `out/y-agent-v3.zip`, then `out/v3-codex/y-agent-v3.zip` → `v3.zip`; `candidates/existing/v3/` → `source/`; `out/v3-local-submission-check.json` → `local-submission-check.json` |
| Practice battle | 2026-09-28 11:25, medium bot, Y: **10-0-0** (the result screenshot is not in the repository) |
| Official matches vs other teams | games 20–47: **8W–20L** ([`../OFFICIAL_MATCH_ANALYSIS.md`](../OFFICIAL_MATCH_ANALYSIS.md)) |

## How it was developed

Hypothesis from the 19 public v2 games: v2 fills 12 flag bearers before making warriors, so it is behind in warriors at turn 10–20. One line was changed and the cap sweep was run on identical seeds
against a stand in opponent with a 6-flag cap: v2 2W–8L → 6-flag 4W–6L, and 9W–1L against v2 itself. Caps 4, 5 and 8 were rejected (each turned at least one v2 win into a loss).
Details, commands and the stored regression replays: [`../experiments/2-flag-cap-sweep(v3)/`](../experiments/2-flag-cap-sweep%28v3%29/).

## Decisive results and limitations

- Official: 8W–20L (v2: 4W–15L). The difference is **not statistically distinguishable** (Fisher p = .74); 11 of the 12 losses in the 9/28 22:00 round and 6 of 8 in the 9/29 10:00 round still show a warrior deficit at turn 20.
- Local descendants of this code (weight search, evolution, decision policies) found no adoptable improvement except the never uploaded [`cap7`](../v0-unsubmitted/cap7-codex/).
- Practice battle wins say nothing about real teams.

## Verify

```sh
python out/tools/evaluation/verify_artifacts.py
wsl --cd <repo> python3 bots/dist/starter/run_tests.py --zip out/v3-codex/v3.zip
```
