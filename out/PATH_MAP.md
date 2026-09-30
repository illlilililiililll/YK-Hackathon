# Old to new path map

Two cleanups moved files. Both were recorded before the first move (inventory of every file) and generated from the actual moves; nothing is unaccounted for.
[`path_map.tsv`](path_map.tsv) lists every file of both inventories: the 1311 files of `out/` and `candidates/` before cleanup 1 (`origin` = `original`), the files that cleanup 1 created and cleanup 2 then moved or deleted (`origin` = `cleanup 1`), and the files created since (empty `old_path`).
The last state of every path is in `final_path` (empty = not moved); intermediate names are only in the tables below.

## Candidates and ZIPs

| candidate | uploaded file name | old local paths | now |
| --- | --- | --- | --- |
| **v1** (rejected upload) | `y-agent-v1.zip` | `out/y-agent-v1.zip` → `out/v1-codex/y-agent-v1.zip` | not stored: rebuilt bit for bit by `tools/evaluation/verify_artifacts.py` from [`v1-v2-codex/source/`](v1-v2-codex/source/) and [`v1-zip-manifest.json`](v1-v2-codex/v1-zip-manifest.json) |
| **v2** | `y-agent-v2.zip` | `out/y-agent-v2.zip` → `out/v2-codex/y-agent-v2.zip`; `candidates/existing/v2/` | [`v1-v2-codex/v2.zip`](v1-v2-codex/v2.zip), `source/` |
| **v3** | `y-agent-v3.zip` | `out/y-agent-v3.zip` → `out/v3-codex/y-agent-v3.zip`; `candidates/existing/v3/`; `out/v3-local-submission-check.json`; working tree `bots/dist/starter/python/main.py` (unchanged) | [`v3-codex/v3.zip`](v3-codex/v3.zip), `source/`, `local-submission-check.json` |
| **v6 = `indep1`** | `y-agent-indep1-20260929.zip` | `out/y-agent-indep1-20260929.zip` → `out/v6-claude/y-agent-indep1-20260929.zip`; `candidates/indep1/`; `out/indep/y-agent-indep1.zip` (byte identical duplicate, deleted) | [`v6-claude/v6.zip`](v6-claude/v6.zip), `source/` |
| **cap7** (never uploaded) | none (local `y-agent-cap7-low-review.zip`) | `out/y-agent-cap7-low-review.zip` → `out/unsubmitted/cap7-codex/y-agent-cap7-low-review.zip`; `candidates/existing/cap7/`; `out/policy-search/candidate-python/` (duplicate, deleted); `out/evolution/candidates/cap7.py` (kept as lineage) | [`v0-unsubmitted/cap7-codex/cap7.zip`](v0-unsubmitted/cap7-codex/cap7.zip) |
| **indep-v0 / `base`** (never uploaded) | none (local `y-agent-indep-v0.zip`) | `candidates/indep/`; `out/indep/y-agent-indep-v0.zip` → `out/unsubmitted/indep-v0-claude/y-agent-indep-v0.zip` | [`v0-unsubmitted/indep-v0-claude/indep-v0.zip`](v0-unsubmitted/indep-v0-claude/indep-v0.zip) |
| **v6-endgame20** (never uploaded) | none (local `v6-endgame20.zip`) | `out/v0-unsubmitted/v6-endgame20-opus/` (experiment 8; that folder now holds experiment 9's successor, `v6-endgame20-nofar.zip`) | [`v0-unsubmitted/v6-endgame20-frozen-opus/v6-endgame20.zip`](v0-unsubmitted/v6-endgame20-frozen-opus/v6-endgame20.zip), `source/` (byte identical copy) |
| v4, v5 | `y-agent-v4.zip` (11.6 KiB), `v-agent-v4.zip` (11.2 KiB) | none: never in this workspace | **no source**; two received look alike sources, identity unproven: [`v4-v5-provenance-uncertain/`](v4-v5-provenance-uncertain/) |
| `main.zip` / `main5.zip` (received via KakaoTalk, outside the repository) | none | `Documents/카카오톡 받은 파일/` (read only, unchanged) | source of the `main.zip` variant in `v4-v5-provenance-uncertain/source/`; valid submission packages of both: `rebuilt-main.zip` and `rebuilt-main5.zip` (the latter from the received `main5.py`, unchanged); `main5.zip` also recorded by its two constants |
| `main_v2.py`, `main_cap4/5/6/8.py` (temporary kit folder copies of the flag cap runs) | none | `bots/dist/starter/python/` (already gone before cleanup 1) | regenerate as in [`experiments/2-flag-cap-sweep(v3)/`](experiments/2-flag-cap-sweep%28v3%29/README.md); `cap6` is v3 |
| evolution and decision candidates (`g1-*.py`, `g2-*.py`, `independent.py`, `defense.py`, …) | none | `out/evolution/candidates/`, `out/decision-20260929/` | `experiments/4-code-evolution(cap7)/candidates/`, `experiments/6-decision-policies(cap7)/` |

## Cleanup 2 (state after cleanup 1 → now)

| before | now |
| --- | --- |
| `out/unsubmitted/` | `out/v0-unsubmitted/` |
| `out/v1-codex/` (ZIP, README), `out/v2-codex/` | `out/v1-v2-codex/` (the v1 ZIP was deleted after a bit exact rebuild from `source/` + `v1-zip-manifest.json` was verified) |
| `y-agent-v2.zip`, `y-agent-v3.zip`, `y-agent-indep1-20260929.zip`, `y-agent-cap7-low-review.zip`, `y-agent-indep-v0.zip` inside the model folders | `v2.zip`, `v3.zip`, `v6.zip`, `cap7.zip`, `indep-v0.zip` (contents and entry names unchanged) |
| `out/experiments/baseline-and-v1/` | `out/experiments/1-baseline-and-first-agent(v2)/` |
| `out/experiments/flag-cap-sweep/` | `out/experiments/2-flag-cap-sweep(v3)/` |
| `out/experiments/policy-search/` | `out/experiments/3-policy-weight-search(cap7)/` |
| `out/experiments/evolution/` | `out/experiments/4-code-evolution(cap7)/` |
| `out/experiments/weight-search/` | `out/experiments/5-weight-search-rounds(cap7)/` |
| `out/experiments/decision-policies/` | `out/experiments/6-decision-policies(cap7)/` |
| `out/experiments/independent-agent/` | `out/experiments/7-independent-agent(v6)/` |
| `docs/PLATFORM_OPERATIONS.md`, `docs/platform-sdk-provenance.json` | deleted; unique content moved into the root README ("Platform notes and kit provenance"); both stay in the Git history |
| none | new: `out/v4-v5-provenance-uncertain/` (kept source, two rebuilt packages, comparison rows) |
| `SHA256SUMS` in each model folder | deleted; `verify_artifacts.py` compares the ZIP entries with `source/` instead |
| dotted imports `out.experiments.evolution.evolve` in four scripts | `from evolve import …` (folder names now contain parentheses) |

## Directories (original state → cleanup 1)

| old | new (before the cleanup 2 renames) |
| --- | --- |
| `out/y-agent-*.zip`, `candidates/existing/*`, `candidates/indep*` | model folders above |
| `candidates/opponents/{pack,raider,rush,turtle}/` | `out/opponents/` (still exactly three levels below the repository root; the opponents locate the kit through `../../..`) |
| `candidates/tools/*` | `out/tools/evaluation/` and `out/tools/reporting/` (`analyze_official.py` → `reporting/official_macro_analysis.py`, `bake.py` → `evaluation/bake_params.py`) |
| `out/evaluate.py`, `out/policy_search.py` | `out/tools/evaluation/subprocess_eval.py`, `policy_search.py` |
| `out/heartbeat_search.py`, `out/heartbeat_search_20260929.py`, `out/heartbeat-20260929-1000/search.py` | one script: `out/tools/evaluation/weight_search.py --preset 20260928 / 20260929-0200 / 20260929-1000` |
| `out/local_metrics.py`, `out/analyze_official.py`, `out/heartbeat-20260928/analyze.py` | `out/tools/reporting/local_metrics.py`, `official_table.py`, `official_matches_json.py` |
| `out/heartbeat-*/` (data) | experiment 5; their `official_matches.json` → `out/official-replays/summary_20-35.json`, `summary_36-47.json` |
| `out/baseline-lv2-self-Y/`, `out/v1-vs-*` | experiment 1 (`seed-N.json` → `<run>/replays/`) |
| `out/cap*-vs-*`, `out/v2-vs-cap6-Y/` | experiment 2 (`seed-N.json` → `<run>/replays/`) |
| `out/policy-search/`, `out/policy-cap7-v3-subprocess-Y/` | experiment 3 |
| `out/evolution/`, `out/decision-20260929/` | experiments 4 and 6 |
| `out/indep/<run>` | experiment 7, `<phase>/<run>` (phase1-blind-build, phase2-analysis, phase3-selection, holdout, consolidation); `candidates/indep/*.md` → its top level |
| `out/official-replays/` | unchanged |

## Deleted or merged documents

| old | fate |
| --- | --- |
| `out/GOAL_PROMPT.md`, `IMPROVEMENT_GOAL_PROMPT.md`, `POLICY_GOAL_PROMPT.md`, `HEARTBEAT_20260928_PROMPT.md`, `HEARTBEAT_20260929_PROMPT.md`, `CONSOLIDATION_GOAL_PROMPT.md`, `CLAUDE_INDEPENDENT_GOAL.md`, `out/evolution/GOAL_PROMPT.md` | merged verbatim into [`PROMPT_RECORD.md`](PROMPT_RECORD.md) |
| `candidates/AI_USE_LOG.md`, `out/CONSOLIDATION_20260929.md` | facts and disclosure carried into `PROMPT_RECORD.md`, `v6-claude/README.md`, `experiments/7-independent-agent(v6)/README.md`, `DEVELOPMENT_LOG.md` |
| `candidates/README.md`, `candidates/.gitattributes` | carried into the experiment 7 README, `tools/README.md`, the root `.gitattributes` |
| `out/heartbeat-*/REPORT.md`, `out/heartbeat-20260929/PLAN.md` | match findings merged into [`OFFICIAL_MATCH_ANALYSIS.md`](OFFICIAL_MATCH_ANALYSIS.md), search parts into the experiment 5 README |
| `out/policy-search/local-submission-check.json`, `out/evolution/selected-zip-check.json` | byte identical to each other; one copy kept as `v0-unsubmitted/cap7-codex/local-zip-check.json` |
| empty `*.log` stderr files of the Claude runs | deleted (empty); the non empty `p1-v0-stderr.log` (KeyError tracebacks) and `serial-final-stderr.log` are kept |
| `__pycache__` folders, tracked `*.pyc` in the kit directories | generated files; removed from the working tree and from the Git index |
| `docs/PLATFORM_OPERATIONS.md`, `docs/platform-sdk-provenance.json` | see cleanup 2 |
| result screenshots `v3-practice-result.png`, `v6-medium-practice-result.png` | never present in the workspace at the start; the facts are in `DEVELOPMENT_LOG.md` and the model READMEs |

## Reconciliation

Cleanup 1: the 1311 files of `out/` and `candidates/` before the first move.

| disposition | files |
| --- | ---: |
| moved (git ignored bulk replay) | 1000 |
| moved | 180 |
| unchanged | 47 |
| moved and edited | 40 |
| deleted (merged) | 18 |
| deleted (empty) | 15 |
| created (authored or generated in a cleanup) | 14 |
| deleted (duplicate) | 8 |
| rewritten in place | 2 |
| deleted | 1 |

Cleanup 2: the 1381 files of `out/`, `docs/` and the kit's Python helpers before the second round (they include the documents cleanup 1 created).

| disposition | files |
| --- | ---: |
| moved (git ignored bulk replay) | 1000 |
| moved | 231 |
| unchanged | 89 |
| moved and edited | 28 |
| rewritten in place | 23 |
| deleted | 7 |
| deleted (merged) | 2 |
| deleted (duplicate) | 1 |

`moved and edited` = moved and then changed (mechanical path rewrite in reports, or path and import fixes in scripts); `rewritten in place` = an existing file whose content was replaced by a merged version.
