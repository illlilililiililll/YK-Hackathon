# Phase 2 — existing agents, official matches, failure patterns (2026-09-29)

Opened only after the Phase 1 checkpoint commit (12:13 +0900). Every number below is recomputed from raw
files by `out/tools/reporting/official_macro_analysis.py` / `loss_geometry.py` (raw official replay JSON) or from
`out/experiments/7-independent-agent(v6)/*/results.jsonl`; reports written by the earlier session were used only as pointers.

## 1. What each existing agent is (source read)

| agent | source | difference |
|---|---|---|
| v1 = v2 | `main.py` identical (only the ZIP file mode differs) | F cap `min(12, targets+2)`, W with all remaining stock at one spawn site, all W stacks chase the nearest enemy F (else centre buildings), F assigned one per building by `d - score - bonus`, no escort, no garrison, capture reserve 4/2 |
| v3 | v2 with `12 -> 6` (one line) | current `bots/dist/starter/python/main.py` in the tree |
| cap7 ("strongest locally verified") | v3 with F cap 7, reserve 1/0 and constants `SCORE_WEIGHT/BONUS/DANGER` | `out/v0-unsubmitted/cap7-codex/cap7.zip` (never uploaded) |

## 2. Distinguishing the kinds of result (they must not be mixed)

| kind | what | record | evidence |
|---|---|---|---|
| **official opponent games** (real teams, Y side, "내 경기" replays) | v2: games 01-19; v3: games 20-47 | v2 **4W-15L** (19), v3 **8W-20L** (28; 4-12 in 20-35, 4-8 in 36-47) | raw JSON `out/official-replays/*.json`, re-tallied; 0 command errors (3813/3813 `status: ok`), max response 546 ms |
| **official medium bot practice** | v2 and v3, Y, "중 - 수료 기준" | v2 10-0 (log only, no artifact), v3 10-0 (screenshot `v3-practice-result.png` checked at the time: 10/10, 9/28 11:25 — the image file is not in the repository any more; the facts are in `out/DEVELOPMENT_LOG.md`) | says nothing about real teams (see 4) |
| **local engine matches** | earlier session: own hand made opponents; this session: `out/experiments/7-independent-agent(v6)/*` | see Phase 3 tables | not comparable to the above |

Version attribution of each official game: by Y's peak F count in turns 1-15 (12 in all of games 01-19 = v2's cap; 6 in
all of 20-47 = v3's cap). **The UUIDv7 `evaluationId` timestamps must not be used**: games 20-35 are stamped 08:00 KST 28 Sep,
before v3 was submitted (11:24), i.e. they are evaluation slot times. (My first attribution attempt used them and was
wrong; the F cap signature is the evidence, and it agrees with the log's game ranges.)

## 3. Figures from the earlier reports, verified against raw records

| claim | recomputed | verdict |
|---|---|---|
| v2 4W-15L over 19 games | 4W-15L (wins: 08, 15, 16, 18) | reproduced |
| v3 round 20-35: 4W-12L | 4W-12L (wins 20, 25, 27, 32) | reproduced |
| 11 of those 12 v3 losses show a W deficit at T20 | 11/12 (exception: game 34, Y 84 vs K 72, lost T142) | reproduced |
| v3 round 36-47: 4W-8L, 6/8 losses with W deficit at T20 | 4W-8L; 6/8 | reproduced |
| v2 losses: K W > Y W at T10 in 13/15, at T20 in 14/15 | 13/15 and 14/15 | reproduced |

## 4. What the raw data adds (new, not in the earlier reports)

1. **Two kinds of opponent.** K's own W count at T20 splits the 47 games cleanly. K < 30 W (F flooder like lv2/"medium"):
   **5W-0L** (games 08, 15, 18, 20, 25). K >= 30 W (W massing): **7W-35L (17%)**; v2 1-15, v3 6-20.
   => the practice "medium" 10/10 (lv2-like) does not measure the games that decide rank.
2. **T20 W ratio vs outcome (W massing opponents, n=42):** Y/K W < 0.7: 0W-16L; 0.7-0.85: 1W-11L; 0.85-1.0: 1W-4L;
   >= 1.0: 5W-4L. Even parity is only ~55%. (Association, not causation: W count is also the result of earlier fights.)
3. **Loss channel = unopposed escorted flags flipping buildings, not flag kills.** v3 losses: 335 Y building losses in 20 games,
   284 by enemy flag neutralization vs 51 "pulled" (my flag killed on the building); K escort on the building averaged
   8 W (67% had K W there); only 13% had any Y W within 1 cell, 32% none within 3 cells, though Y had ~10 W within 3 cells on
   average. 146 of the 335 (44%) were in Y's own home region (x <= 4) and 174 in the centre. By type over all regions:
   STATION 74, WATCH 54, DEPOT 52, HALL 41, LIBRARY 35, ENG 35, PLAZA 25, HOSPITAL 19. Losing HALL/ENG removes income and the
   2-cost W discount, so it can snowball (hypothesis, consistent with the T20->T40 W gap).
4. **Economy timing:** in v3 losses K captured ENG at turn 8.2 vs Y 10.5 (2 of 20 losses Y never held an ENG), HALL
   6.5 vs 6.8, DEPOT 12.3 vs 9.8, PLAZA 18.7 vs 11.1 (Y earlier at the plaza but then loses it). `v3` gives ENG no bonus
   (`bonus` only for DEPOT/HOSPITAL/HALL).
5. **Waste:** F spawned/dead per game in v3 losses 80.8/79.4 (~400 stock) vs W spawned/dead 209/200. Y stock never hit the 40 cap.
6. **Concentration is not the missing ingredient:** in v3 losses Y's W were *more* concentrated than K's (top-1 stack share at
   T20 0.25 vs 0.17, at T40 0.41 vs 0.15) while K had 2.6x the W at T40 (120 vs 46). K spreads over many buildings and wins on volume.

7. **Macro benchmark of the real W massing K bots** (42 games; mean over games, K vs v2/v3 as Y):

   | turn | K W / F | Y(v2,v3) W / F | buildings K/Y | stock K/Y |
   |---|---|---|---|---|
   | 5 | 6.0 / 6.0 | 3.5 / 6.9 | 1.9/2.3 | 12.5/15.1 |
   | 10 | 26.6 / 6.9 | 22.7 / 8.2 | 4.9/5.7 | 15.3/16.0 |
   | 15 | 50.5 / 6.7 | 43.8 / 7.4 | 6.8/7.9 | 14.0/15.2 |
   | 20 | 67.0 / 6.8 | 52.8 / 6.8 | 7.8/7.7 | 13.2/15.3 |

   K keeps ~7 F (stacks of 1-2), pours everything else into W (+4.4 W/turn T10-T20 vs Y +3.0/turn) and holds *less* idle
   stock. At T20 K's W sit in ~19 stacks (largest ~12) in games K won, vs ~14 stacks with one ~13 blob in the games Y won
   *(speculation: K distributes W to cover many buildings/flags)*. `indep-v0` (F cap 4/3) locally reached 33 W at T10 and 78 at T20
   (vs v3), above this benchmark. **Not true of the frozen `indep1`** (F cap 10/8): 22.8 W at T10, ~69 at T20, i.e. parity at T20 and
   below at T10 (see PHASE3_REPORT §5).

## 5. Failure patterns as observation -> decision -> hypothesis (opponent internals = speculation)

| # | observation | decision in v2/v3 | testable hypothesis |
|---|---|---|---|
| P1 | Y/K W ratio at T20 < 0.85 in 27 of the 35 losses vs W massing teams; K ENG 2.3 turns earlier | no ENG priority; F refilled to cap every turn; capture reserve 4/2 | earlier ENG/HALL + fewer F deaths raise T20 W (tested via local W(t) curves; my agent reaches 78 W vs 60 for v3 at T20) |
| P2 | flags flip undefended buildings while ~10 W are within 3 cells | W stacks always march to the nearest enemy F / centre; nothing guards owned buildings | a 1-2 W garrison per owned building and longer range F hunting reduce building losses (Phase 3 H1/H2) |
| P3 | F die at ~1/turn in losses (80 per game) | F step only around cells adjacent to enemy W, no escort | escort conditioned F movement lowers F losses (implemented in `indep`) |
| P4 | K may be expanding with more F (K F 6.3 vs Y 5.2 at T20 in losses) *(speculation about K's policy)* | F cap 6 (v3) vs 12 (v2) | F cap is a trade-off: v2 (12) lost more; but very low caps slow expansion (H3) |

## 6. Prior experiments (earlier session) — audit

Delegated to a subagent (read only; recomputed from 2,509 in process games + 14 subprocess result dirs; full text:
`prior_experiments_audit.md`), then cross-checked against my own reading of `main.py`/`cap7` (the family is exactly what
the diff showed: constants around one W logic). Findings I rely on:

1. **Arithmetic is exact**: every W/D/L figure in the reports and log matches the raw records (0 forfeits in 2,509 games).
   Issues are interpretive: reused seeds between "train" and "holdout" (hb 10:00 consumed decision's reserved seeds),
   3 post-hoc variants added after seeing results (disclosed), "595 real runs" not reproducible (29 unlogged).
2. **The local opponent pool has no diversity.** v2/v3/cap7/"fast-attack"/"slow-defense"/"unseen-mixed"/"g1-safe-goal" are
   parameter clones of one bot whose W logic is identical (every W stack chases the nearest enemy F; no guard, escort,
   retreat, W first rush). Lv2 wins are saturated (100%) and uninformative.
3. **Defense / concentration "failures" are failures of those implementations on that pool, not of the idea.**
   `defense` (guard within 4): intended site guard rate 0.428 -> 0.658, but that metric is satisfied by construction; the
   escort metric was unchanged (0.480 -> 0.482) and wins fell 17 -> 10 of 28 (1:8 discordant, p=.04, 4 maps).
   `defense-near2`: neutral (16 vs 17). `defend_w` (W chase enemy F within 2 of own buildings first): 5/24 and 9/24 vs cap7 19/24.
   `focus_w` / `local-superiority` / the from scratch all-W-to-one-target "independent": 6/24, 8/28, 4/24. All-in or freeze
   rules are bad; "merge stacks, then push" was never tested. Building loss reductions were an artefact of shorter games
   (per 100 turns 25.2 vs 24.7).
4. **Adaptive production**: +1 game (18 vs 17/28), F only turns 21 -> 1 by construction, sign flips across seeds
   (0:35 loss -> 26:5 win on seed 1100, 29:7 win -> 7:18 loss on seed 1103) = noise; correctly rejected.
5. **F cap / reserve**: flat over cap 5-7, worse at <= 4 and >= 9; the original rejections of cap 4/5/8 rested on n=10 and
   2-3-game gaps. v3 vs v2 is not distinguishable (local head to head 55% [43,67]; official 4/19 vs 8/28, Fisher p=.74).
6. **Winner's curse is visible everywhere**: selection stage gains of +3..+5 games shrank to -9..+1 on every confirmation set.
   Their gate (+2 select, +3 adopt) has low power: the audit's two rough estimates are that it catches a true +8-10-pt gain only
   ~30-46% of the time and adopts a null candidate ~15-19% of the time.
7. **Nothing here measures real teams** (official v2 4W-15L, v3 8W-20L; cap7 and every later candidate have 0 official games;
   the opponent pool changed on 9/29 10:00).

### What this changes in my Phase 3 protocol
- Selection must use **paired seeds, held out seeds, and non-family opponents**; wins over Lv2 / the family pool saturate
  (my own `indep-v0` is already 96% there), so the discriminating instrument is **head to head against the baseline** on
  unseen seeds, both sides, with McNemar style discordant counts (`out/tools/reporting/compare.py`).
- Report per seed discordant pairs, never a raw win count from <= 2 games; keep the holdout unopened until the end.
- Treat any gain that appears only on the design seeds as a probable winner's curse artefact (my six design variants all
  went 200/200 vs v3/cap7 after the baseline lost 8/200: that shows the baseline has fragile trajectories, not that
  the six variants are equally good).
