#!/bin/bash
# Local evaluation of experiment 9 (run from the repository root, in WSL):
#   wsl --cd <repo> --exec bash "out/experiments/9-midgame-policy-search(opus)/run.sh" <stage> [eval_matches args]
# Results: out/experiments/9-midgame-policy-search(opus)/<tag>/results.jsonl. Stages are added in the order they were run;
# PLAN.md fixes seeds, opponents and the decision rule before any candidate stage.
set -e
X='out/experiments/9-midgame-policy-search(opus)'
export YKRUN="$HOME/ykrun-midgame"          # own mirror: never clobbers another job's ~/ykrun
B="python3 out/v0-unsubmitted/v6-endgame20-frozen-opus/source/main.py"      # frozen baseline
# search source with the experiment 9 switches (defaults = baseline). The search and refine stages ran it from
# out/v0-unsubmitted/v6-endgame20-opus/source/; it was moved here unchanged when the finalist was baked into that folder.
C="python3 out/v0-unsubmitted/v6-endgame20-switches-opus/source/main.py"
N="python3 out/v0-unsubmitted/v6-endgame20-opus/source/main.py"             # finalist: frozen baseline + hunt_r=1 (bake_params.py)
I="python3 out/v0-unsubmitted/indep-v0-claude/source/main.py"
V="python3 out/v0-unsubmitted/v6-variants-opus/source/main.py"
FRONT="INDEP_PARAMS=fcap_early=6,fcap_late=6,garrison=1,garrison_alert=7,hunt_r=6,hospital_spawn=1 $I"
PRESSURE="INDEP_PARAMS=fcap_early=6,fcap_late=5,garrison=0,hunt_r=6,hospital_spawn=1 $I"
stage="$1"; shift
run() { OUTDIR="$X" bash out/tools/evaluation/wsl_run.sh "$@"; }
case "$stage" in
  repro)   # step 1: the frozen baseline must reproduce the recorded experiment-8 held-out rows game for game
    run --tag repro --seeds 4500-4549 --sides Y --jobs 14 --save-replays none \
      --cand EG20="$B" --opp front="$FRONT" --opp pressure="$PRESSURE" "$@" ;;
  screen)  # step 3: which opponents challenge the frozen baseline, and do its losses look like the official ones? (seeds 7000-7049)
    run --tag screen --seeds 7000-7049 --sides Y --jobs 14 --save-replays lost --cand EG20="$B" \
      --opp v6="python3 out/v6-claude/source/main.py" --opp front="$FRONT" --opp pressure="$PRESSURE" \
      --opp escort="python3 out/opponents/escort/main.py" --opp g1e0="python3 out/v4-v5-provenance-uncertain/source/main.py" \
      --opp indepv0="$I" --opp cap7="python3 out/v0-unsubmitted/cap7-codex/source/main.py" --opp v3="python3 out/v3-codex/source/main.py" \
      --opp pack="python3 out/opponents/pack/main.py" --opp raider="python3 out/opponents/raider/main.py" \
      --opp rush="python3 out/opponents/rush/main.py" --opp turtle="python3 out/opponents/turtle/main.py" \
      --opp F76="INDEP_PARAMS=fcap_early=7,fcap_late=6 $V" --opp G0="INDEP_PARAMS=garrison=0 $V" \
      --opp D4="INDEP_PARAMS=defend=1,defend_eta=4 $V" --opp F76G0="INDEP_PARAMS=fcap_early=7,fcap_late=6,garrison=0 $V" "$@" ;;
  search)  # step 5: the 9 planned variants (PLAN.md) + L0 (lineage defaults: must equal the baseline game for game), seeds 5000-5099 Y
    run --tag search --seeds 5000-5099 --sides Y --jobs 14 --save-replays none \
      --cand base="$B" --cand L0="$C" \
      --cand H1a="INDEP_PARAMS=hold=1,hold_src=1 $C" --cand H1b="INDEP_PARAMS=hold=1,hold_src=2 $C" \
      --cand H1c="INDEP_PARAMS=hold=1,hold_src=1,hold_all=1 $C" \
      --cand H2a="INDEP_PARAMS=hfar_mine=1 $C" --cand H2b="INDEP_PARAMS=hfar_keep=1 $C" --cand H2c="INDEP_PARAMS=hunt_r=3 $C" \
      --cand H3a="INDEP_PARAMS=hub=4 $C" --cand H3b="INDEP_PARAMS=hub=6 $C" --cand H3c="INDEP_PARAMS=hub=8 $C" \
      --opp F76="INDEP_PARAMS=fcap_early=7,fcap_late=6 $V" --opp G0="INDEP_PARAMS=garrison=0 $V" \
      --opp D4="INDEP_PARAMS=defend=1,defend_eta=4 $V" --opp pressure="$PRESSURE" \
      --opp v6="python3 out/v6-claude/source/main.py" "$@" ;;
  refine)  # the one refinement round (PLAN.md): only H2 improved the search reward (H2c hunt_r=3: +18, D4 -5); far-hunting range 1/2/4
    run --tag refine --seeds 5000-5099 --sides Y --jobs 14 --save-replays none \
      --cand H2r1="INDEP_PARAMS=hunt_r=1 $C" --cand H2r2="INDEP_PARAMS=hunt_r=2 $C" --cand H2r4="INDEP_PARAMS=hunt_r=4 $C" \
      --opp F76="INDEP_PARAMS=fcap_early=7,fcap_late=6 $V" --opp G0="INDEP_PARAMS=garrison=0 $V" \
      --opp D4="INDEP_PARAMS=defend=1,defend_eta=4 $V" --opp pressure="$PRESSURE" \
      --opp v6="python3 out/v6-claude/source/main.py" "$@" ;;
  bake)    # baked finalist vs the searched env-var variant: every game must be an identical draw
    run --tag bake-check --seeds 4600-4619 --sides Y,K --jobs 14 --save-replays lost \
      --cand nofar="$N" --opp H2r1env="INDEP_PARAMS=hunt_r=1 $C" "$@" ;;
  final)   # untouched final (PLAN.md): 6 challenging opponents (front, F76G0 never used in search) + v6 floor, both sides
    run --tag final --seeds 6000-6199 --sides Y --jobs 14 --save-replays lost --cand base="$B" --cand nofar="$N" \
      --opp F76="INDEP_PARAMS=fcap_early=7,fcap_late=6 $V" --opp G0="INDEP_PARAMS=garrison=0 $V" \
      --opp D4="INDEP_PARAMS=defend=1,defend_eta=4 $V" --opp pressure="$PRESSURE" \
      --opp front="$FRONT" --opp F76G0="INDEP_PARAMS=fcap_early=7,fcap_late=6,garrison=0 $V" \
      --opp v6="python3 out/v6-claude/source/main.py" "$@"
    run --tag final-k --seeds 6000-6099 --sides K --jobs 14 --save-replays lost --cand base="$B" --cand nofar="$N" \
      --opp F76="INDEP_PARAMS=fcap_early=7,fcap_late=6 $V" --opp G0="INDEP_PARAMS=garrison=0 $V" \
      --opp D4="INDEP_PARAMS=defend=1,defend_eta=4 $V" --opp pressure="$PRESSURE" \
      --opp front="$FRONT" --opp F76G0="INDEP_PARAMS=fcap_early=7,fcap_late=6,garrison=0 $V" \
      --opp v6="python3 out/v6-claude/source/main.py" "$@"
    run --tag final-reg --seeds 6000-6099 --sides Y --jobs 14 --save-replays lost --cand base="$B" --cand nofar="$N" \
      --opp escort="python3 out/opponents/escort/main.py" --opp g1e0="python3 out/v4-v5-provenance-uncertain/source/main.py" \
      --opp indepv0="$I" --opp cap7="python3 out/v0-unsubmitted/cap7-codex/source/main.py" --opp v3="python3 out/v3-codex/source/main.py" \
      --opp pack="python3 out/opponents/pack/main.py" --opp raider="python3 out/opponents/raider/main.py" \
      --opp rush="python3 out/opponents/rush/main.py" --opp turtle="python3 out/opponents/turtle/main.py" "$@" ;;
  timing)  # timing gate: one game at a time, WSL Python 3.14 and the Windows Python 3.12.7 interpreter (closest to the server's 3.12)
    run --tag serial --seeds 4600-4605 --sides Y --jobs 1 --save-replays none --cand nofar="$N" \
      --opp v6="python3 out/v6-claude/source/main.py" --opp F76="INDEP_PARAMS=fcap_early=7,fcap_late=6 $V" --opp pressure="$PRESSURE" "$@"
    run --tag win312 --seeds 4600-4605 --sides Y --jobs 1 --save-replays none \
      --cand nofarwin="'/mnt/c/Program Files/Python312/python.exe' out/v0-unsubmitted/v6-endgame20-opus/source/main.py" \
      --opp v6="python3 out/v6-claude/source/main.py" --opp F76="INDEP_PARAMS=fcap_early=7,fcap_late=6 $V" "$@" ;;
  h2h)     # POST HOC (not in PLAN.md, run after the adoption decision): the finalist head to head against its frozen predecessor
    run --tag h2h --seeds 6000-6199 --sides Y --jobs 14 --save-replays none --cand nofar="$N" --opp eg20frozen="$B" "$@"
    run --tag h2h-k --seeds 6000-6099 --sides K --jobs 14 --save-replays none --cand nofar="$N" --opp eg20frozen="$B" "$@" ;;
  *) echo "stage?"; exit 2 ;;
esac
