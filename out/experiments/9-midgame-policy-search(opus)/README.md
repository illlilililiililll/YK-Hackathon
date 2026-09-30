# 9 — Midgame policy search on v6-endgame20 (Claude Opus 5.5, 2026-09-30)

Model and prompt: [`PROMPT_RECORD.md`](../../PROMPT_RECORD.md). Plan fixed before any candidate match: [`PLAN.md`](PLAN.md) (12:15 KST).
Official-match findings: [`OFFICIAL_MATCH_ANALYSIS.md` §10](../../OFFICIAL_MATCH_ANALYSIS.md).
**Local results are not official win rates.** No upload, practice battle, selection change or automation restart was made.
"Reinforcement learning" here means repeated policy search scored by complete simulated games; no neural or tabular model was trained.

**Outcome: adopted `hunt_r=1` (no far hunting of enemy flags) in [`out/v0-unsubmitted/v6-endgame20-opus/`](../../v0-unsubmitted/v6-endgame20-opus/)**,
one changed line against the frozen baseline [`v6-endgame20-frozen-opus/`](../../v0-unsubmitted/v6-endgame20-frozen-opus/).
On untouched seeds it beats the baseline against every challenging local opponent on both sides (+159 points of 1,800 paired games,
sign test p < 0.001), and beats the frozen baseline head to head 183–117 (post hoc). It does **not** reduce own-building flips; it wins
more of the midgame by keeping warriors with the main group. **Regression against a stated requirement:** early expansion is slightly worse —
at T20 the opponent leads on score (16.0 : 17.3, baseline 16.7 : 16.7); it is even again by T40.

## 1. Baseline and setup checks

- Frozen baseline = `v6-endgame20-opus` as of 09-30 04:24 (source and ZIP copied byte for byte; `verify_artifacts.py` checks both folders).
- `repro`: the frozen source reproduces all 100 recorded experiment 8 held-out games vs front/pressure (outcome, score, turns).
- All matches are isolated subprocesses (`eval_matches.py` via `wsl_run.sh`); `inproc.py` was only used for single diagnostic games.
  `wsl_run.sh` now takes `YKRUN=<dir>` so this job used its own mirror (`~/ykrun-midgame`).
- New per-game diagnostics in every row (`out/tools/evaluation/midgame_metrics.py`, window T11–140): own flips, flips with no own W on
  the building, lost score-turns, score-turn and HALL+ENG-turn differences, decisive turn. Official and local replays use the same code.

## 2. Midgame behaviour on the official games (observed, not counterfactual)

Games 60–71 (9/30 10:00 round, found in `official-replays/`, not analysed before) were also played by v6 code (1,650/1,650 turns,
6W–6L), which gives an independent sample next to 48–59. Both samples show the same mechanism (`w_orders.txt`, analysis §10):

| three turns before an own building flipped (T11–140) | 48–59 | 60–71 |
| --- | --- | --- |
| flips | 322 | 282 |
| Y W within 3 steps / more than 6 steps away | 13% / 59% | 17% / 56% |
| orders to the Y W within 3 steps: flag hunting (`hunt` + `hunt_far`) | 66% | 68% |
| … of which `hunt_far` moved away from the building | 45% | 50% |
| escort / rally / garrison | 18 / 11 / 5% | 16 / 13 / 4% |

`w_orders.py` replays the recorded observations through the v6 brain and tags each warrior move with the rule that issued it; the brain
reproduces every recorded turn, so the tags are what happened. What removing a rule would have done in those matches is **not** observable.

## 3. Discriminating evaluation (step 3)

`screen` (frozen baseline, seeds 7000–7049, Y) against the previous pool, the four remaining fixed bots and v6-family variants used as
opponents: challenging = v6 28–22, **F76** 28–22, **G0** 29–21, **pressure** 37–13, **D4** 39–11, **F76G0** 40–10, **front** 41–9;
cap7, escort, g1e0, indepv0, v3, pack, raider, rush, turtle are all 50–0 (saturated, regression only).
`signature_screen.txt`: losses to F76/G0/D4/pressure/front have the official loss signature — more own flips, ~1.5–2x lost score-turns,
negative HALL+ENG-turn difference, about half decided inside T11–140 (official losses: 79%). Losses to v6 do not (mirror match,
score-turn difference 0, all decided after T140), so v6 is a floor check only. No opponent models a real team.

## 4. Reward, partitions, budget (PLAN.md, fixed before candidates)

Reward: W = 1, D = 0.5, L = 0, paired with the baseline on the same (opponent, seed, side); margin, flips, lost score-turns, production
and forfeits are diagnostics only. Seeds: screen 7000–7049, search 5000–5099 (Y), final 6000–6199 (Y) + 6000–6099 (K), regression 6000–6099 (Y).
Search opponents F76, G0, D4, pressure (+ v6 floor); **front and F76G0 held out** until the final. Budget: 3 hypotheses x 3 variants,
one refinement round, at most 2 finalists, one final run.

## 5. Candidate history (search seeds 5000–5099, Y; [`search_table.txt`](search_table.txt), [`refine_table.txt`](refine_table.txt))

Switch source: [`out/v0-unsubmitted/v6-endgame20-switches-opus/source/`](../../v0-unsubmitted/v6-endgame20-switches-opus/source/)
(defaults = baseline; `L0` = that source with no override was identical to the baseline in all 500 games). Every rule is off in the endgame window.

| cand | rule (one change each) | pool pts (base 288 / 400) | +/− pairs | sign p | worst opponent | v6 (of 100) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1a/b/c | hold valuable (or all) buildings against a flag within 3 with W already within 1–2 steps | 264 / 265 / 252 | −23 to −36 net | 0.97–1.0 | G0 −10, G0 −13, D4 −15 | 41 / 37 / 46 | rejected (like experiment 8's `defend`) |
| H2a | far hunting only for flags heading to my building | 263 | +62/−87 | 0.98 | D4 −14 | 56 | rejected |
| H2b | far hunting never takes W near a valuable building with enemy W close | 275 | +65/−78 | 0.88 | D4 −6 | 59 | rejected |
| H2c | `hunt_r` 6 → 3 | 306 | +79/−61 | 0.075 | D4 −5 | 73 | not a finalist (D4 past −4) |
| H3a/b/c | leftover W reinforce an outnumbered valuable building within 4/6/8 steps | 272 / 278 / 279 | −9 to −16 net | 0.81–0.94 | D4 −8 to −13 | 37 / 60 / 59 | rejected |
| refine H2r1 | **`hunt_r=1`: no far hunting** | **317** | **+81/−52** | **0.007** | G0 −1 | 66 | **finalist** |
| refine H2r2 / H2r4 | `hunt_r` 2 / 4 | 309 / 308 | +73/−52, +80/−60 | 0.037 / 0.054 | G0 −5 / pressure −5 | 67 / 70 | not finalists |

Reading: rules that pull more warriors toward threatened buildings (H1, H3) lose; the only rule family that helps is taking far flag
hunting away, and it helps most when removed completely.

## 6. Final comparison (untouched seeds, run once; [`final_table.txt`](final_table.txt))

Finalist baked with `bake_params.py` (frozen source + `hunt_r=1`); `bake-check`: 40/40 identical draws against the searched env-var variant.

| opponent | Y 6000–6199 base → nofar | K 6000–6099 base → nofar | both sides |
| --- | --- | --- | --- |
| D4 | 139 → 165 | 75 → 85 | +36 |
| F76 | 134 → 160 | 73 → 76 | +29 |
| G0 | 135 → 153 | 66 → 80 | +32 |
| pressure | 171 → 177 | 79 → 87 | +14 |
| **front** (held out) | 144 → 164 | 68 → 77 | +29 |
| **F76G0** (held out) | 155 → 168 | 78 → 84 | +19 |
| **6 challenging** | 878 → 987 (+253/−144) | 439 → 489 (+125/−75) | **1,317 → 1,476 of 1,800 (73.2% → 82.0%)** |
| v6 (floor) | 114 → 129 | 59 → 60 | 173 → 189 of 300 |
| regression pool (9 bots, Y 6000–6099) | 897 → 898 of 900 | | indepv0 −2, g1e0 +3, others 100 |

- Discordant pairs over the challenging pool: 378 better / 219 worse, share 63% (95% Wilson 59–67%), sign test p < 0.001; held-out
  pair alone 125/77 (55–68%). v6 floor 63% (57–68%).
- Diagnostics (challenging pool, mean per game): own flips T11–140 30.3 → 32.8 (worse), lost score-turns 1,091 → 1,238 (worse),
  score-turn difference +461 → +581, HALL+ENG-turn difference +42 → +87 (better).
- Losses 483 → 324; decided inside T11–140 263 → 182 (−31%), after T140 220 → 142. v6: the mirror's 127 late knife-edge losses become
  111 losses, 72 of them decided in the midgame (no longer a mirror).
- Cost: at T20 the opponent is ahead on score (16.0 : 17.3 vs 16.7 : 16.7 for the baseline; buildings 7.9 : 8.0 vs 8.1 : 7.9); even by T40.
  Many of the 219 worse pairs start with a large T20 deficit (e.g. front seeds 6011, 6012, 6054: 13:24, 13:21, 9:23).
- Forfeits 0 in all 6,000 final games.
- **Post hoc (not in PLAN.md, run after the decision; stage `h2h`)**: finalist vs frozen v6-endgame20 head to head, same final seeds:
  Y 124–76, K 59–41, together 183–117 (61%, 95% Wilson 55–66%), 0 draws, 0 forfeits; T20 score 15.7 : 17.7 again, T40 17.1 : 16.7.

Decision rule of the plan: (a) p < 0.05 ✔ (b) held-out pair +48 ✔ (c) no opponent below baseline by more than 3% (worst indepv0 −2%),
regression pool +1 ✔ (d) v6 floor 63% ≥ 50% ✔ (e) 0 forfeits, serial turns ≤ 3.6 ms ✔ (f) K side +50 ✔ → **adopted**.

## 7. How the change relates to the official failure

- Supported: the removed rule is the one the official replays show pulling nearby warriors away from buildings about to flip (§2), and
  against local opponents whose wins have the official loss signature, midgame-decided losses fall by a third.
- Not supported: the rule does not stop flips (own flips rise ~8%). The gain appears as more held production and score-turns, i.e. a
  stronger main group, not better point defence. Targeted defence (H1) and reinforcement (H3) again lost locally.
- Unknown: whether real teams, which beat v6 in 14 of 24 official games, respond like these local opponents. The endgame code path is
  unchanged (`hunt_r` is read only by `hunt_far`, which v6-endgame20 already skips in the last 20 turns; `check_nofar.py`); seed 4505,
  experiment 8's endgame example, is still won (35:2; the baseline 25:11 via a final-turn plaza capture).

## 8. Checks of the adopted source

| check | result |
| --- | --- |
| `check_nofar.py` | midgame: baseline chases a flag 4 steps away, adopted source does not; endgame: identical |
| ZIP (official packager, Windows Python 3.12.7) | `v6-endgame20-nofar.zip`, 11,200 bytes, 6 entries = source, all 0o100666 |
| official `run_tests.py --zip`, seeds 52 / 3 / 16 (WSL) | `ok: true`, no issues or warnings, stderr 0 B, longest line 37 B |
| `serial` (WSL Python 3.14, 18 games) / `win312` (Windows 3.12.7, 12 games) | ordinary turn max 3.1 / 3.6 ms, first turn max 47 / 248 ms, 0 forfeits, same outcomes on both |
| `verify_artifacts.py` | all artifact checks passed |

## 9. Reproduce (repository root)

```sh
wsl --cd <repo> --exec bash "out/experiments/9-midgame-policy-search(opus)/run.sh" <stage>   # repro screen search refine bake final timing h2h
python "out/experiments/9-midgame-policy-search(opus)/paired.py" "out/experiments/9-midgame-policy-search(opus)/final/results.jsonl" \
  "out/experiments/9-midgame-policy-search(opus)/final-k/results.jsonl" --pool F76,G0,D4,pressure,front,F76G0
python "out/experiments/9-midgame-policy-search(opus)/timeline.py" "out/experiments/9-midgame-policy-search(opus)/final/results.jsonl" --opps front
python "out/experiments/9-midgame-policy-search(opus)/signature.py" --official out/official-replays/<48-71>_*.json --local "out/experiments/9-midgame-policy-search(opus)/screen/results.jsonl"
python "out/experiments/9-midgame-policy-search(opus)/w_orders.py" out/official-replays/<48-59>_*.json
python "out/experiments/9-midgame-policy-search(opus)/check_nofar.py"
```

Games are deterministic, so every stage reproduces its `results.jsonl` (the `repro` stage checks this against experiment 8).
Next experiments: (1) an official round played by this version, analysed with `w_orders.py` and `midgame_metrics.py` against games
48–71 (same metrics, same windows) — the only way to learn whether real teams respond like the local opponents; (2) keep far hunting only
in the opening (e.g. the first 20 turns) to recover the T20 deficit — not run, because it would need a new search and a new untouched final.
