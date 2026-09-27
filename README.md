# 2026 연고전 AI 해커톤 — agent development notes

Source: [official rules and downloads](https://yonsei-vs-korea-hackathon.kr/rules), checked 2026-09-27 (KST). The official development kit is included in this repository; [full game rules](docs/rulebook.md) and [starter instructions](bots/dist/starter/README.md) take precedence over this note. Recheck the site before submission.

## Game and bot contract

- Two simultaneous players (Y/K), 15×15 symmetric map, 17 capturable buildings, 160 turns. Win by owned building score; ties use cumulative score-turns, then surviving unit cost.
- `F` (cost 5) captures, `W` (3) fights, `S` (2) moves two cells and reveals scores. Only building scores can be hidden (`-1`); symmetric buildings have equal scores.
- Turn order: spawn → move/teleport → combat → building effects → income → capture → reveal → win check. A new unit can move immediately. Save resources for capture after spawning. Combat can kill a flag before capture.
- Start with 10 resources, gain 10 per turn plus 2 per owned hall, cap 40. Neutral capture costs 2; taking an enemy building needs neutralization then a later capture. The central plaza costs 4 per step. An owned library reduces each capture step by 1.
- Bot stays running for the match. Read one `INIT` block and repeated `TURN` blocks from stdin, each ending in `END`; output commands plus `END` and flush **every turn**. Send diagnostics only to stderr. Invalid command lines are ignored, but missing `END`, timeout, or process exit forfeits.
- First response: 3 s including startup; later turns: 300 ms. Server: Python 3.12.14 / NumPy 2.3.3 or C++20 / GCC 12.2.0, CPU only, 384 MiB. stdout ≤64 KiB and 4,096 lines per turn, ≤1 KiB per line; stderr ≤1 MiB per game.
- Submit a source ZIP with `submission.json` and `main.py` or `main.cpp` **at ZIP root**. Standard library and supplied NumPy only. No executables, build scripts, arbitrary data/weights, or extra package installs.

## Official starter code

- [Python entry point](bots/dist/starter/python/main.py): `decide(view, init)` returns command strings. [Protocol](bots/dist/starter/python/protocol.py) handles I/O, including `END` and flush; [search](bots/dist/starter/python/search.py) has BFS and capture reserve.
- [Python level 1](bots/dist/starter/python/example_lv1.py): nearest neutral building via BFS. [Level 2](bots/dist/starter/python/example_lv2.py): resource reservation, a small warrior force, enemy-flag interception, and capture targeting. Both are baselines, not proven competitive strategies.
- [C++ entry point](bots/dist/starter/cpp/main.cpp) and `protocol.hpp` provide the same persistent loop. C++ level-1/2 examples are alongside it.
- [Local runner](bots/dist/starter/play_local.py), [ZIP builder](bots/dist/starter/make_submission.py), and [submission checks](bots/dist/starter/run_tests.py) came from the official kit. From repository root:

```sh
python bots/dist/starter/play_local.py
python bots/dist/starter/make_submission.py --source bots/dist/starter/python --output out/submission-python.zip
python bots/dist/starter/run_tests.py --zip out/submission-python.zip
```

On this Windows host, `run_tests.py --self-test` currently fails in the supplied runner with `WinError 10093` (`selectors.select` on the subprocess pipe). Use Linux/WSL for local matches and ZIP validation until that runner transport is adapted; this failure does not test the agent itself.

## Competition workflow

- Site submissions open September 27 at 15:00 KST. Upload **and explicitly select** a version for each leaderboard cutoff; uploading alone does not select it. September 28–30 cutoffs: 08:00 and 20:00 KST; leaderboard updates: 10:00 and 22:00.
- October 1: last leaderboard cutoff 15:00, last upload 23:00, final code selection and report 23:59 KST. Final results October 2 at 08:00. A selected code that fails validation is not automatically replaced by an older version.
- Practice battle is ten maps against easy/medium/hard bots. Six **wins** against medium in one ten-game run meets the completion criterion; draws do not count. Practice and interim leaderboard results do not directly set final rank.
- Report is required by October 1 at 23:59. Development process carries 30/100 points: keep dated changes, hypotheses, tests, and measured results. LLM use is allowed, but report its model, prompts, and purpose/scope. Do not exchange code or strategy documents with other teams.

## Next development checks

1. Run the kit self-test and a baseline local match. Confirm the local Python/compiler setup matches server behavior closely enough for timing tests.
2. Build one robust baseline from `example_lv2.py`; measure win rate on multiple seeds and both sides. Track forfeits, per-turn time, capture score, and resource waste before tuning strategy.
3. Package, validate, upload, and select the intended version well before a cutoff. Record the selected version and practice results for the report.
