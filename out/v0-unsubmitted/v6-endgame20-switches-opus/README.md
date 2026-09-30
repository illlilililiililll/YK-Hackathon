# v6-endgame20 with the experiment 9 switches (Claude Opus 5.5, 2026-09-30) — search source only, never packaged

The frozen v6-endgame20 source plus the midgame rules tested in [experiment 9](../../experiments/9-midgame-policy-search%28opus%29/), each an
`INDEP_PARAMS` switch whose default reproduces the baseline (all 500 search games of the no-override run were identical to the baseline):
`hold`, `hold_src`, `hold_all` (H1), `hfar_mine`, `hfar_keep` (H2), `hub` (H3); `hunt_r` already existed. All are inactive in the last 20 turns.
The search and refine stages ran this code from `v6-endgame20-opus/source/`; it was moved here unchanged when the adopted rule (`hunt_r=1`)
was baked into that folder. Only `hunt_r=1` was adopted; the other switches were rejected and are kept only to reproduce the search.
