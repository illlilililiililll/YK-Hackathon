# Independent agent (Claude Sonnet 5.5) and the Codex consolidation — 2026-09-29

**Models.** Primary: **v6** (`indep1`). Also: **indep-v0** (the baseline, [`../../v0-unsubmitted/indep-v0-claude/`](../../v0-unsubmitted/indep-v0-claude/)), cap7, v3 and v2 (earlier agents used as opponents), the local variants `front` and `pressure`, the official Lv1 and Lv2, and the fixed opponents rush, turtle, raider and pack.

Everything here produced [`../../v0-unsubmitted/indep-v0-claude/`](../../v0-unsubmitted/indep-v0-claude/) (the baseline) and the submitted **[v6](../../v6-claude/)** (`indep1`). Results are local (official engine and runner, WSL Python 3.14.4)
and **do not prove win rates against real teams**. Nothing here uploaded anything, ran a practice battle or changed the competition code selection; the later, separate submission of v6 is described in [`../../DEVELOPMENT_LOG.md`](../../DEVELOPMENT_LOG.md).

## Reading order

| file | content |
| --- | --- |
| [`STRATEGY.md`](STRATEGY.md) | assumptions and pass/fail criteria written **before any agent code** (pre-registered) |
| [`PHASE1_REPORT.md`](PHASE1_REPORT.md) | blind build `indep-v0`, blindness statement, source identity, Phase 1 results and defects |
| [`phase2-analysis/PHASE2_REPORT.md`](phase2-analysis/PHASE2_REPORT.md) (+ [`prior_experiments_audit.md`](phase2-analysis/prior_experiments_audit.md)) | analysis of the official replays and an audit of the earlier local experiments; its match findings are merged into [`../../OFFICIAL_MATCH_ANALYSIS.md`](../../OFFICIAL_MATCH_ANALYSIS.md) |
| [`PHASE3_PLAN.md`](PHASE3_PLAN.md) | accept/reject protocol fixed before the runs (seed sets, hypotheses H1–H4) |
| [`PHASE3_REPORT.md`](PHASE3_REPORT.md) | iterations, hold-out, failure analysis, validation of the frozen source/ZIP, selection, limitations |
| [`consolidation/consolidation-plan-20260929.md`](consolidation/consolidation-plan-20260929.md) | Codex's pre-registered re-check with two new stand in opponents (below) |

## Folder layout

| folder | runs | seeds |
| --- | --- | --- |
| `phase1-blind-build/` | `p1-*` sweeps, mirror, serial timing, K side, `sanity` (`failures/` = the 14 `p1-v0-sweep` losses caused by the `KeyError` of the pre-fix code, which exists nowhere else, and the 21 `p1-v0-a` games with spurious `/mnt/c` forfeits; neither set can be regenerated) | 0–29 |
| `phase2-analysis/` | `p2-*` big sweeps of `indep-v0` vs v3/cap7 (+ `official_analysis.*`, `loss_geometry.txt`, `failures/` = the 8 losses) | 30–129 |
| `phase3-selection/` | design (`p3-design-A`), head to head, round robins, regression, bake check | 30–129, 200–599 |
| `holdout/` | final round robin `hold-rr`, K side, styled opponents, serial timing (`failures/` = the one loss) | 1000–1099 |
| `consolidation/` | Codex selection / final / symmetry runs (`failures/` = `indep1`'s losses on the unused seeds) | 2000–2119 |

Each run folder holds `results.jsonl` (one JSON per game: outcome, score, margin, timeline at turns 10/20/40/80/120/160, timing; the `cmds`/`cmd` strings inside old rows are historical and use the pre-cleanup paths) and `summary.txt`
(plus derived tables such as `matrix.txt`, `h2h.txt`, `compare.txt`, `table.md`). `replays/*.json.gz` (losses; all games for `p1-v0c-serial`) are **git ignored bulk output** and can be regenerated with the commands below.
Old to new mapping: [`../../PATH_MAP.md`](../../PATH_MAP.md) (`out/indep/<run>` → `out/experiments/7-independent-agent(v6)/<phase>/<run>`).

## Consolidation result (Codex, unused final seeds 2100–2119, Y side, 40 games per candidate)

Opponents `front` and `pressure` are **local variants of the independent baseline** built from official loss observations, not replicas of any team:
`front` = `INDEP_PARAMS=fcap_early=6,fcap_late=6,garrison=1,garrison_alert=7,hunt_r=6,hospital_spawn=1`, `pressure` = `INDEP_PARAMS=fcap_early=6,fcap_late=5,garrison=0,hunt_r=6,hospital_spawn=1`.

| Y candidate | selection seeds 2000–2019 (40) | **unused final seeds 2100–2119 (40)** | mean score diff | building diff | unit value diff | forfeits / max ordinary turn |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| **`indep1` (v6)** | 29·0·11 | **30·0·10** (`front` 13·0·7, `pressure` 17·0·3) | +13.8 | +6.0 | +202 | 0 / 22 ms |
| `indep-v0` (`base`) | 1·0·39 | 3·0·37 | −21.9 | −10.1 | −330 | 0 / 28 ms |
| cap7 | 0·0·40 | 0·0·40 | −33.0 | −15.1 | −462 | 0 / 14 ms |

K side symmetry (seeds 2100–2104 × 2 opponents = 10 games): `indep1` 6·0·4, `indep-v0` 1·0·9, cap7 0·0·10. Counter-examples: `pressure` seed 2104 — `indep-v0` won by 19, `indep1` lost by 11; `front` seed 2117 — `indep1` led 10:7 in buildings at turn 40 and lost 3:36.
Raw records: `consolidation/consolidate-{select,final,symmetry}/results.jsonl`. The earlier claim "399/400" was re-derived from `holdout/hold-rr/results.jsonl` (indep1 as Y over seeds 1000–1099: 100 / 100 / 100 / 99 wins vs v2 / v3 / cap7 / `indep-v0`).

## Reproduce (Windows host; the official runner's pipes need Linux, so matches run in WSL)

Local replays are deterministic: a stored game re-run with the same command gives the same commands, orders, events and per turn states (checked in the cleanup on 10 Codex flag cap games, on the one hold-out loss at seed 1000, and on all 40 Phase 1 `p1-v0c-serial` games, which the parametrised `indep-v0` source reproduced with 0 differing result rows).

```powershell
# one game from the hold-out: indep1 (Y) vs the baseline, seed 1000 (stored result: loss 14:23, 160 turns)
wsl --cd <repo> bash out/tools/evaluation/wsl_run.sh --tag repro-hold1000 `
  --cand indep1="python3 out/v6-claude/source/main.py" `
  --opp base="python3 out/v0-unsubmitted/indep-v0-claude/source/main.py" --seeds 1000 --sides Y --jobs 1 --save-replays none
#   -> out/experiments/local-runs/repro-hold1000/results.jsonl  (git-ignored scratch folder)

# the consolidation final set (Y, seeds 2100-2119)
wsl --cd <repo> bash out/tools/evaluation/wsl_run.sh --tag repro-final --jobs 1 --seeds 2100-2119 --sides Y --save-replays lost `
  --cand indep1="python3 out/v6-claude/source/main.py" `
  --cand base="python3 out/v0-unsubmitted/indep-v0-claude/source/main.py" `
  --cand cap7="python3 out/v0-unsubmitted/cap7-codex/source/main.py" `
  --opp front="INDEP_PARAMS=fcap_early=6,fcap_late=6,garrison=1,garrison_alert=7,hunt_r=6,hospital_spawn=1 python3 out/v0-unsubmitted/indep-v0-claude/source/main.py" `
  --opp pressure="INDEP_PARAMS=fcap_early=6,fcap_late=5,garrison=0,hunt_r=6,hospital_spawn=1 python3 out/v0-unsubmitted/indep-v0-claude/source/main.py"

# tables from any results.jsonl
python out/tools/reporting/final_table.py --files "out/experiments/7-independent-agent(v6)/consolidation/consolidate-final/results.jsonl" --cands indep1,base,cap7 --opps front,pressure --side Y --seeds 2100-2119
python out/tools/reporting/compare.py <results.jsonl> --base base            # paired stats
python out/tools/reporting/trace.py "out/experiments/7-independent-agent(v6)/holdout/failures/indep1-Y-vs-base-s1000.json.gz" --from 1 --to 25   # turn-by-turn view
python out/tools/evaluation/inproc.py --y v6 --k lv2 --seed 3                  # in-process match on Windows (shows exceptions and decide() time)
```

Notes: never rewrite `wsl_run.sh` while a run uses it (bash reads scripts incrementally). Timing gates (`max ms`) are only valid from `--jobs 1` runs; parallel runs inflate them (and on `/mnt/c` cause spurious first turn forfeits — that is why `wsl_run.sh` mirrors the repository to `~/ykrun`).
Candidate variants are made without editing code by prefixing the command with `INDEP_PARAMS=k=v,...`; `out/tools/evaluation/bake_params.py` bakes such overrides into a copy of the source (that is how `v6-claude/source/` was produced from `indep-v0-claude/source/`).
