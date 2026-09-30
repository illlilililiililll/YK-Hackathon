# Plan — midgame policy search on v6-endgame20 (written 2026-09-30 12:15 KST, before any candidate match)

Baseline (frozen, never edited): `out/v0-unsubmitted/v6-endgame20-frozen-opus/source/` (= `v6-endgame20-opus` as of 09-30 04:24;
byte identical source and ZIP; reproduces all 100 recorded experiment 8 held-out games vs front/pressure, stage `repro`).
Lineage: `out/v0-unsubmitted/v6-endgame20-opus/source/`. New rules are switches whose defaults reproduce the baseline; a candidate
= one `INDEP_PARAMS` override. Every new rule is active only for `turn <= 160 - endgame` (T1-140), so the endgame branch is unchanged.

## What was measured before this plan (no candidate involved)

- `screen` (baseline vs 16 opponents, seeds 7000-7049, Y): challenging = v6 28-22, F76 28-22, G0 29-21, pressure 37-13,
  D4 39-11, F76G0 40-10, front 41-9; the other 9 are 50-0 (saturated).
- `signature_screen.txt`: losses to F76/G0/D4/pressure/front have the official loss signature (more own flips T11-140,
  ~1.5-2x lost score-turns, negative HALL+ENG-turn difference, about half decided inside T11-140). Losses to v6 (mirror) do not:
  score-turn difference 0, never decided before T141 — v6 is a floor check, not a search signal.
- `w_orders.txt` (official games, brain replay): 66-68% of the orders given to Y warriors within 3 steps of a building in the
  3 turns before it flipped came from flag hunting (`hunt`, `hunt_far`); `hunt_far` sent 45-50% of them away; the garrison rule 4-5%.
  At onset only 13-17% of Y warriors stood within 3 steps; in ~56% of flips Y could have had a local majority within the flag's distance.

## Reward (fixed now)

Primary: match outcome, W = 1, D = 0.5, L = 0, **paired** with the baseline on the same (opponent, seed, side).
Secondary (diagnostics / tie breaks only, never optimized on their own): score margin, own flips T11-140, lost score-turns,
score-turn and HALL+ENG-turn differences (`out/tools/evaluation/midgame_metrics.py`), forfeits, max turn time.

## Opponents and seeds (fixed now)

| set | opponents | seeds | use |
| --- | --- | --- | --- |
| screen | all 16 | 7000-7049 Y | opponent selection only (done) |
| search | F76, G0, D4, pressure (+ v6 floor) | 5000-5099 Y | choosing candidates |
| final, challenging held out | **front, F76G0** (never used in search) | 6000-6199 Y, 6000-6099 K | adoption |
| final, challenging search opponents | F76, G0, D4, pressure | 6000-6199 Y, 6000-6099 K | adoption (unseen seeds) |
| final, floor | v6 | 6000-6199 Y, 6000-6099 K | head to head floor |
| final, regression | cap7, escort, g1e0, indepv0, v3, pack, raider, rush, turtle | 6000-6099 Y | regression only |

Opponent sources: F76/G0/D4/F76G0 = `v6-variants-opus` with the experiment 8 overrides; front/pressure = indep-v0 overrides
(experiment 7); the rest are the files in `run.sh`. All matches: isolated subprocesses (`eval_matches.py` via `wsl_run.sh`).

## Hypotheses and search budget (fixed now; at most 3 hypotheses x 3 variants, one refinement round, then at most 2 finalists)

- **H1 hold** — before hunting, a valuable own building (HALL, ENG, or >= 3 points) with an enemy flag within 3 steps keeps
  `need` = enemy W within the flag's distance + 1 warriors, taken only from W on it or within `hold_src` steps; if they are not
  enough, nothing is held (no trickle). Variants: `hold_src=1`; `hold_src=2`; `hold_src=1` for every own building.
- **H2 hunt discipline** — far hunting stops pulling defenders away. Variants: `hunt_far` only for enemy flags whose predicted target
  is my building; `hunt_far` never takes W within 2 steps of a valuable own building that has enemy W within 4; `hunt_r` 6 -> 3
  (bounded parameter, existing structure).
- **H3 hub** — leftover W (no convoy duty) within `hub_r` steps of a valuable own building where enemy W within 4 outnumber mine
  reinforce it (until mine exceed theirs) instead of walking to the attack target. Variants: `hub_r` 4 / 6 / 8.

## Decision rules (fixed now)

Finalist (search seeds): reward over the 4 search opponents >= baseline + 8 points (of 400) and one-sided sign test on discordant
pairs p < 0.10; no search opponent more than 4 points below baseline; v6 floor >= 45 of 100.
If no variant of a hypothesis improves the search reward, that hypothesis is dropped (no further tuning of its weights).

Adoption (final seeds, run once): (a) paired reward over the 6 challenging opponents, Y and K, higher than baseline with a one-sided
sign test on discordant pairs p < 0.05; (b) the held-out pair (front + F76G0) not below baseline; (c) no single opponent more than
3% of its games below baseline, regression pool at most 2 points below in total; (d) v6 floor: points >= 50%;
(e) 0 forfeits, serial timing well under 300 ms; (f) K side not reversed. Otherwise v6-endgame20 stays the best verified version.
A local improvement is not evidence of an official improvement.
