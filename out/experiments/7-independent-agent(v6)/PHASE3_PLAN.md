# Phase 3 protocol (fixed before the runs; 2026-09-29)

Baseline `base` = `indep-v0` behaviour (all new params at their default). Each candidate is the *same source* with an
`INDEP_PARAMS=k=v,...` override, so a paired comparison changes exactly one decision.

## Observation -> decision -> hypothesis (from Phase 1/2 evidence)

| # | Observation | Decision changed | Testable hypothesis |
|---|---|---|---|
| H1 | 8/200 losses of `indep-v0` vs v3/cap7 (seeds 30-129); replay traces show lone enemy F flipping my buildings 3-5 cells from ~50 idle W. Official v3 losses: 335 building losses, K escort mean 8 W, only 13% had a Y W within 1 cell. | `garrison=1`: keep 1 W on every owned building; `garrison=2,garrison_alert=1`: 2 W, +1 when enemy F within 6 / enemy W within 4 | Fewer buildings lost after T10, fewer losses vs v3/cap7, no loss of offensive mass (W is cheap: 17 buildings x 1-2 W ~ 34-68 W) |
| H2 | `hunt()` only reacts when my W is already adjacent to the enemy F's predicted cell. | `hunt_r=6`: send W from up to 6 steps away when their strength beats the F's escort | Enemy F live fewer turns; fewer of my buildings flipped |
| H3 | Enemy (v3/cap7) keeps 6-7 F vs my 3-4; T20 buildings 10-16 vs 1-7 in the losses. | `fcap_early=6,fcap_late=5` | Faster expansion without more F deaths |
| H4 | combination of H1+H2 (and +H3) | `garrison=1,hunt_r=6[,fcap...]` | additive |

## Seeds / opponents (never mixed)

- **Design** seeds 30-129 (already looked at for failure analysis) vs `v3`, `cap7` (where all losses occurred) + regression
  set `lv2, rush, turtle, raider` on 30-59.
- **Select** seeds 200-299: only for the 1-2 candidates surviving design; paired vs `base` (head to head both sides) and vs the pool.
- **Holdout** seeds 1000-1099 and opponents **never used for design/selection**: `v2`, `pack`, `lv1`, plus `base` head-to-head.
  Used once, for the final table.

## Accept / reject (pre-registered)

Accept a candidate for the next stage only if ALL hold: (a) 0 forfeits, 0 tracebacks, max turn <= 120 ms serial;
(b) losses vs {v3,cap7} <= baseline losses (design), and total losses on the regression set do not increase;
(c) head to head vs `base` (both sides, paired seeds) wins >= 55% with the 95% Wilson lower bound not below 45%;
(d) no single opponent's loss count worsens by more than 2 games. A result that rests on <= 2 games, or on one opponent, is
"inconclusive", not accepted. If nothing is reliably better than `base`, `base` is kept (and if v3/cap7/v2 were better it would
be the selected agent -- see final table).

## Caveat

Local opponents are prior agents and hand made bots. Improvement here does not prove a higher win rate against real teams.
