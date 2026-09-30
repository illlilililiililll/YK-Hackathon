# Phase 3 report — improve, compare, select, validate (2026-09-29)

Protocol fixed in `PHASE3_PLAN.md` before the runs. Every number is regenerated from `out/experiments/7-independent-agent(v6)/*/results.jsonl` (derived tables
sit next to them: `matrix.txt`, `h2h.txt`, `compare.txt`, `table.md`). **Local results do not prove higher win rates against real
teams.** Nothing was uploaded, no official practice battle was run, the competition's selected code was not touched.

## 0. Stage log (seeds, what was decided after seeing what)

| stage | seeds | opponents | purpose | seeds afterwards |
|---|---|---|---|---|
| Phase 1 sweep | 0-29 (+K) | lv1 lv2 rush turtle raider, mirror | correctness / safety of `indep-v0` | design |
| Phase 2 big sweep | 30-129 | v3 cap7 lv2 rush turtle raider | find `indep-v0`'s weaknesses (8/200 losses, all vs v3/cap7) | design |
| **design** | 30-129 | v3, cap7 | 6 variants, one changed decision each | design |
| **select-1** | 200-299 | `base` head to head | variants vs baseline on unseen seeds | selection |
| **select-2** (round robin) | 300-399 | 8 agents vs each other | additivity / non-transitivity. **F86, F108 and hospital-spawn (HS) were added *post hoc* after select-1 (disclosed)** | selection |
| **regression** | 400-449 | lv1 lv2 rush turtle raider pack; v2/v3/cap7 also run as candidates | plan criteria (b),(d); comparison; proxy search | selection |
| **select-3** (round robin) | 500-599 | 7 agents (F cap 8/6-12/10 x garrison/hunt/HS), **post hoc** extension of the F cap line | final choice | selection |
| **freeze** | - | - | `out/v6-claude/source` = garrison 1, hunt_r 6, F cap 10/8, hospital spawn 1 (params baked into source; env var variant vs baked: 80/80 identical draws). Committed at 13:05:50 +0900, before any holdout game | - |
| **holdout** | 1000-1099 (+K 1000-1029) | v2 v3 cap7 base indep1 + lv1 lv2 rush turtle raider pack | final table | opened once, after the freeze |

Methods: agents are deterministic and the map point symmetric, so a side swap replays the mirrored game (0 of 600 select-1 seed pairs and
0 of 40 bake-check seed pairs differed between sides; K side holdout equals Y side). Head to head statistics therefore use the Y side (n = seeds).
Wilson 95% intervals; games share maps and opponents are deterministic, so real uncertainty is wider.

## 1. Iterations: hypothesis -> decision changed -> paired result -> keep / reject

| # | hypothesis (from the observation in Phase 2) | decision changed (`INDEP_PARAMS`) | evidence | verdict |
|---|---|---|---|---|
| H1 | lone enemy F flip buildings 3-5 cells from ~50 idle W (8/200 base losses; official: 13% of v3 losses had a Y W within 1 cell) | `garrison=1`: keep 1 W on every owned building | design +8/-0 (p=.01, saturated); select-1 65-35 vs base; on top of F cap: G1H6F65 vs F65 59-41, G1H6F86 vs F86 58-42, G1H6F108 vs F108 61-39 | **kept** |
| H1b | more garrison, alert scaled | `garrison=2,garrison_alert=1` | select-1 59-41 vs base (G1: 65-35; difference within noise) | rejected (no better than G1, more idle W) |
| H2 | `hunt()` only reacts when a W is adjacent to the flag | `hunt_r=6`: chase flags from up to 6 steps when W beat their escort | select-1 61-39 vs base; combined with G1 67-33 | **kept** |
| H3 | rivals keep ~7 F, base kept 4/3; T20 buildings 10-16 vs 1-7 in the losses | F cap 4/3 -> 6/5 -> 8/6 -> 10/8 -> 12/10 | select-1: 6/5 beats base 87-13; select-2: 8/6 beats 6/5 66-34, 10/8 beats 8/6 71-29, 10/8 beats base 98-2; select-3: 12/10 beats 10/8 58-42 without garrison but 46-54 with garrison/hunt/HS | **10/8 kept**, 12/10 rejected (no gain with the rest, larger F exposure) |
| H5 (post hoc) | reinforcements travel far from the base | `hospital_spawn=1`: spawn at the owned hospital nearest to the goal | select-2: F65HS vs F65 56-38 (6 draws), G1H6F65HS vs G1H6F65 67-25 (8 draws); select-3: G1H6F108HS vs G1H6F108 69-25 (6 draws). Really used: 13 W in a 38-turn game, first at turn 36 | **kept** (small; used late) |
| - | (earlier session's finding) "defense / concentration lose wins" | - | not contradicted for *their* rules; my garrison is 1 W per building plus escorted F, not a blanket guard or freeze; no "concentration" rule was added | see Phase 2 audit |

Interaction check (no cycles): select-2 order F108 > G1H6F65HS > G1H6F86 > F86 > F65HS > G1H6F65 > F65 > base; select-3 order
G1H6F1210HS ~ G1H6F108HS > F1210 > G1H6F108 > F108 > G1H6F65HS > F86. G1H6F108HS has the best worst matchup in select-3 (54%
vs 46% for G1H6F1210HS; their head to head is 54-46, not significant).

## 2. Holdout (seeds 1000-1099; opened after the freeze)

Agent round robin (row = Y, wins-draws-losses of the row agent, 100 seeds each; K side mirrors exactly):

| Y \ K | indep1 | base (`indep-v0`) | cap7 | v3 | v2 |
|---|---|---|---|---|---|
| **indep1** (frozen) | - | 99-0-1 | 100-0-0 | 100-0-0 | 100-0-0 |
| **base** | 1-0-99 | - | 97-0-3 | 99-0-1 | 100-0-0 |
| **cap7** (strongest previously verified) | 0-0-100 | 3-0-97 | - | 57-0-43 | 68-0-32 |
| **v3** | 0-0-100 | 1-0-99 | 43-0-57 | - | 61-0-39 |
| **v2** | 0-0-100 | 0-0-100 | 32-0-68 | 39-0-61 | - |

Styled opponents (seeds 1000-1049, Y side; lv1 lv2 rush turtle raider pack): **every one of the five agents goes 300/300**
(0 forfeits; margin +31 for all; occupation diff 611 for `indep1` vs 792-863 for the others because it ends games earlier) - saturated, uninformative.
K side, `indep1` on 1000-1029 vs base/cap7/v3/v2/lv2/rush: 179/180 (29-1 vs base, 30-0 elsewhere) = identical to Y.

Mean win% of each row over its four opponents (`hold-rr/matrix.txt`): indep1 99.8, base 74.2, cap7 32.0, v3 26.2, v2 17.8; 0 forfeits in
all 1,000 games. Mean score margin of `indep1` (`compare.py`): +33.5 vs v2, +33.4 vs v3, +33.5 vs cap7, +29.2 vs base.

**No local opponent reproduces v3's official record (8W-20L, 29%)**: v3 is 100% against all six styled opponents and 61%
against v2. The audit's warning applies to me too: the local evidence is self-play among my variants plus a saturated pool.

## 3. Representative failure analysis (base -> frozen)

`indep-v0` lost 8/200 games to v3/cap7 (seeds 39, 58, 116 vs cap7; 48, 52, 89, 119, 121 vs v3). Trace of seed 52 (`out/experiments/7-independent-agent(v6)/phase2-analysis/p2-indep-big-Y/replays`,
`out/tools/reporting/trace.py`): at T20 K owned 16 buildings vs my 1 with W 52:50; single unescorted F flipped STA11, DEP16, HOS7, HAL1,
LIB3, ENG5 within 3-5 cells of my ~50 W. `indep1` wins all eight (e.g. seed 52: base 0-29 at T55 -> indep1 34-0 at T35).

## 4. Validation of the exact frozen source / ZIP

| check | result |
|---|---|
| ZIP built with **Windows Python 3.12.7** `make_submission.py` | Originally `out/v6-claude/v6.zip`; byte identical fresh replacement `out/v6-claude/v6.zip`; entries `_generated.py brain.py campus_bot.py main.py protocol.py submission.json`; **all modes `0o100666`, no execute bit** (`out/tools/evaluation/zip_modes.py`). The old duplicate was removed after it was confirmed byte identical. |
| the earlier WSL built `y-agent-indep-v0.zip` | modes `0o100777` on every entry = the defect that made the server reject v1 (`EXECUTABLE_FILE`); **not an upload candidate** |
| official `run_tests.py --zip` (extracts the ZIP and plays it), seeds 3, 16, 21, 52 | `ok: true`, `issues: []`, `warnings: []`, stderr 0 B, max stdout line 22-37 B |
| separate process, official runner, `--jobs 1`, 24 games each | Python 3.14: max turn (turn >= 2) 21 ms, first turn incl. process start <= 230 ms; **Windows Python 3.12.7** subprocess: max turn 45 ms, first turn <= 957 ms (limits 300 ms / 3000 ms); 0 forfeits; outcomes identical between the two interpreters |
| memory | peak RSS 14.6 MiB (limit 384 MiB) |
| in process decide time (Python 3.12.7) | mean ~2-5 ms, p95 < 20 ms |
| exceptions | `decide` is wrapped (fallback = spawn W); 0 tracebacks in every run listed here |

## 5. Selection

Selected by the pre-registered procedure: **`out/v6-claude/source`** (ZIP above). On unseen seeds it beats every previously developed candidate 100-0 (v2, v3, cap7) and the
baseline `indep-v0` 99-1. Whether it beats real teams is **unknown**: the official record (v2 4W-15L, v3 8W-20L; 5W-0L vs W light
opponents, 7W-35L vs W massing ones) comes from opponents that nothing local reproduces.

**Macro of the frozen agent itself** (`out/experiments/7-independent-agent(v6)/holdout/hold-rr/macro.txt`, holdout, vs v3 / cap7; K benchmark from the official replays in brackets):

| | T10 W | T10 F | T20 W | T20 F | T20 buildings |
|---|---|---|---|---|---|
| `indep1` | 22.8 | 10.0 | 69.6 / 68.0 | 9.5 / 9.6 | 9.3 / 9.0 (opponent 6.3 / 6.7) |
| `indep-v0` (F cap 4/3) | 34.1 | 4.0 | 78.6 / 79.5 | 3.8 | 7.2 (opponent 7.8 / 8.1) |
| official K bots [Phase 2] | [26.6] | [6.9] | [67.0] | [6.8] | [7.8] |
| official v2/v3 as Y [Phase 2] | [22.7] | [8.2] | [52.8] | [6.8] | [7.7] |

So `indep1` is **not** above the K benchmark in W: it is at parity at T20 (about 69 vs 67; ratio vs v3 1.14) and below it at T10 (22.8 vs 26.6),
and it holds about 10 F where the K bots hold about 7. It buys that with the F cap: it leads in buildings at T20 (+2.3 to +3.0) but has
~10 fewer W than `indep-v0`. Self-play selection moved the F cap from 4/3 toward 10/8, i.e. toward v2's cap of 12, the direction that the
*official* data associates with W deficits and losses (v2: 1W-15L vs W massing teams; 2W-31L when K led in W at T20). In the local head to head
the extra flags win (buildings compound), but self-play can reward exploiting the baseline's specific weakness (too few flags), and no local
opponent measures the real risk. **This is the main open question for any upload decision**: `indep1` (buildings first) vs a W first agent
such as `indep-v0` cannot be separated with local data.

Other reasons for and against: *for* - 100-0 vs the lineage that produced the official record, no forfeits, times/memory far inside limits,
robust to both sides; *against* - selection among 7-8 variants on 100-seed sets (winner's curse; the holdout confirms superiority only over
my own and earlier bots), deterministic single map outcomes, and the fact that the raids that beat `indep-v0` locally were unescorted
single flags, whereas in the official v3 losses 67% of building flips had K warriors on the building (mean 8), which a 1-W garrison does not
stop. The garrison/hunt gain is therefore evidence about the v2-family opponents, not about real teams.

**Held out opponents:** `PHASE3_PLAN.md` reserved v2, pack and lv1 as opponents never used before the holdout. The pre-freeze regression batch
(seeds 400-449) did use them (v2 as a candidate; pack and lv1 as opponents), a deviation I introduced. The holdout is therefore
**unseen seeds only**; no unseen opponent remained. The results do not depend on that (those opponents are saturated at 100%).

## 6. Deadlines (not re-verifiable: the site's schedule is login gated; taken from `README.md`, checked 2026-09-27)

Cutoffs Sep 28-30 at 08:00 and 20:00 KST (leaderboard updates 10:00 / 22:00); Oct 1: last cutoff 15:00, last upload 23:00,
final code selection + report 23:59 KST; final results Oct 2 08:00. A selected code that fails validation is not replaced
automatically. Recheck the site before any upload. **No upload or selection was made here; none is recommended without a human
decision.**
