# Audit of prior (Codex) local experiments — Phase 2

Read only; every count recomputed with plain Python from `games.jsonl`, `*.json`, `summary.json`: 2,509 in process game rows (2,488 unique; see 3) + 14 subprocess result dirs; 0 forfeits anywhere. "Δ" = candidate minus reference wins on the same (opponent, seed, side) pairs; "b:w" = pairs won only by candidate : only by reference; p = two sided sign test; CIs are Wilson unless marked.

## 1. Bottom line
1. **Every win/draw/loss number in the reports and DEVELOPMENT_LOG matches the raw records.** Problems are interpretive (section 3), plus a few things that cannot be reproduced.
2. **All local opponents are parameter clones of one bot** (the v2 skeleton) or the official Lv2. Their warrior logic is identical: each W stack BFS chases the nearest enemy F (else central buildings); no guard, escort, retreat or bait. Bots are deterministic (21 duplicated cap7 games in two experiments gave identical winner/score/turns), so a "game" is one (map seed, parameter setting) cell.
3. **No tested idea shows a credible win gain.** Defense/concentration rules lose big; adaptive production is +1 game. The one repeatable positive is cap7 (+cap 7, reserve 1/0) over v3: about +12 pts vs the family pool, but only +5..+10 pts over the mirror baseline head to head and never significant on a single confirmation set.
4. Selection stage gains of +3..+5 games shrank to -9..+1 on confirmation for cap4, reserve only, safe_goal, cap6-low, score-half (winner's curse). **cap7-low is the exception** (train2 +5/30 -> holdout2 +6/80 -> final +5/80), still small.
5. Nothing here measures performance vs real teams (official v2 4W-15L, v3 8W-20L). cap7 and all later candidates have 0 official games.

## 2. Opponents actually used (in process unless noted)
| Name | What it is | Notes |
|---|---|---|
| v2 | v3 code, F cap 12 | |
| v3 ("v3-like", "6-flag K", "6명형") | F cap 6, reserve 4 (plaza owned: 2) | = submitted v3 |
| cap7 | cap 7, reserve 1/0 | parent of most candidates |
| fast-attack | cap 3, reserve 0/0 | spends almost everything on W |
| slow-defense ("defensive") | cap 8, reserve 6/4, danger 8 | not defensive: slower spending, more F, same W logic |
| unseen-mixed ("mixed attacker") | cap 5, reserve 0/0, score 1.8, bonus 0, danger 0 | |
| g1-safe-goal ("past strong") | cap7 + F target penalty if enemy W adjacent | beats its parent: cap7 as Y wins 4/25 vs it |
| lv2 | official example bot | candidates win 100% (cap7 51/51, v3 42/42): uninformative, 12-20% of most "n" |

## 3. Experiments and recount
| Exp | Change tested | Design -> held out seeds (n) | Rule | Stated / recount |
|---|---|---|---|---|
| Cap sweep | F cap 4/5/8 vs 6; v2=12 | seeds 0-9, n=10 each, no holdout | none | cap6 9/10 vs v2; cap4 6/10 vs cap6, 7/10 vs v2 -> "rejected" (7<9); cap5 3/10, cap8 4/10, cap6 mirror 4/10. Exact. Variant sources (`main_cap*.py`) no longer exist: caps cannot be verified from source |
| policy search (1,030 g) | cap, reserve, score, bonus, danger; 5 stages | 20-23 -> 100-107; 30-35 -> 200-207; final 300-319 (Y, 80) | top-k advance; no numeric threshold | cap7-low 45 vs 40 on final; Y 74 vs 68 /120. Exact |
| evolution (566 g) | safe_goal, focus_w, defend_w, adaptive_cap, from scratch "independent" | 400-403 (24/policy) -> 500-507 (Y 56, K 14) | pre-registered: +3 over both incumbents, no opponent drop >2, 0 forfeits | none promoted. Exact. "595 real runs": 28 of 29 extra games traceable (7 smoke, 5 subprocess, 10 process-context, 5 failure replays, 1 zip); 6 decision `cases/` and 5 `failures/` replays match games.jsonl |
| hb 9/28 (260 g) | cap6/5 x reserve 0/1 | 700-703 -> 800-807 | +2 select, +3 adopt | cap6-low 32 vs 31; rejected. Exact |
| hb 9/29 02:00 (126 g) | danger 0/8, bonus 0, score 2, cap9 | 900-902 (21/policy) | +2 select | none; exact |
| decision (294 g) | defense, adaptive, combined + 3 post-hoc variants | 1100-1103 (28/policy); K diag 1100-1101 | pre-reg +2 select, +3 holdout; variants added after seeing results (disclosed) | none pass; holdout never opened. Exact |
| hb 9/29 10:00 (233 g) | cap5, danger6, bonus3, score 0.5 | 1100-1102 -> 1200-1205 | +2/+3 | score-half 23 vs 26; rejected. Exact |

**Interpretation problems (not number mismatches)**
- **Duplicates:** hb 10:00 train re-ran cap7 on seeds 1100-1102 x 7 opponents = 21 rows identical to decision's (outcomes 21/21 identical). It also consumed 1200-1205, decision's "reserved" holdout. It ran after decision (11:26 vs 11:11) but DEV LOG lists it first. My pooled stats below are de-duplicated.
- decision report shows only site guard rate 0.428->0.658 for defense. The PLAN's other metric, flag escort, is 0.480->0.482 (only in result.json). Building losses look lower (756 vs 839) only because games are shorter (107 vs 121 turns); per 100 turns 25.2 vs 24.7; W lost/100t 243 vs 226; F lost/100t 86 vs 82.
- "Unused Y 120 games" (68 vs 74): holdout2 (Y only 29 vs 28) already chose cap7-low over large-bonus; the gain is +5 from `final`; holdout2 has 16/80 saturated Lv2 wins.
- Evolution REPORT quotes "0:15 / 9:6" (buildings) next to scores; harmless.

## 4. Targeted evaluations
**(a) Defense / escort.**
- decision `defense` (guard within 4, keep min(count, threat+1), never enter a stack >= mover): site guard 0.428->0.658, but the metric uses the policy's own radius-2/1 test (satisfied by construction); flag escort unchanged; wins 17->10/28 (1:8, p=.04), 0/4 vs v3 (was 3/4), paired score diff -13.8 [-24.5,-3.0], W gap at 40 +20.6->+5.0. `defense-near2`: guard 0.643, wins 16 (5:6), score -2.0 [-14.6,+10.7], K 5/14 vs cap7 8/14 (diagnostic). Metric moved, wins did not; near2 is neutral, not shown harmful.
- evolution `defend_w` (W chase enemy F within 2 of own building first; no escort metric logged): 5/24 and 9/24 vs cap7 19/24 (0:14; 1:11); final 26/56 vs 42 (3:19, p=.001). `safe_goal` (F survival not logged): train 22/24 vs cap7 19 (+3, 4:1) -> final 42 vs 42 (8:8); K 9/14 vs 5/14 (4:0, p=.12, diagnostic); by opponent +3 slow / -3 fast (n=8 each, noise). Its clear edge is over its parent: 8/12 as Y.

**(b) Concentration.** `focus_w` (all W to the single enemy F nearest centre): 5/24 and 6/24 vs cap7 19/24 (0:14, 0:13); by turn 20 buildings 7.3 vs 9.1, games 91 vs 115 turns. `local-superiority` (W advance only if allies within 1 of target cell > enemies, else freeze): 8/28 vs 17 (1:10, p=.012); site guard .499, escort .486, W gap@40 +18.0 (vs +20.6), buildings lost/100t 27.6 (24.7), F lost/100t 91.5 (82.4): no intended metric improved. From scratch "independent" (all W to one target): 4/24, 16/56 final. Credible only as "these all-in / freeze implementations are bad vs this pool"; proper concentration (merge stacks, then push) was never tested.

**(c) Adaptive production.** decision `adaptive`: after turn 9, if enemy W >= own+8 (margin4: +4), or >=2 F lost last turn, or threatened while behind: F spawn <=1, reserve capture cost, F=0 if W unaffordable. F-only turns (21-40) 21->1 (0 for margin4) by construction; F lost/100t 82->69; wins 18/28 vs 17 (3:2; margin4 2:1); paired score diff +3.9 [-2.0,+9.7]. Single game flips 0:35->26:5 (seed 1100) and 29:7->7:18 (seed 1103). Relative to v3 as reference adaptive is +7:0, but cap7 is already +7:1, so adaptation adds ~0. Evolution `adaptive_cap` (a different rule) was -3/24 (2:5): sign flips across implementations = noise. One K turn hit 313 ms in process (timeout risk unchecked).

**(d) F cap / reserve / plaza.** Flat over cap 5-7, worse at <=4 and >=9. cap4: +4/20 train -> -9/80 holdout (9:18, p=.12; ex-Lv2 27 vs 36). Reserve alone (1/0 or 7/4): +5/20 train -> 0 and -1 /80. cap9+reserve 2/1: -7/21 (1:8; one of 5 tested, nominal p=.04). cap6-low +3/24 -> +1/48; cap5-low +3/24 (hb 9/28) then 0/21 (hb 10:00, new seeds); 3 of 4 hb 10:00 candidates tied cap7 at 12/21. cap7 and reserve 1/0 were never separated. v2 -> v3 (12 -> 6): seeds 0-9 gave 9/10 and 2/10, but later in process v3 vs v2 (Y) is 34/62 = 55% [43,67]; official v2 4/19 vs v3 8/28, Fisher p=.74.

## 5. Statistical credibility of headline claims
| Claim | n | Δ / rate | 95% / p | Flags |
|---|---|---|---|---|
| cap7 > v3, ps final | 80 | +5 (17:12) | [-7,+19] pts; p=.46 | 4 family opponents, Y only |
| cap7 > v3, pooled post-selection (ps final, evo train+final, decision) | 202 (36 seed clusters) | +24 (46:22) = +12 pts | naive [+4,+20]; cluster bootstrap [+3,+20]; p=.005 | vs family pool only |
| cap7 vs v3 head to head | in process 39/71 (55%); +subprocess 44/86 (51%) | mirror baseline v3-v3 Y 45% [33,58] | [41,61] | seeds 600-604 subprocess cap7 0/5 (v3 mirror 3/5); seeds 0-9 5/10; inconclusive, not zero |
| safe_goal > cap7 | 24 -> 56 | +3 -> 0 | 4:1 -> 8:8 | winner's curse (92% -> 75%) |
| defense harms | 28 | -7 (1:8) | p=.04 | 4 maps |
| local-superiority / focus_w / defend_w harm | 28 / 24 / 24 | -9 / -14 / -14 | p<=.012 | 4 maps; crude rules |
| adaptive helps | 28 | +1 (3:2) | p=1.0 | pre-reg reject fine; not evidence of harm |
| cap4 rejected | 80 | -9 (9:18) | p=.12 | not significant; original cap4 "rejection" was 2 games of 10 |
| v3 better than v2 | 62 local; 19 vs 28 official | 55%; 21% vs 29% | [43,67]; p=.74 | 9/10 on seeds 0-9 was a lucky set |
Gate power (simulation, 30% discordant pairs, 4 candidates, +2/24 select then +3/48 adopt): a null candidate set is adopted 19% of the time (7% for one null candidate); a true +8 / +10 / +15 pt gain only 39% / 46% / 67%. Verdicts are mostly "cannot tell". Unjustified: rejecting cap4/5/8 at n=10 (<=3-game gaps); "regression" claims from n=6-8 per opponent cells (+-2 games).

## 6. What this can / cannot say about real teams
- Can: no crashes/forfeits (0 in 2,488 unique games); within v2-family production variants, extreme caps and several W behaviour rules are clearly worse.
- Cannot: any real team win rate. v3 wins 52% [45,58] of 248 local family games and 100% vs Lv2, vs 29% [15,47] officially; the family is easier and different. No local opponent guards, escorts, rushes with W, or plays the official W heavy openings (official losses: K W > Y W at turn 20 in 14/15 v2 and 17/20 v3 losses); official own building guard rate in games 31/34 is 13%/24% vs local 41%. cap7, adaptive, safe_goal never played an official game; the official records cannot separate v2 from v3 (p=.74), and the pool changed at 9/29 10:00.
- For Phase 2: paired seeds, >=250 pairs to see +10 pts, non-family opponents (W first rush, flag heavy, W with guards), report seed cluster CIs, treat Lv2 wins as uninformative.
