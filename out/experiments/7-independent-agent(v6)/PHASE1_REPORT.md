# Phase 1 checkpoint — blind independent Y agent (`indep-v0`)

Date: 2026-09-29. Model: Claude Sonnet 5.5 (`claude-sonnet-5-5`) via Claude Code, background job.
Strategy assumptions and pass/fail criteria were committed in `STRATEGY.md` **before** any agent code.

## Blindness statement

Read before/while building: `README.md`, `docs/*`, starter kit (all of `bots/dist/starter/**` **except**
`python/main.py`), `engine/`, `runner/`, `mapgen/`, `config/`, `out/PROMPT_RECORD.md`, official
`/api/rules` artifacts (rules PDF, SDK, Python starter; byte compared with the local copies).
**Not opened before this checkpoint:** `bots/dist/starter/python/main.py` (current agent), `out/y-agent-*.zip`,
`out/DEVELOPMENT_LOG.md`, `out/OFFICIAL_MATCH_ANALYSIS.md`, every other `out/*` report/replay/prompt file,
the official SDK/starter zips' own `main.py`. Only file *names* were visible from `git status`.
The only test feedback used to shape the code was the agent's own results against lv1/lv2 and the
three fixed opponents below (which were written from the rules alone).

## Source identity

The frozen Phase 1 sources and ZIP are kept in [`out/v0-unsubmitted/indep-v0-claude/`](../../v0-unsubmitted/indep-v0-claude/); the official helpers are byte identical to the starter, and the three fixed opponents (`rush`, `turtle`, `raider`) are in [`out/opponents/`](../../opponents/).

## What the agent does (canonical frame; K is rotated 180 degrees so both sides run identical code)

- Spawn: all stock each turn (income arrives before capture, so almost no capture reserve). F only while there
  are open targets (cap 4 early / 3 later, and only if W >= F after turn 12); everything else W (2 with an ENG).
- F: stay on a building being captured (escorted), else global greedy by `value/(eta+1.5)`; a target/step is
  taken only if my W within one step >= enemy W that can reach the step (equal W leave F alive).
  Building value = score (2x for enemy owned) + function bonus (HALL 3.5, ENG 3.0, DEPOT 1.5, HOSPITAL 1.0 ...).
- W: escort F, intercept enemy F (predicted next cell / destination), otherwise convoy with F or head to the
  best safe target. `PRIORITY` = descending value. `decide` never raises: exception -> `SPAWN W 99` fallback.

## Results (official runner, `out/tools/evaluation/eval_matches.py`, native ext4 WSL, Python 3.14.4)

| run (dir under `out/experiments/7-independent-agent(v6)/`) | games | result |
|---|---|---|
| `p1-v0c-sweep` Y, seeds 0-29 vs lv1 / lv2 / rush / turtle / raider | 150 | 150-0-0 (each opponent 30-0-0), 0 forfeits, 0 tracebacks |
| `p1-v0c-K` K, seeds 0-29, same opponents | 150 | 150-0-0, 0 forfeits (K margin == Y margin for symmetric opponents) |
| `p1-v0c-mirror` indep vs indep, seeds 0-29 | 30 | 30 draws, stats identical => symmetric + deterministic |
| `p1-v0c-serial` `--jobs 1`, seeds 0-9 vs lv2/rush/turtle/raider, all replays saved | 40 | 40-0-0, max turn time 9-16 ms end to end |
| `y-agent-indep-v0.zip` via `run_tests.py --zip` seeds 3, 16, 21 | 3 | `ok: true`, no issues, stderr 0 B, max line 21-23 B. **Correction (added in Phase 3):** this ZIP was built under WSL and every entry has unix mode `0o100777`; the earlier development log records that exactly this made the server reject v1 (`EXECUTABLE_FILE`), and `run_tests.py`/`inspect_zip` cannot detect it. Any ZIP meant for upload must be built with Windows Python (modes `0o100666`) and checked with `out/tools/evaluation/zip_modes.py`. `indep-v0` is a baseline, not an upload candidate. |
| in process, Windows Python 3.12.7 (full 160-turn mirror games) | 3 | decide mean ~2 ms, p95 < 4 ms, max 30 ms (INIT precompute) |

Average margin (Y): lv1 +34.2, lv2 +33.5, rush +33.1, turtle +32.9, raider +27.7; nearly all wins are instant wins
(opponent score 0 with > half of the map score) around turns 25-45.

## Defects found by this checkpoint (kept for the development report)

1. **`KeyError` in `Brain.rally`** (a non-building cell was compared with `bval`): on seeds 16, 21, 22, 28 the
   exception net returned `[]` every turn, so the agent sat with 2 F and no W and lost 14/150 games (`p1-v0-sweep`).
   Fixed; the fallback now buys W instead of returning nothing; `eval_matches.py --errlog` counts tracebacks so a
   swallowed exception can no longer hide (0 in every run above).
2. **Spurious forfeits under 6-way parallel WSL on `/mnt/c`** (`p1-v0-a`: 3 forfeits; both bots timed out on the
   same turn in the mirror). First turn latency there was p50 0.8 s / max 2.3 s even for the trivial official bots.
   Serial reruns had 0 forfeits (`p1-v0-recheck`). Evaluations now run from `~/ykrun` (ext4) via `wsl_run.sh`.
   Timing gates use serial runs only.

## Reproduce

```sh
# from repo root, PowerShell/Windows host (matches run under WSL because the runner's pipes break on Windows)
wsl --cd <repo> bash out/tools/evaluation/wsl_run.sh --tag t --errlog out/experiments/local-runs/t-stderr.log \
  --cand indep="python3 out/v0-unsubmitted/indep-v0-claude/source/main.py 2>>out/experiments/local-runs/t-stderr.log" \
  --opp lv2="python3 bots/dist/starter/python/example_lv2.py" \
  --opp rush="python3 out/opponents/rush/main.py" --seeds 0-29 --sides Y --jobs 4
python out/tools/evaluation/inproc.py --y indep --k lv2 --seed 3         # in-process, shows exceptions + decide ms
wsl --cd <repo> python3 bots/dist/starter/make_submission.py --source out/v0-unsubmitted/indep-v0-claude/source --output out/v0-unsubmitted/indep-v0-claude/indep-v0.zip
wsl --cd <repo> python3 bots/dist/starter/run_tests.py --zip out/v0-unsubmitted/indep-v0-claude/indep-v0.zip --seed 3
```

## Caveats

- lv1/lv2 and the three fixed opponents are weak: lv2 caps itself at 3 W and floods ~20 F which a W heavy agent
  kills for free (T20: my W ~92 vs 2). A 100% score here shows correctness and safety, **not** strength against real
  teams or the hidden "medium" bot. Phase 3 needs stronger discriminators (variants of the agent itself, replay derived
  opponent models).
- Local results do not prove win rates against real teams.
