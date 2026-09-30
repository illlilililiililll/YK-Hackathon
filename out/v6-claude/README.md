# v6 — the submitted `indep1` agent (strategy by Claude)

> **This folder is the code that was uploaded to the competition site as submission v6.** [`v6.zip`](v6.zip) is the exact uploaded file (the local file was renamed from `y-agent-indep1-20260929.zip`; the bytes did not change) and
> `source/` is the source it was built from (all six ZIP entries are byte identical to `source/`). It is **not** the code selected for the competition:
> at the last recorded check (2026-09-29 15:41 KST) the site's competition code selection was **v5**, whose source is not in this repository, and v6 must not be assumed to equal v5.

| item | value |
| --- | --- |
| Server submission | **v6**, ID `01a0ebe3-3f4b-74c5-9a44-d57b14b70ab2`, 2026-09-29 15:38 KST, Python 3.12, status `사용 가능` |
| Uploaded as | file name `y-agent-indep1-20260929.zip` (this is how the site lists it), submission ID above |
| ZIP | [`v6.zip`](v6.zip) — 10,465 bytes; the entry names inside are unchanged (`main.py`, `submission.json`, `brain.py`, …) |
| Source | [`source/`](source/) — `main.py` and `brain.py` are the strategy; `campus_bot.py`, `protocol.py`, `_generated.py` and `submission.json` are the unmodified official helpers |
| ZIP properties | built with the official `make_submission.py` under **Windows Python 3.12.7**; every entry mode `0o100666` (no execute bit); only the six files at the ZIP root |
| Strategy developed by | **Claude Sonnet 5.5** (blind independent design, then improvement; internal name `indep1`). Packaged, re-verified and submitted by Codex — [`../PROMPT_RECORD.md`](../PROMPT_RECORD.md) |
| Official practice battle | 2026-09-29 15:41 KST, medium bot, Y side: **10 wins, 0 draws, 0 losses**, completion criterion met; server diagnostics `정상 실행`, 43 recorded turn responses, mean 25 ms (the result screenshot is not in the repository) |
| Official matches vs other teams | none recorded in this repository |
| Old names | `candidates/indep1/` → `source/`; `out/y-agent-indep1-20260929.zip`, then `out/v6-claude/y-agent-indep1-20260929.zip` → `v6.zip`; `out/indep/y-agent-indep1.zip` was a byte identical duplicate and was removed |

`source/` files keep the CRLF line endings they were submitted with, and [`/.gitattributes`](../../.gitattributes) (`out/** -text`) makes Git store exactly these bytes.
Renaming the local ZIP does not obscure its identity: the uploaded file name and the submission ID identify it. Do not rebuild it for submission purposes (see the end of this file).

## How it was developed

1. **`indep-v0`** ([`../v0-unsubmitted/indep-v0-claude/`](../v0-unsubmitted/indep-v0-claude/)) — designed from the rules only, before reading any earlier agent: canonical frame (K rotated 180°), warriors (W) first with a small flag bearer (F) force (cap 4/3), F moves only where enough W escort it, W chase enemy flags. Fixed assumptions and pass/fail criteria were written before any code ([`STRATEGY.md`](../experiments/7-independent-agent%28v6%29/STRATEGY.md)).
2. **Analysis** of the 47 official replays showed that the losses were mostly *unopposed, escorted enemy flags neutralising buildings* while ~10 of our W stood within 3 cells ([`../OFFICIAL_MATCH_ANALYSIS.md`](../OFFICIAL_MATCH_ANALYSIS.md) §3.4).
3. **Improvement**, one hypothesis at a time with a pre-registered accept/reject protocol ([`PHASE3_PLAN.md`](../experiments/7-independent-agent%28v6%29/PHASE3_PLAN.md)): kept `garrison=1` (one W stays on each owned building), `hunt_r=6` (chase enemy flags from up to 6 steps), flag cap 10/8, and hospital forward spawn; rejected larger garrisons and flag cap 12/10. The chosen parameters were baked into `brain.py` with [`bake_params.py`](../tools/evaluation/bake_params.py) (environment variable variant and baked source: 80/80 identical draws).
4. **Codex consolidation** re-tested it against two new stand in opponents built from the official loss observations and rebuilt the ZIP (identical bytes), then submitted it.

## Decisive results (local; not evidence about real teams)

| test | result |
| --- | --- |
| Hold-out, unseen seeds 1000–1099, Y side, vs earlier agents | **100–0 vs v2, v3, cap7; 99–1 vs `indep-v0`** (K side 179/180) |
| Consolidation, unused seeds 2100–2119, vs warrior heavy stand ins `front`/`pressure` (40 games) | `indep1` **30/40**, `indep-v0` 3/40, cap7 0/40; K check (10 games) 6 / 1 / 0 wins; 0 forfeits; max ordinary turn 22 ms |
| Official ZIP check (WSL, Python 3.14.4), seed 52 | `ok: true`, no issues/warnings, 12 turns 21:0, stderr 0, max turn stdout 341 B / 22 lines |
| Timing / memory (Windows Python 3.12.7, separate process) | max ordinary turn 45 ms, first turn 957 ms, peak memory 14.6 MiB |

## Limitations

- **No local opponent reproduces the official record** of v2/v3 (v3 is 100% against all styled bots locally but 8W–20L officially); self-play among our own variants may reward exploiting the baseline's weakness (too few flags).
- The macro is only at parity with the real K bots (about 69 vs 67 W at turn 20) and it keeps ~10 F where they keep ~7; buildings first (`indep1`) versus warriors first (`indep-v0`) **cannot be separated with local data**.
- The 1-warrior garrison does not stop the raids seen in official losses, where 67% of building flips had enemy warriors (mean 8) on the building.
- Selection among 7–8 variants on 100-seed sets carries a winner's curse risk; the hold-out confirms superiority only over our own and earlier bots.
- Losses on the unused final seeds are kept as replays in [`../experiments/7-independent-agent(v6)/consolidation/failures/`](../experiments/7-independent-agent%28v6%29/consolidation/failures/); the one hold-out loss is in [`.../holdout/failures/`](../experiments/7-independent-agent%28v6%29/holdout/failures/).

## Verify

```sh
python out/tools/evaluation/verify_artifacts.py                                   # ZIP entries == source, no execute bits
python out/tools/evaluation/zip_modes.py out/v6-claude/v6.zip
wsl --cd <repo> python3 bots/dist/starter/run_tests.py --zip out/v6-claude/v6.zip --seed 52   # official checker (needs Linux pipes)
python out/tools/evaluation/inproc.py --y v6 --k lv2 --seed 3                     # in-process match on Windows
```

Do not rebuild the ZIP for submission purposes: `make_submission.py` stores file modification times, so a rebuild changes the bytes even with identical sources.
