# Consolidation check plan — 2026-09-29 KST

Question: `indep1` wins 399/400 held out local games against v2/v3/cap7/base, but its 10/8 flag cap buys fewer warriors than the 4/3-cap baseline. Official v3 losses often involved escorted flags and a warrior deficit by turn 20. The following opponents are **local policy variants**, not replicas of another team's private strategy.

- `front`: independent baseline with `fcap_early=6,fcap_late=6,garrison=1,garrison_alert=7,hunt_r=6,hospital_spawn=1`. It keeps more warriors at threatened owned buildings and six flags for expansion.
- `pressure`: independent baseline with `fcap_early=6,fcap_late=5,garrison=0,hunt_r=6,hospital_spawn=1`. It spends more on mobile warriors and sends them toward enemy flags.
- Selection: Y, seeds 2000–2019; candidates `indep1`, `base` (`indep-v0`), cap7; same official engine and runner, same opponent commands. Check outcomes, margin, 10/20-turn flags and warriors, building control, forfeits, time.
- Final untouched evaluation: Y, seeds 2100–2119, same out/opponents and commands. One K side symmetry sample, seeds 2100–2104. Do not tune on final seeds.
- Decision: prefer the candidate with stable wins across both styles and no serious paired regression on the final set. If close, retain the safer proven candidate and state uncertainty. Prior 399/400 result is context, not a selection substitute.

Use `out/tools/evaluation/eval_matches.py` via `wsl_run.sh`; JSONL is the reproducible record. Serial timing and official ZIP checker are separate gates. No online action until local selection and a fresh Windows packaged ZIP are validated.
