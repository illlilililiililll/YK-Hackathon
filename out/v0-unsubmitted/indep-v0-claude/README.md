# indep-v0 — Claude's blind baseline (never submitted)

> **Not a submitted version: it lives under `v0-unsubmitted/` and has no site version number. Do not upload the ZIP in this folder:** it was built under WSL and every entry has execute bits (`0o100777`), the defect that made the server reject v1.
> The submitted successor is [`../../v6-claude/`](../../v6-claude/).

| item | value |
| --- | --- |
| `source/` | the **parametrised** `indep-v0` baseline: `brain.py` (`P` defaults reproduce v0; behaviours added later are off by default and switched with `INDEP_PARAMS=k=v,...`), `main.py` (identical to v6's `main.py`), and the unmodified official helpers. It differs from v6's `source/` only in the defaults of `P` in `brain.py` |
| ZIP | [`indep-v0.zip`](indep-v0.zip) (local file name; formerly `y-agent-indep-v0.zip`) — 9,396 bytes. The **Phase 1 build**: `brain.py` (14,796 B) and `main.py` (2,332 B) exist **only inside this ZIP** — the Phase 1 commit no longer resolves — so it is the only surviving copy of the original Phase 1 source. Entry modes `0o100777` |
| Strategy developed by | **Claude Sonnet 5.5**, from the rules only, before reading any earlier agent — [`../../PROMPT_RECORD.md`](../../PROMPT_RECORD.md) |
| Old names | `candidates/indep/` (sources) → `source/`; `out/indep/y-agent-indep-v0.zip`, then `out/unsubmitted/indep-v0-claude/y-agent-indep-v0.zip` → `indep-v0.zip`; `candidates/indep/{STRATEGY,PHASE1_REPORT,PHASE3_PLAN,PHASE3_REPORT}.md` → [`../../experiments/7-independent-agent(v6)/`](../../experiments/7-independent-agent%28v6%29/) |

## How it was developed

Assumptions and pass/fail criteria were written first ([`STRATEGY.md`](../../experiments/7-independent-agent%28v6%29/STRATEGY.md)); then the agent: canonical frame (K rotated 180° so both sides run the same code), warriors first with a small flag force (cap 4 early / 3 later),
flag bearers only where enough warriors can escort them, warriors escort or intercept enemy flags. Report: [`PHASE1_REPORT.md`](../../experiments/7-independent-agent%28v6%29/PHASE1_REPORT.md).

## Decisive results and limitations

- Cleanup check: re-running the 40 stored `p1-v0c-serial` Phase 1 games (seeds 0–9 vs Lv2, rush, turtle, raider; `--jobs 1`, WSL) from this `source/` reproduced every stored result row (outcome, score, turns, unit values, six timeline snapshots) — so the parametrised defaults do reproduce the Phase 1 behaviour. The pre-fix code that lost 14 games to the `KeyError` no longer exists anywhere; those replays are kept in [`../../experiments/7-independent-agent(v6)/phase1-blind-build/failures/`](../../experiments/7-independent-agent%28v6%29/phase1-blind-build/failures/).
- Phase 1 (official runner, WSL): 150/150 wins against the official Lv1/Lv2 and three fixed local opponents, 30/30 mirror draws, no forfeits — after fixing a `KeyError` that had silently made it passive on 4 seeds (14/150 losses) — evidence kept in `p1-v0-stderr.log`.
- Lost 8/200 games to v3/cap7: unescorted single flags flipping buildings 3–5 cells away from ~50 idle warriors (traces in [`../../experiments/7-independent-agent(v6)/phase2-analysis/failures/`](../../experiments/7-independent-agent%28v6%29/phase2-analysis/failures/)). That is what the garrison / long range hunt of v6 were designed for.
- Hold-out (unseen seeds 1000–1099, Y): 97–3 vs cap7, 99–1 vs v3, 100–0 vs v2; but only 3/40 against the warrior heavy `front`/`pressure` stand ins, where v6 wins 30/40. Its turn 20 warrior count (~78) is above the real K benchmark (~67).
- Whether warriors first (this agent) or buildings first (v6) is better against real teams **cannot be decided from local data**.

## Verify

```sh
python out/tools/evaluation/verify_artifacts.py            # ZIP entries; the ZIP is expected to carry execute bits (do-not-upload evidence)
python out/tools/evaluation/zip_modes.py out/v0-unsubmitted/indep-v0-claude/indep-v0.zip   # FAIL (execute bit present) - expected
python out/tools/evaluation/inproc.py --y indep --k lv2 --seed 3
```
