# Plan — local evaluation after the 2026-09-29 22:00 round (written before any candidate match)

Baseline: `candidate/` with no overrides = v6 (verified: reproduces all 1,738 recorded v6 turns of games 48–59).
Every variant is the same source with an `INDEP_PARAMS` override, so each changes one decision rule.

| name | override | decision changed | hypothesis (from the 8 official losses) |
| --- | --- | --- | --- |
| `base` | – | – | reference (= v6) |
| `D4` | `defend=1,defend_eta=4` | threat-proportional defence of owned buildings before hunting, trigger at 4 steps | fewer buildings flipped by escorted flags |
| `EG` | `endgame=12` | last 12 turns: exact deadline for flag targets (incl. neutralizing), no far hunting | fewer last-turn steals (game 50), more last-turn neutralizations |
| `F76` | `fcap_early=7,fcap_late=6` | flag cap 10/8 → 7/6 | K bots keep ~7 flags; fewer idle flags = more W |
| `D4EG` | `defend=1,defend_eta=4,endgame=12` | D4 + EG | additive |
| `ALL` | `defend=1,defend_eta=4,endgame=12,fcap_early=7,fcap_late=6` | all three | additive |

Opponents (fixed before the runs; none is a model of a real team):
- design: `v6` (head to head, the only opponent at v6's strength level), `front`, `pressure` (indep-v0 variants from experiment 7),
  `escort` (new, from observable K statistics, calibrated on the OLD agents v2/v3, not on any candidate), `g1e0` (v4/v5 look alike), `indepv0`.
- held out (never used for choosing): unseen seeds with the same pool plus `cap7` and `v3`; K side check.

Seeds: design 4000–4049 (Y). Held out 4500–4599 (Y) and 4500–4529 (K). Nothing is tuned on held-out seeds.

Addendum after the design runs, before any held-out game (04:16 KST): a second design round `design2` was added **post hoc**
(`G0` garrison=0, `G0EG`, `F76EG`, `G0F76EG`, `EG20` endgame=20). By a script slip `design2` also played `cap7` and `v3`
on the design seeds, so these two are not unseen opponents any more (both are saturated at 100% for every variant). Held-out
finalists fixed now: `EG` and `EG20` (the only variants without a pool regression; `EG20` is the only one above 50% against v6
in design, 31–19), with `base` as reference. `D4`, `ALL`, `G0*`, `F76*` are rejected at design (tables in `design_table.md`).

Decision rule (fixed now): keep a variant only if on the held-out seeds (a) it beats `v6` head to head in more than 55 of 100 Y games
(Wilson lower bound > 45%), (b) its total wins over the rest of the pool are not lower than base's by more than 3 games,
(c) no opponent loses more than 3 wins vs base, (d) 0 forfeits, max turn time within limits (serial check), and (e) K side shows no
asymmetry. If none qualifies, v6 stays the best verified agent. A local win is **not** evidence of an official improvement.
