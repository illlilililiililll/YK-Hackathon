# v6-variants (Claude Opus 5.5, 2026-09-30) — source only, never uploaded

The v6 source ([`../../v6-claude/source/`](../../v6-claude/source/)) with two new switches in `brain.py`, both **off** by default:

- `defend` (+ `defend_eta`): threat-proportional defence of owned buildings before hunting (rejected in experiment 8);
- `endgame`: in the last N turns, flag targets count if reached by turn 160, and far hunting stops (N = 20 adopted as `../v6-endgame20-opus/`).

With the defaults it is v6: fed the official observations it reproduces all 1,738 recorded v6 command turns of games 48–59.
Variants are selected with the environment variable used by the experiment scripts, e.g. `INDEP_PARAMS=endgame=20 python3 main.py`
(never set on the server). Results: [`experiments/8-round-0929-2200(opus)/`](../../experiments/8-round-0929-2200%28opus%29/).
