# Weight search rounds around cap7 — 2026-09-28 to 09-29 (Codex)

**Models.** Primary: **cap7** (incumbent). Also: v3 (the source of the rendered policies), v2, `g1-safe-goal` (from experiment 4), the stand in policies and the official Lv2 as opponents.

Three bounded, resumable searches over a few decision weights of the v3 policy (flag cap, capture reserve with/without the central plaza, target score weight, function bonus, danger penalty), each triggered by a newly published match round.
Model: Codex (GPT-6 family), driven by the heartbeat automations (prompt P5 in [`../../PROMPT_RECORD.md`](../../PROMPT_RECORD.md)). One script runs all three: [`../../tools/evaluation/weight_search.py`](../../tools/evaluation/weight_search.py) with `--preset <round>`
(it replaced `heartbeat_search.py`, `heartbeat_search_20260929.py` and `heartbeat-20260929-1000/search.py`, which shared the same train → select → hold-out → adopt workflow and differed only in the parameters recorded in the presets).
The match findings of these rounds were moved to [`../../OFFICIAL_MATCH_ANALYSIS.md`](../../OFFICIAL_MATCH_ANALYSIS.md); the heartbeat report files were removed.

**Common setup.** Official engine, in process bots (`out/tools/evaluation/policy_search.py`), policies rendered from the v3 source (`out/v3-codex/v3.zip`), incumbent **cap7** (cap 7, reserve 1/0; asserted byte equal to `../evolution/candidates/cap7.py`).
Stand in opponents (not real teams): `v2` (cap 12), `v3`, `cap7` (rounds 2–3), `g1-safe-goal` (`../evolution/candidates/g1-safe_goal.py`), `fast-attack` (cap 3, reserve 0/0), `slow-defense` (cap 8, reserve 6/4, danger 8), official Lv2, and a held back `unseen-mixed` attacker (cap 5, reserve 0/0, score 1.8, bonus 0, danger 0).
Win = 1, draw = ½, loss = 0. A candidate reaches the hold-out only with ≥ +2 points over cap7 on the search seeds; it is adopted only with ≥ +3 points, a better mean score diff and 0 forfeits (rounds 2–3 also: no single opponent more than 2 points worse).
Budgets fixed in advance: round 1 none recorded; round 2 at most 254 games and 360 s of match time (cumulative over restarts); round 3 at most 240 games and 360 s per invocation.
Rows are in `<round>/games.jsonl`, the verdict in `<round>/result.json`. **No candidate was adopted in any round; cap7 stayed.** 0 forfeits in all 619 games.

| round folder (preset) | trigger | candidates (settings) | search seeds · Y · opponents | hold-out |
| --- | --- | --- | --- | --- |
| `20260928` | 9/28 22:00 round, 16 new games (v3 4W–12L) | cap5-zero, cap6-zero, cap5-low, cap6-low (cap N, reserve 0/0 or 1/0) | 700–703 · 6 (no cap7) = 24 games each | Y 800–807 (48), K 800–801 (12), unseen attacker Y/K |
| `20260929-0200` | 9/29 02:13, no new matches | danger 0, danger 8, bonus 0, score 2, cap 9 + reserve 2/1 | 900–902 · 7 = 21 each | not opened |
| `20260929-1000` | 9/29 10:00 round, 12 new games (v3 4W–8L; opponent pool widened) | cap5-low, danger 6, bonus 3, score 0.5 | 1100–1102 · 7 = 21 each | Y 1200–1205 × 8 opponents (48), K 1200–1201 (16) |

## Results

| round | search seed wins (cap7 → best) | hold-out (cap7 vs candidate) | verdict and failure evidence |
| --- | --- | --- | --- |
| `20260928` | cap7 14/24; cap5-zero 12, cap6-zero 14, cap5-low 17, **cap6-low 17** (tie, higher score diff) | Y 31/48 vs **32/48**; K 10/12 vs 9/12; unseen attacker Y 8/8 vs 6/8, K 2 vs 2 | +1 win < +3 → **rejected**. Fast attacker 7/8 → 5/8; seed 804: cap7 28:0 win → candidate 0:28 loss; seed 801 vs v2 went the other way (6:21 loss → 27:6 win), so the change is two directional noise. 260 games, max in process turn 31.6 ms |
| `20260929-0200` | cap7 **16/21** (+10.0 mean diff); danger0 10, danger8 15, bonus0 11, score2 13, cap9 9 | none (no candidate ≥ +2) | **rejected**. danger8: better vs the earlier strong policy (0 → 2 wins) but worse vs fast attacker 3 → 2 and slow defence 2 → 1; danger0: fast attacker 3 → 0 (seed 900: cap7 won 11:11 on tiebreak, danger0 lost 3:32); score2 cut turn 20 buildings 8.00 → 6.76. 126 games, 137.6 s, max in process turn 14.0 ms, max output 535 B / 33 lines |
| `20260929-1000` | cap7 12/21; cap5-low 12, danger6 12, bonus3 12, **score 0.5: 15** | Y **26/48** vs 23/48 (mean diff +3.35 vs +3.19); K 9/16 vs 9/16; mixed attacker 5/6 vs 3/6; vs v3 1/6 vs 4/6 | +3 wins *fewer* → **rejected**. Seed 1202: cap7 17:13 win → candidate 8:25 loss. Final buildings 8.88 vs 8.92, unit value 389 vs 426. 233 games, max in process turn 49.9 ms |

These are in process timings, not server guarantees, and every opponent is a stand-in. The recurring pattern (small gains on the search seeds shrinking or reversing on unused seeds, with strong opponent specific sign flips) is the reason the pre-set adoption gate was kept.

## Regenerate / verify

```sh
python out/tools/evaluation/weight_search.py --list
python out/tools/evaluation/weight_search.py --preset 20260929-1000                        # Windows or WSL, Python >= 3.12; skips the 233 stored games
python out/tools/evaluation/weight_search.py --preset 20260928 --out-dir <fresh dir>       # a fresh dir replays every game (round 2's 126 games took 137.6 s of match time)
```

Run in place, a finished round plays nothing and rewrites `result.json`. In the cleanup each preset was run against a copy of its stored `games.jsonl`: all three produced a `result.json` identical to the stored one (modulo line endings) with 0 new games.
The stored `games.jsonl` are the evidence; the search is deterministic apart from the timing fields (`max_ms`, `match_seconds`).
