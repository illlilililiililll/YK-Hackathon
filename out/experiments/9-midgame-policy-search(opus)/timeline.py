"""Early expansion and timing check: mean buildings / true score / W of the candidate side at T10, T20, T40 (both sides shown
as cand:opp), and when lost games were decided (T11-140 vs the last 20 turns), per candidate.

  python "out/experiments/9-midgame-policy-search(opus)/timeline.py" <results.jsonl ...> [--cands base,nofar] [--opps ...]
"""
import argparse, json, sys
from collections import defaultdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--cands", default=None)
    ap.add_argument("--opps", default=None)
    a = ap.parse_args()
    g = defaultdict(list)
    for f in a.files:
        for r in map(json.loads, open(f, encoding="utf-8")):
            if (a.cands and r["cand"] not in a.cands.split(",")) or (a.opps and r["opp"] not in a.opps.split(",")):
                continue
            g[r["cand"]].append(r)
    for c, rs in sorted(g.items()):
        parts = []
        for t in ("10", "20", "40"):
            xs = [(r["timeline"][t], r["side"]) for r in rs if t in r["timeline"]]
            m = lambda k, own: sum(x[k][s if own else ("K" if s == "Y" else "Y")] for x, s in xs) / len(xs)
            parts.append(f"T{t} bld {m('nb', 1):4.1f}:{m('nb', 0):4.1f} score {m('score', 1):4.1f}:{m('score', 0):4.1f}")
        lost = [r for r in rs if r["outcome"] == "L"]
        dec = [r["mid"][r["side"]]["decisive"] for r in lost]
        mid = sum(d is not None and d <= 140 for d in dec)
        print(f"{c:<8} n {len(rs):4d}  " + "  ".join(parts) + f"  | losses {len(lost)}: decided T11-140 {mid}, after T140 {len(lost) - mid}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
