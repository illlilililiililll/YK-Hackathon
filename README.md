# 2026 연고전 AI 해커톤 — Yonsei (Y) agent workspace

The official game kit of the 2026 Yonsei–Korea University AI hackathon ("깃발 대항전") plus the agents, evidence and experiments of one Yonsei team.
Source of the rules: [official rules and downloads](https://yonsei-vs-korea-hackathon.kr/rules), checked 2026-09-27 and 2026-09-29 (KST). The kit's [full rulebook](docs/rulebook.md) and [starter instructions](bots/dist/starter/README.md) take precedence over this note; recheck the site before submitting.

## Repository layout

| path | what it is |
| --- | --- |
| [`bots/`](bots/) | **Official kit**: starter bots (Python and C++ `main`, protocol helpers, BFS and capture reserve `search`, level 1 and 2 example bots), the local match runner `play_local.py`, the ZIP builder `make_submission.py` and the submission checker `run_tests.py`. Left as delivered, except that the working tree copy of `bots/dist/starter/python/main.py` is the **v3 agent** (byte identical to `out/v3-codex/source/main.py`) and one link in `bots/dist/starter/README.md` now points to the platform notes below |
| [`engine/`](engine/) | **Official kit**: the game rules as code: state, commands, the per turn pipeline (spawn → move → combat → effects → income → capture → reveal → win check) and the balance loader |
| [`runner/`](runner/) | **Official kit**: plays a match between two bots (subprocess bots that speak the stdin/stdout protocol, or in process bots), validates output, writes replays |
| [`mapgen/`](mapgen/) | **Official kit**: deterministic, point symmetric 15×15 map generator (seed → map) |
| [`config/`](config/) | **Official kit**: `balance.json`, the fixed game numbers (grid, 160 turns, unit costs, income, capture costs, building effects). Never changed by our work |
| [`docs/`](docs/) | The official rulebook (`rulebook.md`). The platform operations note and the kit provenance record that used to be here are carried into [Platform notes and kit provenance](#platform-notes-and-kit-provenance) below |
| [`out/`](out/) | **Our work**: one folder per submitted version (`v1-v2-codex`, `v3-codex`, `v6-claude`), a folder for two sources of uncertain provenance (`v4-v5-provenance-uncertain`), local only candidates (`v0-unsubmitted`), official replays, shared tools, numbered experiments, the development log, the official match analysis and the prompt and AI use record. Start at [`out/README.md`](out/README.md) |

`LICENSE` applies to the repository. Python bytecode caches, local bulk match output and scratch files are git ignored (`.gitignore`).

## Current state (2026-09-29 KST)

**Upload and selection status.** **v6** was uploaded (submission ID `01a0ebe3-3f4b-74c5-9a44-d57b14b70ab2`, 15:38 KST, file `y-agent-indep1-20260929.zip`, status `사용 가능`) and practice tested (15:41 KST, medium bot, 10 wins, 0 draws, 0 losses). **v5 remained the website's competition selection** at the last recorded check (2026-09-29 15:41 KST); v5's source is not in this repository, so it is not assumed to equal v6 or any local candidate.
Nothing in this repository uploads, selects or changes anything on the website; whether to select v6 is a separate decision.

**Three kinds of results, never to be mixed.**

| kind | what it is | results so far |
| --- | --- | --- |
| Official team matches | public replays of games against other teams, Y side ([analysis](out/OFFICIAL_MATCH_ANALYSIS.md)) | only v2 and v3 have any: **v2 4 wins, 15 losses; v3 8 wins, 20 losses** (47 games). None for v4, v5, v6 or the local candidates |
| Official medium bot practice | ten games against the site's medium bot (six wins complete the practice); the bot is weak and this test is saturated | v2, v3, v5 (as observed on the site) and v6: 10 wins, 0 draws, 0 losses each. It says nothing about strength against teams |
| Local proxy matches | our own runs on the official engine against opponents we built (earlier agents, parameter variants, fixed bots) | e.g. v6 beats v2, v3 and cap7 100–0 on unused seeds and two warrior heavy stand ins 30 of 40; cap7 won 74 of 120 unused games where v3 won 68 (same seeds and opponents). They are proxies, **not** real team win rates |

**The retained models: what they do and how they arose.**

- **v1 and v2** (Codex, [`out/v1-v2-codex/`](out/v1-v2-codex/)): a greedy flag rush built from the official Lv2 example. Up to 12 flag bearers (F) are produced first and each is assigned to a different building (near and valuable first); everything left goes into warriors (W) that chase the nearest enemy flag or gather at central buildings. No escort, no guard. It arose from the observation that Lv2 sends many flags to the same building; locally it beats Lv2 10–0 on both sides. v1 and v2 are the same code: the server rejected v1 only because its ZIP entries had execute bits.
- **v3** (Codex, [`out/v3-codex/`](out/v3-codex/)): v2 with the flag cap lowered from 12 to 6. The 19 public v2 games were mostly lost with fewer warriors than the opponent at turns 10–20 although v2 had more flags.
- **cap7** (Codex, never uploaded, [`out/v0-unsubmitted/cap7-codex/`](out/v0-unsubmitted/cap7-codex/)): v3 with **cap** 7 (the flag cap) and smaller capture reserves (1, or 0 once the central plaza is owned, instead of 4 and 2). It came out of a bounded local search over six decision values against local stand in opponents. Later code evolution, weight search rounds and decision policy experiments could not beat it, but it never played an official game.
- **indep-v0** (Claude Sonnet 5.5, never uploaded, [`out/v0-unsubmitted/indep-v0-claude/`](out/v0-unsubmitted/indep-v0-claude/)): "indep" means independent, "v0" the first version. It was designed from the rules alone before reading any earlier agent or match: warriors first with a small flag force (cap 4, later 3), flags move only where enough warriors can escort them, warriors escort their flags and intercept enemy flags, and both sides run the same code in a mirrored frame.
- **indep1, the submitted v6** (Claude Sonnet 5.5, [`out/v6-claude/`](out/v6-claude/)): indep-v0 plus four changes that passed pre registered tests: one warrior stays on every owned building (garrison), warriors chase enemy flags from up to six steps away, the flag cap goes to 10 and 8 (expand buildings first), and reinforcements spawn at the hospital nearest to their goal. It was built to stop the way official losses happened (escorted enemy flags flipping buildings) but has no official team game yet.
- **v4 and v5** (developer unknown, source absent): on the website, v4 is `y-agent-v4.zip` (11.6 KiB, rejected: "check the file composition", 13:22) and v5 is `v-agent-v4.zip` (11.2 KiB, usable, uploaded 13:25, the competition selection). Two received sources ([`out/v4-v5-provenance-uncertain/`](out/v4-v5-provenance-uncertain/)), which differ only in two constants (`GUARD` 1 or 2, `ENDGAME` 0 or 15), belong to a design unlike all the other models here (safe target flags, one main army, per building guards). Both were turned into valid submission packages (`rebuilt-main.zip` and `rebuilt-main5.zip`, never uploaded); the variant `GUARD = 1`, `ENDGAME = 0` is the better one locally (151 wins in 200 head to head games). **Nothing proves that either is v4 or v5.**

History and evidence: [`out/DEVELOPMENT_LOG.md`](out/DEVELOPMENT_LOG.md) (chronology), [`out/experiments/`](out/experiments/) (how each idea was tested, including rejected ones), [`out/PROMPT_RECORD.md`](out/PROMPT_RECORD.md) (LLMs, prompts, scope of AI use).

## Game and bot contract

- Two simultaneous players (Y/K), 15×15 symmetric map, 17 capturable buildings, 160 turns. Win by owned building score; ties use cumulative score turns, then surviving unit cost.
- `F` (cost 5) captures, `W` (3) fights, `S` (2) moves two cells and reveals scores. Only building scores can be hidden (`-1`); symmetric buildings have equal scores.
- Turn order: spawn → move/teleport → combat → building effects → income → capture → reveal → win check. A new unit can move immediately. Save resources for capture after spawning. Combat can kill a flag before capture.
- Start with 10 resources, gain 10 per turn plus 2 per owned hall, cap 40. Neutral capture costs 2; taking an enemy building needs neutralization then a later capture. The central plaza costs 4 per step. An owned library reduces each capture step by 1.
- The bot stays running for the match. Read one `INIT` block and repeated `TURN` blocks from stdin, each ending in `END`; output commands plus `END` and flush **every turn**. Send diagnostics only to stderr. Invalid command lines are ignored, but a missing `END`, a timeout or a process exit forfeits.
- First response: 3 s including startup; later turns: 300 ms. Server: Python 3.12.14 / NumPy 2.3.3 or C++20 / GCC 12.2.0, CPU only, 384 MiB. stdout ≤ 64 KiB and 4,096 lines per turn, ≤ 1 KiB per line; stderr ≤ 1 MiB per game.
- Submit a source ZIP with `submission.json` and `main.py` or `main.cpp` **at the ZIP root**. Several Python modules or C++ sources and headers, the standard library and the supplied NumPy are allowed; no executables, build scripts, arbitrary data or weight files, or extra package installs. **ZIP entries must not have execute bits** (a ZIP built under WSL is rejected as `EXECUTABLE_FILE`; build with Windows Python).

## Running things

From the repository root. The official runner's subprocess transport needs Linux pipes: on Windows it fails with `WinError 10093`, so use WSL (Ubuntu) for subprocess matches and the official ZIP checker; in process matches work on Windows.

```sh
python bots/dist/starter/play_local.py                                            # kit demo match (Linux/WSL)
python bots/dist/starter/make_submission.py --source bots/dist/starter/python --output out/submission-python.zip   # scratch ZIP (git ignored)
python bots/dist/starter/run_tests.py --zip out/submission-python.zip             # official ZIP checker (Linux/WSL)

python out/tools/evaluation/inproc.py --y v6 --k lv2 --seed 3                     # in process match, any OS
python out/tools/evaluation/verify_artifacts.py                                   # ZIP entries == source, file modes, v1 rebuilt from its manifest
wsl --cd <repo> python3 bots/dist/starter/run_tests.py --zip out/v6-claude/v6.zip --seed 52   # official checker on v6
```

Batch evaluation, weight searches and report utilities: [`out/tools/README.md`](out/tools/README.md); how each recorded experiment is regenerated: [`out/experiments/README.md`](out/experiments/README.md).
The kit's own C++ and Python instructions: [`bots/dist/starter/README.md`](bots/dist/starter/README.md).

## Competition workflow (from the official site, 2026-09-27 to 09-29)

- Site submissions open September 27 at 15:00 KST. Upload **and explicitly select** a version for each leaderboard cutoff; uploading alone does not select it. September 28–30 cutoffs: 08:00 and 20:00 KST; leaderboard updates: 10:00 and 22:00.
- October 1: last leaderboard cutoff 15:00, last upload 23:00, final code selection and report 23:59 KST. Final results October 2 at 08:00.
- From the September 29 10:00 round the opponent pool is all participating teams, regardless of school; the side information given to the agent is unchanged. The September 29 announcements also state that rules and balance numbers are not changed, that constants written inside the source are allowed, and that separate data or weight files are not.
- The practice battle is ten games against an easy, medium or hard bot on the public seeds 0–9, keeping the team's own side. Six **wins** against medium in one ten game run meets the completion criterion; draws do not count. Practice and interim leaderboard results do not directly set the final rank.
- The report is required by October 1 at 23:59. Development process carries 30/100 points: keep dated changes, hypotheses, tests and measured results. LLM use is allowed, but the report must state model, prompts and purpose and scope ([`out/PROMPT_RECORD.md`](out/PROMPT_RECORD.md)). Do not exchange code or strategy documents with other teams.

## Platform notes and kit provenance

Carried over from `docs/PLATFORM_OPERATIONS.md` and `docs/platform-sdk-provenance.json`, which were removed as duplicates of this README once their unique content was transferred (both remain in the Git history).

**Operations.**
- Only the code selected by the deadline is used for that round. Code that is still being checked can be selected; if it fails the check no other code replaces it. Build checks may continue after the deadline.
- If both sides err in a game it is a draw (0.5 points each); tie breaks of normal games follow the game engine. On the server, exceeding the whole match infrastructure time limit does not count as the participant's loss: the match is retried under the same conditions and the operators are notified. Exceeding an output limit forfeits on the server, while the local checker only warns.
- Submission and practice jobs are requested one at a time: request again after the running job has finished. Inquiries go through the channel talk of the competition website.
- The local tools are for strategy development. They do not reproduce the server's isolation, memory and CPU limits, so performance can differ on the server.

**Kit provenance.** Game and example sources come from the platform's public rules revision `platform-public-rules-v4` and SDK revision `participant-sdk-docs-v2`; `docs/rulebook.md` is the public website rulebook.
Platform changes to the distribution: the public rulebook and the operations note were replaced; `_support.py` reads the run limits from `limits.json`; the game engine, map generator, strategy sources and the match logic of the runner are the originals. The obsolete operations command `runner/smoke.py` (needs internal reference bots that are not distributed) was removed; `runner/__init__.py` and `runner/cli.py` lost only its imports and command line mode, and one docstring in `runner/match.py` changed (executable AST unchanged).

<details><summary>Modified kit files</summary>

| file | change |
| --- | --- |
| `bots/dist/starter/README.md` | updated by the platform; one link (to the removed operations note) was edited again in this repository |
| `bots/dist/starter/RULES_SUMMARY.md` | updated by the platform |
| `bots/dist/starter/_support.py` | reads the run limits from `limits.json` |
| `bots/dist/starter/limits.json` | run limits, updated by the platform |
| `docs/rulebook.md` | replaced by the public website rulebook |
| `runner/__init__.py` | obsolete smoke imports and exports removed |
| `runner/cli.py` | obsolete smoke only command line mode removed; local matches unchanged |
| `runner/match.py` | one docstring changed (obsolete bot file name); executable code unchanged |
| `runner/smoke.py` | removed (obsolete operations command) |
| `docs/PLATFORM_OPERATIONS.md` | added by the platform, since removed |

</details>
