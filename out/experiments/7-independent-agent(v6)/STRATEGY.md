# Independent Y agent — strategy assumptions & evaluation criteria

Written 2026-09-29, **before** any agent code and **before** reading `main.py`, prior
candidates, `out/DEVELOPMENT_LOG.md`, `out/OFFICIAL_MATCH_ANALYSIS.md` or experiment reports.
Sources read: `README.md`, `docs/rulebook.md`, `docs/PLATFORM_OPERATIONS.md` (removed in the cleanup; its content is now in the root README), starter kit
(`bots/dist/starter/**` except `python/main.py`), `engine/`, `runner/`, `mapgen/`,
`config/balance.json`, `out/PROMPT_RECORD.md`. Official kit/SDK (`/api/rules`,
starter policy v4, SDK docs v6) was byte compared with the local
copy: identical except `python/main.py`. No rule drift found.

## Assumptions (each is falsifiable by local matches)

- **A1 Combat is a W count game.** Per cell, W cancel 1:1; a surviving W wipes enemy F/S for free.
  F (5) and S (2) must never stand where enemy W can plausibly arrive with more W than I bring.
  F survives iff my W at the cell >= enemy W arriving there (equal W wipe each other, F/S live).
- **A2 Income dwarfs capture cost.** Income (10 + 2/HALL) is added *before* captures (2, plaza 4,
  library -1), so stock need not be reserved for captures except when >5 capture at once.
  Spend nearly all stock each turn (cap 40 wastes overflow). Leftover stock is worth 0 in tiebreaks,
  surviving units are worth F5/W3/S2 -> convert stock to units on the last turns.
- **A3 Flags persist without a flag-bearer.** A flag is pulled only if my F dies *on* that building.
  So F should move on after capturing instead of parking on owned buildings.
- **A4 Flipping an enemy building needs two turns** (neutralize, then capture) unless combat kills
  the defending F on it (then same turn capture). A mobile W reserve within 1-2 steps of a building
  can save it after an enemy F arrives, so reactive defence is cheaper than static guards.
- **A5 Building value ~ score + function.** HALL (+2 income/turn), ENG (W 3->2: +50% army per
  resource; 2nd ENG useless), DEPOT (+15 once), HOSPITAL (forward spawn), plaza (3 pts, cost 4),
  STATION/LIBRARY/WATCH lower. Early captures also accumulate occupation turns (tiebreak 2).
- **A6 Enemy policy is unknown.** Use worst case (all enemy W within 1 step may arrive) for F safety,
  with an aggressiveness knob; treat inferred enemy intent as speculation.
- **A7 Latency.** Precompute all pairs distances at INIT (3 s budget). Target <= 50 ms mean and
  <= 120 ms max per turn locally (server budget 300 ms, CPU unknown -> 2.5x margin).
- **A8 Instant loss/win.** If my score is 0 while the enemy holds > half of the total I lose
  immediately; conversely zeroing a weak enemy while holding > half ends the game early.

## Evaluation criteria (fixed in advance)

- Primary: candidate-as-**Y** results vs each opponent, seeds 0-9 (= official practice seeds)
  and extended dev seeds 10-29. Report W/D/L, score margin, occupation, unit value.
- Diagnostic: candidate-as-**K** on the same seeds (symmetry / protocol check). A Y-K win rate gap
  > 20 pts or any K only forfeit is investigated before trusting Y numbers.
- Safety gates (hard): 0 forfeits, 0 invalid format lines, stdout/stderr within `limits.json`,
  max turn time <= 120 ms locally, mean per match max <= 80 ms.
- Opponents in Phase 1: official `example_lv1`, `example_lv2` (Python). Local styled opponents
  (rush / turtle / greedy) added for Phase 3.
- Held out seeds (100-139) are not used for design decisions; used only for final selection.
- **Caveat:** the real "medium" practice bot and real teams' bots are not available locally;
  local results do not prove win rates against them.
