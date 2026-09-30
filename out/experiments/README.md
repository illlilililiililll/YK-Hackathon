# Experiments

Local evaluation runs and the reports that explain them. The folders are numbered in chronological order, and the model they are mainly about is in parentheses (`v2`, `v3`, `v6` are site versions; `cap7` is the unsubmitted candidate in [`../v0-unsubmitted/`](../v0-unsubmitted/)). Each README starts with the primary model and lists the other models involved.
All results come from the official engine and runner against **stand in opponents** and do not prove win rates against real teams. Bulk per game replays are git ignored (regenerate them with the commands in each README); scripts, summaries (`summary.json`, `metrics.txt`, `results.jsonl`, `games.jsonl`, `result.json`) and selected failure cases (`failures/`, `cases/`) are tracked.

| # | folder | period (KST) | what | primary model | key outcome |
| ---: | --- | --- | --- | --- | --- |
| 1 | [`1-baseline-and-first-agent(v2)`](1-baseline-and-first-agent%28v2%29/) | 09-27 18:56–19:01 | official Lv2 self play baseline; the v1/v2 strategy against Lv1 and Lv2 | v2 | v1/v2 10–0 against Lv2 on both sides |
| 2 | [`2-flag-cap-sweep(v3)`](2-flag-cap-sweep%28v3%29/) | 09-28 10:25–11:20 | flag bearer cap 4, 5, 6, 8 against v2's 12, which gave v3 | v3 | 6 flags: v2 2W–8L → 4W–6L against the stand in; 4, 5, 8 rejected |
| 3 | [`3-policy-weight-search(cap7)`](3-policy-weight-search%28cap7%29/) | 09-28 15:51–16:06 | six weight search on v3, which gave cap7 (1,030 games) | cap7 | unused Y games 68 → 74 of 120; cap7 not uploaded |
| 4 | [`4-code-evolution(cap7)`](4-code-evolution%28cap7%29/) | 09-28 from 18:00 | two generations of seven code candidates incl. a from scratch agent (566 games) | cap7 (incumbent) | no promotion; cap7 kept |
| 5 | [`5-weight-search-rounds(cap7)`](5-weight-search-rounds%28cap7%29/) | 09-28 22:00 → 09-29 11:26 | three bounded weight search rounds, one after each new public match round | cap7 (incumbent) | no adoption in 619 games |
| 6 | [`6-decision-policies(cap7)`](6-decision-policies%28cap7%29/) | 09-29 02:58–11:04 | defence and escort, adaptive production, combined (294 games) | cap7 (incumbent) | all rejected; single turn counterfactuals on official games 31 and 34 |
| 7 | [`7-independent-agent(v6)`](7-independent-agent%28v6%29/) | 09-29 11:53–15:32 | blind independent agent `indep-v0` → `indep1` (the submitted v6), then the Codex consolidation | v6 | v6: 100–0 against earlier agents; 30/40 against warrior heavy stand ins |
| 8 | [`8-round-0929-2200(opus)`](8-round-0929-2200%28opus%29/) | 09-30 03:20–05:00 | attribution (command replay) and loss analysis of the 9/29 22:00 round (games 48–59, v6 code); new opponent `escort`; defence, endgame, flag cap and garrison variants of v6 with held-out seeds | v6 → `v6-endgame20` | defence rejected; endgame 20 turns 56–44 vs v6 held out, adopted locally (not uploaded) |
| 9 | [`9-midgame-policy-search(opus)`](9-midgame-policy-search%28opus%29/) | 09-30 12:00–13:10 | games 60–71 (v6 code) and the warrior orders before each official flip; opponents chosen by the official loss signature; hold / far-hunt / reinforcement hypotheses on v6-endgame20 with a pre-registered plan and an untouched final (≈13,000 games) | `v6-endgame20` → + no far hunting | only `hunt_r=1` survived: 73% → 82% paired points over six challenging opponents, both sides; flips not reduced; adopted locally (not uploaded) |
| — | `local-runs/` | — | default output folder of the evaluation tools (created on first use; git ignored) | — | — |

**Why this order.** The numbers follow the first evidence of each experiment (file times of the original run folders and the entries of [`../DEVELOPMENT_LOG.md`](../DEVELOPMENT_LOG.md)). Experiments 5 and 6 overlap in time: the first weight search round ran on 09-28 22:00, the decision policy work started at 02:58 on 09-29 and ended before the third round finished (11:26).
Two related sets sit elsewhere: the comparison of the two received `main.zip` / `main5.zip` sources is in [`../v4-v5-provenance-uncertain/`](../v4-v5-provenance-uncertain/) (comparison rows, not an experiment folder), and the analysis of the 47 official matches is [`../OFFICIAL_MATCH_ANALYSIS.md`](../OFFICIAL_MATCH_ANALYSIS.md).

## Conventions

- Folder names contain parentheses, so quote them in shell commands (for example `"out/experiments/2-flag-cap-sweep(v3)/README.md"`); Markdown links write them as `%28` and `%29`. Python scripts inside the experiment folders import their neighbours directly (`from evolve import …`); nothing imports them as packages.
- Tools live in [`../tools/`](../tools/): `evaluation/` runs games, `reporting/` builds tables and checks. Fixed local opponents (`rush`, `turtle`, `raider`, `pack`, `escort`) are in [`../opponents/`](../opponents/).
- The official runner needs Linux pipes; on Windows use WSL for subprocess matches (`wsl_run.sh`, `subprocess_eval.py`) and Windows Python for in process matches (`inproc.py`, `policy_search.py`, `weight_search.py`, and the `evaluate.py` of experiment 6).
- Do all timing checks with `--jobs 1`; parallel runs and the `/mnt/c` mount inflate turn times and can cause spurious first turn forfeits.
- Old paths in stored data (`cmd` strings inside `results.jsonl`, `args` inside `summary.json`, `source` paths inside `generation-*.json` of experiment 4) are historical and were not rewritten; the map is [`../PATH_MAP.md`](../PATH_MAP.md).
- `7-independent-agent(v6)/phase1-blind-build/p1-v0-stderr.log` (the `KeyError` tracebacks that show the defect) had the absolute local path prefix in its stack frames replaced by `<repo>/` before publication; nothing else in it was changed.
- The historical reports in experiment 7 (`STRATEGY.md`, `PHASE*.md`, the audit, the consolidation plan; the plans are the pre registered ones) were edited only for moved paths and for hyphens in prose; no number or statement was changed.
- Ignored, regenerable output can be deleted safely with `git clean -fdX out/experiments` (review with `git clean -ndX out/experiments` first).
