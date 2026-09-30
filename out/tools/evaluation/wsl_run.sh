#!/bin/bash
# Run eval_matches.py from WSL's native ext4 (~/ykrun) instead of the slow, noisy /mnt/c mount, then copy
# results back into <repo>/$OUTDIR (default out/experiments/local-runs; also every 30 s while running, so a
# killed run loses nothing; use --resume).
# Run from the repo root:
#   wsl --cd <repo> bash out/tools/evaluation/wsl_run.sh --tag t --cand a="python3 ..." --opp b="..." [--resume] ...
# Commands passed to --cand/--opp are relative to the repo root (they run from ~/ykrun, a mirror of it).
# To write elsewhere: OUTDIR=out/experiments/<dir> bash out/tools/evaluation/wsl_run.sh ...  (the script passes --outdir).
set -e
SRC="$(pwd)"
DST="${YKRUN:-$HOME/ykrun}"      # YKRUN=~/ykrun-<job>: a separate mirror, so parallel jobs do not clobber each other
OUTDIR="${OUTDIR:-out/experiments/local-runs}"
mkdir -p "$DST" "$DST/$OUTDIR" "$SRC/$OUTDIR"
rsync -a --delete --exclude '.git' --exclude '.claude' --exclude '__pycache__' --exclude '/out/experiments' --exclude '/out/official-replays' "$SRC/" "$DST/"
cd "$DST"
( while true; do sleep 30; rsync -a "$DST/$OUTDIR/" "$SRC/$OUTDIR/" 2>/dev/null || true; done ) &
SYNCER=$!
trap 'kill $SYNCER 2>/dev/null; rsync -a "$DST/$OUTDIR/" "$SRC/$OUTDIR/" 2>/dev/null || true' EXIT
rc=0
python3 out/tools/evaluation/eval_matches.py --outdir "$OUTDIR" "$@" || rc=$?
exit $rc
