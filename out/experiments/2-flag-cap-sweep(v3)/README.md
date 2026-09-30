# Flag bearer cap sweep — how v3 was chosen (2026-09-28, Codex)

**Models.** Primary: **v3** (Codex). Also: **v2** (the 12 flag baseline, [`../../v1-v2-codex/`](../../v1-v2-codex/)), temporary variants with caps 4, 5 and 8 (not kept as files; recreate them as shown below) and the official Lv2 as an opponent.

Question: do fewer flag bearers (`F`) than v2's cap of 12 give more warriors (`W`) early and better centre control? Only `min(12, len(targets) + 2)` in `main.py` was changed.
Model: Codex (GPT-6 family). Prompt: P2 in [`../../PROMPT_RECORD.md`](../../PROMPT_RECORD.md). Interpretation and the public match evidence behind the hypothesis: [`../../OFFICIAL_MATCH_ANALYSIS.md`](../../OFFICIAL_MATCH_ANALYSIS.md) §3.1, §5.

**Setup.** Official engine and runner (`SubprocessBot`), seeds 0–9, WSL Python 3.14.4 (server: 3.12.14). "Y" in a run name = the first agent plays Y. The stand in opponent ("6-flag K", called `main_cap6.py` at the time) is **v3's code**; it approximates the public losers' 6–8 flags and high warrior count and is **not a real team**.
The candidate files `main_v2.py`, `main_cap4.py`, `main_cap5.py`, `main_cap6.py`, `main_cap8.py` were temporary copies of v2's `main.py` with `12` replaced by N (`cap6` = v3, byte identical) and are no longer in the kit directory; recreate them below.
All runs: 0 forfeits.

| run (folder) | candidate vs opponent | W · D · L | mean final score | mean buildings·value at turn 20 → end | max turn ms (WSL) |
| --- | --- | ---: | ---: | --- | ---: |
| `v2-vs-cap6-Y` | v2 vs 6-flag | 2·0·8 | 11.2 | 7.6·172 → 5.2·123.1 | 143.7 |
| `cap6-vs-cap6-Y` | 6-flag vs 6-flag (mirror) | 4·0·6 | 19.8 | 7.4·195.5 → 9.1·474.7 | 340.5 |
| `cap6-vs-v2-Y` | 6-flag vs v2 | 9·0·1 | 25.9 | 6.4·204.3 → 11.7·793.0 | 146.2 |
| `cap6-vs-lv2-Y` / `cap6-vs-lv2-K` | 6-flag vs official Lv2 (Y / K side) | 10·0·0 / 10·0·0 | 34.5 / 34.3 | 11.0·261.0 → 15.2·497.3 / 12.0·265.2 → 15.2·660.3 | 179.0 / 942.6 |
| `cap4-vs-cap6-Y` | 4-flag vs 6-flag | 6·0·4 | 19.9 | 7.2·211 → 9.2·682.4 | 903.4 |
| `cap4-vs-v2-Y` | 4-flag vs v2 | 7·0·3 | 22.3 | 6.3·213.5 → 10·1014.9 | 195.1 |
| `cap5-vs-cap6-Y` | 5-flag vs 6-flag | 3·0·7 | 14.9 | 8.4·201.3 → 7.2·517.4 | 1309.3 |
| `cap8-vs-cap6-Y` | 8-flag vs 6-flag | 4·0·6 | 16.0 | 8.0·195.3 → 7.4·330.1 | 512.9 |

Same seed comparison: v2 → 6-flag against the 6-flag stand in is +2 wins, +8.6 mean score, +3.9 final buildings (and 9–1 against v2 itself). Caps 4, 5 and 8 were **rejected**:
cap 4 beat the stand in 6–4 but only 7–3 against v2 (6-flag: 9–1) and turned v2's seed 4 win into a loss; cap 5 3–7 (seeds 0 and 4 turned from v2 wins into losses); cap 8 4–6 (seed 0). Those regression replays are kept in [`failures/`](failures/)
(`v2-vs-cap6-Y_seed-0/4` are the v2 wins, the others the regressions). Some WSL turns exceeded 300 ms without a forfeit (first turn budget is 3 s); server timing was checked separately by the site's practice battle.

Each run folder holds `summary.json` (per seed results), `metrics.txt` (`local_metrics.py` output, kept because the per seed replays are git ignored) and, locally, `replays/seed-N.json` (**git ignored**, regenerable).

## Regenerate (verified in the cleanup)

```sh
# 1) variants: v2 with the cap replaced (helpers copied next to main.py)
python - <<'EOF'
import pathlib, shutil
for n in (4, 5, 6, 8):
    d = pathlib.Path(f"out/experiments/local-runs/variants/cap{n}")
    shutil.copytree("out/v1-v2-codex/source", d, dirs_exist_ok=True)
    m = d / "main.py"
    m.write_bytes(m.read_bytes().replace(b"min(12, len(targets) + 2)", f"min({n}, len(targets) + 2)".encode()))   # bytes: keeps LF endings, so cap6 == v3 exactly
EOF
# 2) runs (WSL, repository root; ~1-2 minutes each)
python3 out/tools/evaluation/subprocess_eval.py out/v1-v2-codex/source/main.py out/v3-codex/source/main.py --side Y --seeds 10 --name v2-vs-cap6-Y
python3 out/tools/evaluation/subprocess_eval.py out/experiments/local-runs/variants/cap4/main.py out/v3-codex/source/main.py --side Y --seeds 10 --name cap4-vs-cap6-Y
python3 out/tools/evaluation/subprocess_eval.py out/v3-codex/source/main.py bots/dist/starter/python/example_lv2.py --side K --seeds 10 --name cap6-vs-lv2-K
python out/tools/reporting/local_metrics.py out/experiments/local-runs/v2-vs-cap6-Y
```

(`subprocess_eval.py` writes to `out/experiments/local-runs/<name>/` by default — git ignored scratch; pass `--outdir` to write elsewhere.) Re-running `v2-vs-cap6-Y` in WSL gave results identical to the stored run for 10 of 10 seeds and per turn game states identical for 10 of 10 (only the wall clock field differs).
