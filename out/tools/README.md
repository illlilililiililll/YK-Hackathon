# Shared tools

Run from the repository root. Python 3.12 (the server's version) is enough for everything except the subprocess matches, which need Linux pipes (WSL) because of the official runner.

## `evaluation/` — play games and check artifacts

| tool | use |
| --- | --- |
| `eval_matches.py`, `wsl_run.sh`, `wait_rows.sh` | batch matches through the official runner (candidates × opponents × seeds × sides, resumable, JSONL results, replays of losses). `wsl_run.sh` mirrors the repository to WSL's ext4 (`~/ykrun`, or `$YKRUN` so parallel jobs do not clobber each other) first; results are written to `$OUTDIR` (default `out/experiments/local-runs`). Every row carries `mid`: the midgame metrics below per team |
| `midgame_metrics.py` | midgame building control of one replay, local or official format (T11–140): own flips, flips with no own warrior on the building, lost score-turns, score-turn and HALL/ENG-turn totals, decisive turn |
| `subprocess_eval.py` | one candidate vs one opponent over N seeds through the official `SubprocessBot`; writes `summary.json` + `replays/seed-N.json` |
| `inproc.py` | one in process match on Windows or Linux; shows exceptions and per turn `decide()` time (`--y v6`, `--y indep`, `--k lv2`, `--k file:<main.py>`). Fixed 09-30: before, the second agent reused the first agent's cached `brain` module, so two indep-family agents played the same policy (no reported result depended on it) |
| `replay_commands.py` | attribute an official replay to a source: feeds the recorded observations turn by turn to `decide()` and compares with the recorded Y commands (the true source reproduces every turn) |
| `policy_search.py` | library (`render_policy`, `policy`, `match`, `summarize`, `TimedBot`) and CLI for the 6-weight search on the v3 policy; imported by the searches below |
| `weight_search.py` | the three recorded weight search rounds as presets (`--list`, `--preset`, `--out-dir`) |
| `bake_params.py` | bake `INDEP_PARAMS`-style overrides into a copy of the independent agent's source (how v6's source was made from `indep-v0`) |
| `zip_modes.py` | print ZIP entry modes; exit 1 on any execute bit (the server rejects them: `EXECUTABLE_FILE`) |
| `verify_artifacts.py` | check the retained submission artifacts: ZIP entries == `source/`, execute bit expectations, and the rejected v1 ZIP rebuilt bit for bit from its manifest |

## `reporting/` — build tables and figures

| tool | reproduces |
| --- | --- |
| `official_table.py` | the 47-match table (10/20/end buildings and warriors) |
| `official_matches_json.py` | `official-replays/summary_*.json` (per match snapshots, commands, events, response times, full `gameId`) |
| `official_macro_analysis.py` | `7-independent-agent(v6)/phase2-analysis/official_analysis.{json,txt}`: version attribution, opponent types, macro benchmark, building loss causes |
| `loss_geometry.py` | `7-independent-agent(v6)/phase2-analysis/loss_geometry.txt` |
| `local_metrics.py` | the `metrics.txt` files of experiments 1, 2 and 3 (needs the local `replays/`) |
| `final_table.py`, `compare.py`, `h2h.py`, `rr_matrix.py`, `macro.py` | tables from `results.jsonl`: candidate × opponent, paired statistics, head to head, round robin matrix, macro at fixed turns |
| `trace.py`, `count_spawns.py` | turn by turn view of a replay (`.json` or `.json.gz`); spawn counts |
| `check_links.py` | verify Markdown links, `out/...` paths and the script names in documented commands |

The three official replay analysers (`official_table`, `official_matches_json`, `official_macro_analysis`/`loss_geometry`) answer different questions and were kept separate; in the cleanup each was re-run: the JSON/text outputs reproduced their stored files byte for byte, and `official_table.py` reproduced the numbers of all 47 rows of the three former hand copied tables.
