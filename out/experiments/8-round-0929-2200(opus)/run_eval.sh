#!/bin/bash
# Local evaluation of experiment 8 (run from the repository root, in WSL):
#   bash "out/experiments/8-round-0929-2200(opus)/run_eval.sh" design     # seeds 4000-4049, Y
#   bash "out/experiments/8-round-0929-2200(opus)/run_eval.sh" holdout    # seeds 4500-4599, Y (after the choice is fixed)
#   bash "out/experiments/8-round-0929-2200(opus)/run_eval.sh" kside      # seeds 4500-4529, K
# Extra args are passed to eval_matches.py (e.g. --resume). Results: out/experiments/8-round-0929-2200(opus)/<tag>/results.jsonl
set -e
X='out/experiments/8-round-0929-2200(opus)'
# candidate sources must live outside out/experiments (wsl_run.sh does not mirror that folder to WSL)
C="python3 out/v0-unsubmitted/v6-variants-opus/source/main.py"
I="python3 out/v0-unsubmitted/indep-v0-claude/source/main.py"
stage="$1"; shift
case "$stage" in
  design)  SEEDS=4000-4049; SIDES=Y; TAG=design ;;
  design2) SEEDS=4000-4049; SIDES=Y; TAG=design2 ;;    # post hoc second round (added after reading "design")
  holdout) SEEDS=4500-4599; SIDES=Y; TAG=holdout ;;
  kside)   SEEDS=4500-4529; SIDES=K; TAG=kside ;;
  bake)    # baked source (no env var) vs the tested env-var variant: every game must be an identical draw
    OUTDIR="$X" bash out/tools/evaluation/wsl_run.sh --tag bake-check --seeds 4600-4619 --sides Y,K --jobs 8 --save-replays lost \
      --cand eg20baked="python3 out/v0-unsubmitted/v6-endgame20-frozen-opus/source/main.py" \
      --opp eg20env="INDEP_PARAMS=endgame=20 $C" "$@"; exit ;;
  win312)  # separate process under the Windows Python 3.12.7 interpreter (closest to the server's 3.12.14), one game at a time
    OUTDIR="$X" bash out/tools/evaluation/wsl_run.sh --tag win312 --seeds 4600-4605 --sides Y --jobs 1 --save-replays none \
      --cand eg20win="'/mnt/c/Program Files/Python312/python.exe' out/v0-unsubmitted/v6-endgame20-frozen-opus/source/main.py" \
      --opp v6="python3 out/v6-claude/source/main.py" \
      --opp pressure="INDEP_PARAMS=fcap_early=6,fcap_late=5,garrison=0,hunt_r=6,hospital_spawn=1 $I" "$@"; exit ;;
  serial)  # timing gate: one game at a time
    OUTDIR="$X" bash out/tools/evaluation/wsl_run.sh --tag serial --seeds 4600-4605 --sides Y --jobs 1 --save-replays none \
      --cand eg20baked="python3 out/v0-unsubmitted/v6-endgame20-frozen-opus/source/main.py" \
      --opp v6="python3 out/v6-claude/source/main.py" \
      --opp pressure="INDEP_PARAMS=fcap_early=6,fcap_late=5,garrison=0,hunt_r=6,hospital_spawn=1 $I" \
      --opp g1e0="python3 out/v4-v5-provenance-uncertain/source/main.py" "$@"; exit ;;
  *) echo "stage?"; exit 2 ;;
esac
CANDS=(--cand base="$C"
       --cand D4="INDEP_PARAMS=defend=1,defend_eta=4 $C"
       --cand EG="INDEP_PARAMS=endgame=12 $C"
       --cand F76="INDEP_PARAMS=fcap_early=7,fcap_late=6 $C"
       --cand D4EG="INDEP_PARAMS=defend=1,defend_eta=4,endgame=12 $C"
       --cand ALL="INDEP_PARAMS=defend=1,defend_eta=4,endgame=12,fcap_early=7,fcap_late=6 $C")
if [ "$stage" = holdout ] || [ "$stage" = kside ]; then   # finalists fixed after design, before any held-out game
  CANDS=(--cand base="$C" --cand EG="INDEP_PARAMS=endgame=12 $C" --cand EG20="INDEP_PARAMS=endgame=20 $C")
fi
if [ "$stage" = design2 ]; then
  CANDS=(--cand G0="INDEP_PARAMS=garrison=0 $C"
         --cand G0EG="INDEP_PARAMS=garrison=0,endgame=12 $C"
         --cand F76EG="INDEP_PARAMS=fcap_early=7,fcap_late=6,endgame=12 $C"
         --cand G0F76EG="INDEP_PARAMS=garrison=0,fcap_early=7,fcap_late=6,endgame=12 $C"
         --cand EG20="INDEP_PARAMS=endgame=20 $C")
fi
OPPS=(--opp v6="python3 out/v6-claude/source/main.py"
      --opp front="INDEP_PARAMS=fcap_early=6,fcap_late=6,garrison=1,garrison_alert=7,hunt_r=6,hospital_spawn=1 $I"
      --opp pressure="INDEP_PARAMS=fcap_early=6,fcap_late=5,garrison=0,hunt_r=6,hospital_spawn=1 $I"
      --opp escort="python3 out/opponents/escort/main.py"
      --opp g1e0="python3 out/v4-v5-provenance-uncertain/source/main.py"
      --opp indepv0="$I")
case " $* " in *" --resume "*) ;; *) rm -rf "$HOME/ykrun/$X/$TAG" ;; esac   # fresh run: drop stale mirror rows
if [ "$stage" != design ]; then
  OPPS+=(--opp cap7="python3 out/v0-unsubmitted/cap7-codex/source/main.py" --opp v3="python3 out/v3-codex/source/main.py")
fi
OUTDIR="$X" bash out/tools/evaluation/wsl_run.sh --tag "$TAG" --seeds "$SEEDS" --sides "$SIDES" --jobs 8 --save-replays lost \
  "${CANDS[@]}" "${OPPS[@]}" "$@"
