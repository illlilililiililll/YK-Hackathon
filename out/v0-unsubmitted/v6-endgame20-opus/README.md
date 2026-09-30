# v6-endgame20 lineage — current version: no far hunting (Claude Opus 5.5, 2026-09-30) — best verified local candidate, never uploaded

History of this folder:
1. **v6-endgame20** (09-30 04:24, experiment 8): v6 with a 20-turn endgame rule (flag targets count if reached by turn 160, no far
   hunting in the last 20 turns). Frozen byte for byte, source and ZIP, in [`../v6-endgame20-frozen-opus/`](../v6-endgame20-frozen-opus/).
2. **current, `hunt_r=1`** (09-30, experiment 9): the same source with far hunting of enemy flags switched off for the whole game
   (`source/brain.py` differs from the frozen source in one line, baked with `tools/evaluation/bake_params.py`). The endgame code path is unchanged.

Evidence ([`experiments/9-midgame-policy-search(opus)/`](../../experiments/9-midgame-policy-search%28opus%29/)): untouched seeds, both sides,
six challenging local opponents (two never used in search): 1,317 → 1,476 of 1,800 paired points against the frozen v6-endgame20
(378 better / 219 worse pairs, p < 0.001), every opponent better on both sides, v6 head to head 63%, regression pool unchanged (898 vs 897
of 900), 0 forfeits. It does not reduce own-building flips; it keeps warriors with the main group, which holds more production and
score-turns; the opponent is slightly ahead at T20. This is a local result; the official effect is unknown.

| file | what |
| --- | --- |
| `source/` | the agent (official helpers unchanged; `main.py` as in v6) |
| `v6-endgame20-nofar.zip` | built with the official packager on Windows Python 3.12.7; 11,200 bytes; 6 entries, all mode 0o100666 |
| `local-zip-check.json` | official `run_tests.py --zip … --seed 52` (WSL): `ok: true`, no issues or warnings, stderr 0 |

Other checks: `run_tests.py --zip` also on seeds 3 and 16 (ok); serial games under WSL Python 3.14 and Windows Python 3.12.7: ordinary turn
at most 3.6 ms, first turn at most 248 ms, identical outcomes on both interpreters. Before any upload, check the site's schedule and current
selection; build the ZIP only with Windows Python (a WSL build gets execute bits and the server rejects it).
