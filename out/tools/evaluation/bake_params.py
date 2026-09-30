"""Bake INDEP_PARAMS-style overrides into a copy of out/v0-unsubmitted/indep-v0-claude/source (so the shipped source needs no environment variable).

  python out/tools/evaluation/bake_params.py --src out/v0-unsubmitted/indep-v0-claude/source --dst <new dir> --params fcap_early=6,fcap_late=5,garrison=1
Only the defaults inside `P = dict(...)` of brain.py are rewritten; every other file is copied byte-for-byte.
Verify afterwards with an indep1-vs-(env-var variant) mirror match: every game must be a draw with identical scores.
"""
import argparse, re, shutil, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True); ap.add_argument("--dst", required=True); ap.add_argument("--params", required=True)
a = ap.parse_args()
src, dst = Path(a.src), Path(a.dst)
if dst.exists():
    sys.exit(f"{dst} exists; refusing to overwrite")
shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.md"))
brain = (dst / "brain.py").read_text(encoding="utf-8")
# the whole `P = dict(...)` block: from its first line to the blank line after it (comments may contain parentheses)
m = re.search(r"^P = dict\(.*?\n\n", brain, re.S | re.M)
block = m.group(0)
new = block
for kv in a.params.split(","):
    k, v = kv.split("=")
    new, n = re.subn(rf"\b{k}=-?\d+(?:\.\d+)?", f"{k}={v}", new, count=1)
    if n != 1:
        sys.exit(f"parameter {k} not found in P")
(dst / "brain.py").write_text(brain.replace(block, new), encoding="utf-8")
print("baked:", a.params)
print(new)
