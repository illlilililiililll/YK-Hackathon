# `out/` — agents, evidence and experiments of this project

Everything the team produced lives here; the official game kit is outside (`bots/`, `engine/`, `runner/`, `mapgen/`, `config/`, `docs/`).

```
out/
  README.md  DEVELOPMENT_LOG.md  OFFICIAL_MATCH_ANALYSIS.md  PROMPT_RECORD.md  PATH_MAP.md  path_map.tsv
  v1-v2-codex/  v3-codex/  v6-claude/       submitted versions: v<N>.zip + source + README
  v4-v5-provenance-uncertain/               two received look alike sources, each with a valid submission package; NOT proven to be the site's v4 or v5
  v0-unsubmitted/cap7-codex/  v0-unsubmitted/indep-v0-claude/   local only candidates (never uploaded)
  v0-unsubmitted/v6-endgame20-opus/         best local candidate (lineage: v6-endgame20 + no far hunting, 09-30)
  v0-unsubmitted/v6-endgame20-frozen-opus/  v6-endgame20 as of experiment 8, frozen (baseline of experiment 9)
  v0-unsubmitted/v6-variants-opus/  v0-unsubmitted/v6-endgame20-switches-opus/   switchable sources of experiments 8 and 9 (source only)
  official-replays/       the 71 public official replay originals + per match summaries
  opponents/              fixed local opponents (rush, turtle, raider, pack, escort)
  tools/evaluation/  tools/reporting/       shared evaluation and report building tools
  experiments/            1 … 9, local runs and their reports in chronological order, model in parentheses
```

Folder names are `v<N>-<model>`: `<N>` is the **site submission number**, `<model>` is the AI that developed the strategy (`codex` = Codex, GPT-6 family; `claude` = Claude Sonnet 5.5; `opus` = Claude Opus 5.5).
`v1-v2-codex` holds the one strategy that was submitted twice. In the submitted folders the ZIP has a simple name (`v2.zip`, `v3.zip`, `v6.zip`); the file name that was uploaded and the submission ID are in each README, and the entry names inside the ZIPs (`main.py`, `submission.json`, …) are unchanged.
`v0-unsubmitted` holds candidates that never had a site version.

## Which version is what

| version | strategy by | in this repo | site status | note |
| --- | --- | --- | --- | --- |
| **v1** | Codex | [`v1-v2-codex/`](v1-v2-codex/) (manifest only; the ZIP is rebuilt bit for bit) | rejected `EXECUTABLE_FILE` | ZIP entries had execute bits; same `main.py` as v2 |
| **v2** | Codex | [`v1-v2-codex/`](v1-v2-codex/) | usable; practice 10–0–0; official team matches 4W–15L | first accepted; flag cap 12 |
| **v3** | Codex | [`v3-codex/`](v3-codex/) | usable; practice 10–0–0; official team matches 8W–20L | v2 with flag cap 6; source also at `bots/dist/starter/python/main.py` |
| **v4** | unknown | **absent**; possible look alike in [`v4-v5-provenance-uncertain/`](v4-v5-provenance-uncertain/) | `y-agent-v4.zip`, 11.6 KiB, `수정 필요` ("파일 구성을 확인해 주세요.", processed 09-29 13:22) | source not recorded |
| **v5** | unknown | **absent**; possible look alike in [`v4-v5-provenance-uncertain/`](v4-v5-provenance-uncertain/) | `v-agent-v4.zip`, 11.2 KiB, usable; **selected for the competition**; processed 09-29 13:25, ID `01a0eb68-e2a0-7200-b852-6f81f2906061`; practice 10–0–0 at 13:27 | source not recorded: **do not treat v6 or any local candidate as v5** |
| **v6** | Claude | [`v6-claude/`](v6-claude/) — **the submitted `indep1`** | usable; practice 10–0–0; not selected at the last recorded check (09-29 15:41); **its code played the 9/29 22:00 and 9/30 10:00 rounds**, 4W–8L and 6W–6L (proven by command replay, [`OFFICIAL_MATCH_ANALYSIS.md`](OFFICIAL_MATCH_ANALYSIS.md) §9–§10; the site selection behind it was not checked) | ZIP and source in one folder |
| — | Codex | [`v0-unsubmitted/cap7-codex/`](v0-unsubmitted/cap7-codex/) | never uploaded | best local Codex candidate |
| — | Claude | [`v0-unsubmitted/indep-v0-claude/`](v0-unsubmitted/indep-v0-claude/) | never uploaded | blind baseline; its ZIP has execute bits, do not upload |
| — | Claude Opus | [`v0-unsubmitted/v6-endgame20-opus/`](v0-unsubmitted/v6-endgame20-opus/) | never uploaded | v6-endgame20 + no far hunting (one line); best verified **local** candidate (experiment 9: 82% vs 73% of paired points over six challenging opponents, both sides, untouched seeds); checked ZIP `v6-endgame20-nofar.zip` |
| — | Claude Opus | [`v0-unsubmitted/v6-endgame20-frozen-opus/`](v0-unsubmitted/v6-endgame20-frozen-opus/) | never uploaded | v6 + endgame rule (one line), as adopted in experiment 8 (held out: 56–44 vs v6); checked ZIP `v6-endgame20.zip`; frozen baseline of experiment 9 |
| — | Claude Opus | [`v0-unsubmitted/v6-variants-opus/`](v0-unsubmitted/v6-variants-opus/) | never uploaded | source only: v6 with switchable rules (`defend`, `endgame`); defaults = v6 exactly; used for experiment 8 |
| — | Claude Opus | [`v0-unsubmitted/v6-endgame20-switches-opus/`](v0-unsubmitted/v6-endgame20-switches-opus/) | never uploaded | source only: v6-endgame20 with the experiment 9 switches (`hold`, `hfar_*`, `hub`); defaults = v6-endgame20 exactly |

## Integrity

`python out/tools/evaluation/verify_artifacts.py` compares the entries of every stored ZIP with its `source/` folder, checks the file modes and rebuilds the rejected v1 ZIP from its manifest. The v6 source and ZIP are byte identical to what they were before both cleanups. Old names and paths: [`PATH_MAP.md`](PATH_MAP.md).

## Documents

| file | content |
| --- | --- |
| [`DEVELOPMENT_LOG.md`](DEVELOPMENT_LOG.md) | concise chronology: designs, decisive tests, rejected ideas, official submissions and results |
| [`OFFICIAL_MATCH_ANALYSIS.md`](OFFICIAL_MATCH_ANALYSIS.md) | all 71 public official matches: IDs, version attribution, observations, uncertainty, links to the replay originals |
| [`PROMPT_RECORD.md`](PROMPT_RECORD.md) | models, verbatim prompts, purpose and scope of AI use (for the competition report) |
| [`experiments/README.md`](experiments/README.md), [`tools/README.md`](tools/README.md) | experiment index with regeneration commands; tool index |

## Verify

```sh
python out/tools/evaluation/verify_artifacts.py      # ZIP entries == source, execute bit expectations, v1 rebuilt from its manifest
python out/tools/reporting/check_links.py            # Markdown links, out/... paths and documented script names
wsl --cd <repo> python3 bots/dist/starter/run_tests.py --zip out/v6-claude/v6.zip --seed 52   # official ZIP checker
```

Build any new submission ZIP with **Windows Python** (the official `make_submission.py`) and check it with `tools/evaluation/zip_modes.py`; a ZIP built under WSL gets execute bits and the server rejects it.

## What is not in Git

Reproducible local output is ignored (see the root `.gitignore`): per game replays under `experiments/**/replays/` (Codex runs: `seed-N.json`; Claude runs: `*.json.gz` of lost games), the scratch folders `experiments/local-runs/` and `_scratch*/`, Python caches, and top level scratch ZIPs.
Their summaries, the scripts and the commands to regenerate them (per experiment README) are tracked, as are the selected failure cases (`failures/` and `cases/` folders) and the official replay originals.
