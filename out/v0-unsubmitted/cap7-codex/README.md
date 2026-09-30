# cap7 — best local Codex candidate, never uploaded

> **Not a submitted version: it lives under `v0-unsubmitted/` and has no site version number.** This ZIP was never uploaded, never played an official practice battle and has **zero official games**.
> It must not be confused with any site submission (nothing in the records links it to v4 or v5; their source is unavailable).

| item | value |
| --- | --- |
| ZIP | [`cap7.zip`](cap7.zip) (local file name; formerly `y-agent-cap7-low-review.zip`, "cap7 low reserve, for review") — 6,782 bytes; Windows Python, entry mode `0o100666`; created 2026-09-28 16:03; the entry names inside are unchanged |
| Source | [`source/`](source/) = the ZIP contents, extracted (byte identical). `main.py` is the v3 policy with the constants `CAP=7`, `RESERVE=1`, `PLAZA_RESERVE=0` (and `SCORE_WEIGHT`, `BONUS`, `DANGER` at the v3 values) |
| Also present as | `../../experiments/4-code-evolution(cap7)/candidates/cap7.py` (byte identical copy, referenced by the evolution records and loaded by the search scripts) |
| Strategy developed by | **Codex** (GPT-6 family) — weight search, [`../../experiments/3-policy-weight-search(cap7)/`](../../experiments/3-policy-weight-search%28cap7%29/) |
| Local ZIP check | [`local-zip-check.json`](local-zip-check.json): official `run_tests.py --zip` (WSL, Python 3.14.4) `ok: true`, no issues/warnings, 16-turn win 20:0 (seed 0), stdout ≤ 331 B / 20 lines per turn, stderr 0 |
| Old names | `out/y-agent-cap7-low-review.zip`, `out/unsubmitted/cap7-codex/y-agent-cap7-low-review.zip` → `cap7.zip`; `candidates/existing/cap7/` → `source/`; `out/policy-search/candidate-python/` (duplicate) removed; `out/policy-search/local-submission-check.json` and `out/evolution/selected-zip-check.json` were identical and are now `local-zip-check.json` |

## How it was developed

A bounded coordinate search over six decision values of v3 (flag cap, capture reserve with/without the central plaza, target score weight, function bonus, danger penalty) on the official in process engine,
train seeds → unused seeds → final seeds ([`../../experiments/3-policy-weight-search(cap7)/README.md`](../../experiments/3-policy-weight-search%28cap7%29/README.md)). The cap 4 candidate was the textbook over-fit: 16/20 on the search seeds, 43/80 on unused seeds versus v3's 52/80.

## Decisive results (local stand in opponents only)

- Unused Y games: v3 68/120 → cap7 74/120; last 80 games 40 → 45 (one fewer win against the fast attacker). Evolution run: 56 unused Y games v3 36 / cap7 42.
- Real process cross-check against v3: 5W–5L on seeds 0–9, **0W–5L on seeds 600–604** (v3 against itself: 3W–2L) — a counterexample that keeps the +6 wins from being over-read.
- Every later attempt to improve on it failed the adoption rule: evolution (2 generations), three weight search rounds, and three decision policies ([`../../experiments/`](../../experiments/)).
- The independent agent `indep1` (v6) beats it 100–0 on unseen seeds and 30/40 vs 0/40 on the warrior heavy stand-ins.

## Limitations

The gains are a few wins on small local samples with sign flips across seeds (e.g. seed 1100 loss 0:35 → win 26:5 and seed 1103 win → loss for a sibling policy); the opponents are parameter variants of the same v3 family plus the official Lv2; there is no official match with it.

## Verify

```sh
python out/tools/evaluation/verify_artifacts.py
wsl --cd <repo> python3 bots/dist/starter/run_tests.py --zip out/v0-unsubmitted/cap7-codex/cap7.zip
```
