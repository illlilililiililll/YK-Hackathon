# 8 — 9/29 22:00 public round: attribution, loss mechanisms, endgame fix (Claude Opus 5.5, 2026-09-30)

Model and prompt: [`PROMPT_RECORD.md`](../../PROMPT_RECORD.md). Plan written before any candidate match: [`PLAN.md`](PLAN.md)
(with a dated addendum before the held-out games). Official-match findings: [`OFFICIAL_MATCH_ANALYSIS.md` §9](../../OFFICIAL_MATCH_ANALYSIS.md).
**Local results are not official win rates.** No upload, practice battle, selection change or automation restart was made.

## 1. The round (games 48–59)

The 12 replays were downloaded by the user (the site needs a login this session could not use). Integrity: valid JSON, 12 distinct
game IDs, none repeats an earlier game, all Y side, 1,738 command statuses all `ok`, 0 forfeits. Record **4W–8L**, as seen on the leaderboard.

**Attribution by command replay** ([`replay_commands.py`](../../tools/evaluation/replay_commands.py), [`attribution.txt`](attribution.txt)):
the recorded observations fed turn by turn to `out/v6-claude/source` reproduce **all 1,738 recorded Y command turns exactly**; the v4/v5
look alike, indep-v0 and v3 diverge at turn 1–3. The method was validated on the old games (v3 source 100% on 20–47, v2 source 100% on
01–19, swapped sources diverge by turn 4–5). The site's submission number that carried this code was not checked here.

## 2. Loss mechanisms (official data; details in the analysis §9)

| measured (8 losses vs 4 wins) | value |
| --- | --- |
| flags lost T1–40 | 1.4 per loss (v3 losses: ~79 per game) — the v2/v3 failure is gone |
| W ratio Y:K at T20 | 0.91 (v3 losses 0.74) |
| Y buildings flipped by T60 | 16.4 per loss vs 7.5 per win; 75% with K W on the cell; **95 of 131 with no Y W on the building the turn before** |
| Y vs K W within reach of the flipped building | Y more in 29% of flips 5 turns before, 1% one turn before (`flip_lead.txt`) |
| where the W are at T30 (losses) | K 25% near Y buildings, Y 1% near K buildings (`w_position.txt`) |
| HALL-turns T1–40 Y:K | 28.2:34.1 in losses, 37.0:34.2 in wins |
| decisive turn (score behind until the end) | mid game 31–78 in 5 losses; **144, 150, 160 in 3 losses** (game 50: 19:14 at T158, 13:17 at T160 after two last-turn steals) |

Rejected explanations: wrong submission (command replay), wasted resources (no flag waste, stock never capped).
Supported: practice saturation, local opponents rewarding weaknesses real teams lack (v6 100–0 vs v3 locally, 33% officially vs v3's 29%),
local inferiority at the attacked building with a 1-W garrison that is usually absent, and a too-conservative endgame (2-turn margin).

## 3. Local opponents

Pool: `v6` (head to head), `front`, `pressure` (indep-v0 variants, experiment 7), **`escort`** (new, `out/opponents/escort/`), `g1e0` (v4/v5 look alike),
`indepv0`; plus `cap7`, `v3` (saturated). `escort` was written only from observable K statistics of the 47 old replays (`k_tactics.py`,
`k_tactics_47.txt`: ~7 flags, W from turn 2, escorted flags, ~19 W stacks, local superiority) and calibrated only against the OLD agents
(in process, seeds 0–7: v3 wins 5/8, v2 4/8; official v3 29%, v2 21%). Its v3 loss (seed 6) reproduces the official v3 signature
(W 63:73 at T20, 42:84 at T40, 76 flags lost). It does **not** reproduce what beats v6 (v6 wins 100%), so it is a regression check only.
No local opponent reproduces v6's official 33%.

## 4. Candidates and results (Y side; `base` = v6 behaviour; every variant = same source + one override)

Source with switches: [`out/v0-unsubmitted/v6-variants-opus/source/`](../../v0-unsubmitted/v6-variants-opus/source/) (defaults = v6; verified:
reproduces all 1,738 official v6 turns). New switches: `defend` (threat-proportional defence before hunting), `endgame` (last N turns:
exact T160 deadline for flag targets, no far hunting).

Design, seeds 4000–4049 ([`design_table.md`](design_table.md)); `design2` was added post hoc:

| variant | change | vs v6 W–L | front | pressure | verdict |
| --- | --- | --- | --- | --- | --- |
| base | – | 50 draws | 39 | 34 | reference |
| D4 | defend, trigger 4 steps | 15–35 | 28 | 28 | rejected: the defence pulls W off tempo (as in experiment 6) |
| EG | endgame 12 | 23–27 | 40 | 35 | finalist |
| EG20 | endgame 20 | **31–19** | 41 | 35 | finalist |
| F76 | flag cap 7/6 | 20–30 | 34 | 38 | rejected |
| G0 / G0EG | no garrison (/ + endgame) | 16–34 / 17–33 | 37 / 37 | 38 / 42 | rejected (head to head) |
| F76EG, G0F76EG, ALL | combinations | 18–32, 9–41, 15–35 | 34, 28, 21 | 37, 27, 21 | rejected |

The official intent check (`counterfactual_defense.py`) had already shown that `defend` barely changes the response on the flipped buildings
(W on the building 26% → 27% of flips): the needed W are not within reach in time.

Held out, seeds 4500–4599 (never used for choosing; [`holdout_table.md`](holdout_table.md)):

| variant | vs v6 W–L | front | pressure | g1e0 | indepv0 | escort / cap7 / v3 | pool total (7 opp.) | forfeits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 100 draws | 69 | 82 | 99 | 99 | 100 / 100 / 100 | 649 | 0 |
| EG | 40–60 | 72 | 87 | 99 | 98 | 100 / 100 / 100 | 656 | 0 |
| **EG20** | **56–44** | **76** | **85** | **100** | **99** | 100 / 100 / 100 | **660** | 0 |

EG20 vs base on the pool, paired: +19 / −8 games, net +11, sign test p ≈ 0.05. K side, seeds 4500–4529 ([`kside_table.md`](kside_table.md)):
identical to the Y side on the same seeds (EG20 vs v6 15–15 on both sides). Decision rule of the plan: (a) 56 > 55 and Wilson lower bound
46% > 45% — **passed, narrowly**; (b) +11; (c) no opponent below base; (d) 0 forfeits; (e) no asymmetry → **EG20 adopted as the best
verified local candidate**. EG (12 turns) fails (a).

Mechanism check (seed 4505, baked EG20 vs v6, same result in process and in the runner, 25:11): in the last turns EG20 keeps sending flags to
targets it can still reach by T160 — it neutralizes K's ENG and takes the plaza on the final turn, the steal that decided official game 50.

## 5. Adopted candidate and checks

[`out/v0-unsubmitted/v6-endgame20-frozen-opus/`](../../v0-unsubmitted/v6-endgame20-frozen-opus/) (this version was frozen there byte for byte on 09-30;
the lineage folder `v6-endgame20-opus/` now holds experiment 9's successor): `source/` = the variants source with `endgame=20` baked in
(one line differs, `tools/evaluation/bake_params.py`), ZIP `v6-endgame20.zip` (11,202 bytes).

| check | result |
| --- | --- |
| baked source vs env-var variant (`bake-check/`, 40 games, both sides) | 40 identical draws |
| ZIP built with Windows Python 3.12.7 (official packager) | 6 entries, all mode 0o100666 (`zip_modes.py`) |
| official `run_tests.py --zip`, seeds 52 / 3 / 16 (WSL) | `ok: true`, no issues or warnings, stderr 0 B, longest line 37 B ([`local-zip-check.json`](../../v0-unsubmitted/v6-endgame20-frozen-opus/local-zip-check.json)) |
| serial, WSL Python 3.14 (`serial/`, 18 games) | ordinary turn max 3.9 ms, first turn max 59 ms, 0 forfeits |
| separate process, Windows Python 3.12.7 (`win312/`, 12 games) | same outcomes and margins as 3.14; ordinary turn max 3.8 ms, first turn max 343 ms |

The `defend` code is present but switched off in the adopted source (tested exactly as shipped).

## 6. What remains uncertain

- Effect size is uncertain: design + held out together, the 12-turn window went 63–87 against v6 and the 20-turn window 87–63 — the same
  rule at two lengths moved in opposite directions, and EG20's held-out Wilson lower bound (46%) is only one point above the bar.
- Risk: from turn 141 EG20 stops far hunting; in official games 48 and 59 real teams flipped buildings late, where hunting may have mattered.
- The improvement is local: over v6 head to head (56–44) and over a pool that is mostly saturated. Whether it adds wins against real teams
  is unknown; the mechanism it fixes decided 1 of the 8 official losses (50) and may matter in close games (48, 59).
- The main official loss mechanism (building flips under local inferiority, 5 mid game losses) is **not** fixed: the tested defence rule
  lost locally, and no local opponent reproduces the teams that beat v6.
- The site's current competition selection and the submission number of the code that played 48–59 were not verified in this session.

## 7. Reproduce (repository root)

`<48-59>_*.json` stands for the 12 files of games 48–59 (in bash: the two patterns `4[89]_*.json` and `5?_*.json` in that folder).

```sh
python out/tools/evaluation/replay_commands.py --src out/v6-claude/source out/official-replays/<48-59>_*.json
python "out/experiments/8-round-0929-2200(opus)/round_summary.py" out/official-replays/<48-59>_*.json
python "out/experiments/8-round-0929-2200(opus)/round_diag.py" out/official-replays/<48-59>_*.json
wsl --cd <repo> --exec bash "out/experiments/8-round-0929-2200(opus)/run_eval.sh" design     # also: design2, holdout, kside, bake, serial, win312
python out/tools/reporting/final_table.py --files "out/experiments/8-round-0929-2200(opus)/holdout/results.jsonl" --cands base,EG,EG20 \
  --opps v6,front,pressure,escort,g1e0,indepv0,cap7,v3 --side Y
```
