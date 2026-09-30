# Baseline and v1/v2 local runs (2026-09-27, Codex)

**Models.** Primary: **v2** (Codex). Also: v1 (the same strategy, submitted first with a packaging defect; see [`../../v1-v2-codex/`](../../v1-v2-codex/)) and the official Lv1 and Lv2 examples as opponents.

Official engine and runner, seeds 0–9, WSL Python 3.14.4 (server 3.12.14), 0 forfeits in every run. The candidate is the v1/v2 strategy: `out/v1-v2-codex/source/main.py` is byte identical to the file that was `bots/dist/starter/python/main.py` when these runs were made (the stored `summary.json` still names that old path).

| run (folder) | candidate vs opponent, side | W · D · L | mean final score (Y:K) | mean buildings·value at turn 20 → end | max turn ms (WSL) |
| --- | --- | ---: | --- | --- | ---: |
| `baseline-lv2-self-Y` | official Lv2 vs official Lv2, Y | 0·10·0 | 14.3 : 14.3 | 7.0·172.9 → 6.9·1052 | 94.4 |
| `v1-vs-lv1-Y` | v1/v2 vs official Lv1, candidate Y | 10·0·0 | 34.8 : 0 | 14.0·290.4 → 15.6·360.3 | 79.3 |
| `v1-vs-lv2-Y` | v1/v2 vs official Lv2, candidate Y | 10·0·0 | 34.2 : 0 | 11.8·254.0 → 15.1·564.0 | 87.8 |
| `v1-vs-lv2-K` | v1/v2 vs official Lv2, candidate K | 10·0·0 | 34.2 : 0 | 12.8·255.5 → 15.3·632.0 | 111.0 |

What they showed: the official Lv2 sends several flag bearers to the same nearest building, so Lv2 against itself stalls (all 10 games drawn at 160 turns, centre buildings left neutral in seed 0). One flag bearer per building, forward production at a hospital and warriors chasing enemy flags beat it on both sides.
The very first code of v1 forfeited on its first turn in all 10 games (a `sorted()` generator syntax error); the fixed version is the one measured here. Saturated wins against Lv1/Lv2 say nothing about real teams (see [`../../OFFICIAL_MATCH_ANALYSIS.md`](../../OFFICIAL_MATCH_ANALYSIS.md)).

Each folder holds `summary.json`, `metrics.txt` (`local_metrics.py` output) and, locally, `replays/seed-N.json` (git ignored, regenerable).

## Regenerate (WSL, repository root)

```sh
python3 out/tools/evaluation/subprocess_eval.py bots/dist/starter/python/example_lv2.py bots/dist/starter/python/example_lv2.py --side Y --seeds 10 --name baseline-lv2-self-Y
python3 out/tools/evaluation/subprocess_eval.py out/v1-v2-codex/source/main.py bots/dist/starter/python/example_lv1.py --side Y --seeds 10 --name v1-vs-lv1-Y
python3 out/tools/evaluation/subprocess_eval.py out/v1-v2-codex/source/main.py bots/dist/starter/python/example_lv2.py --side Y --seeds 10 --name v1-vs-lv2-Y
python3 out/tools/evaluation/subprocess_eval.py out/v1-v2-codex/source/main.py bots/dist/starter/python/example_lv2.py --side K --seeds 10 --name v1-vs-lv2-K
python out/tools/reporting/local_metrics.py out/experiments/local-runs/v1-vs-lv2-Y     # -> the metrics.txt line
```

Output goes to `out/experiments/local-runs/<name>/` (git ignored scratch) unless `--outdir` is given.
