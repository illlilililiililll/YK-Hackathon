"""Head-to-head summary: each candidate (as Y) vs one opponent, with Wilson intervals and a K/Y mirror check.

  python out/tools/reporting/h2h.py out/experiments/7-independent-agent(v6)/phase3-selection/p3-select-h2h/results.jsonl [--opp base]

Deterministic agents on the point-symmetric map play the mirrored game when sides swap, so the K-side games only
confirm symmetry; statistics use the Y-side games (n = number of seeds).
"""
import argparse, json, math, sys
from collections import Counter, defaultdict


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--opp", default=None)
    a = ap.parse_args()
    rows = []
    for f in a.files:
        rows += [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    if a.opp:
        rows = [r for r in rows if r["opp"] == a.opp]
    y = defaultdict(Counter)
    ys = {}
    for r in rows:
        if r["side"] == "Y":
            y[(r["cand"], r["opp"])][r["outcome"]] += 1
            ys[(r["cand"], r["opp"], r["seed"])] = r["outcome"]
    mis = sum(1 for r in rows if r["side"] == "K" and (r["cand"], r["opp"], r["seed"]) in ys
              and ys[(r["cand"], r["opp"], r["seed"])] != r["outcome"])
    print(f"{len(rows)} games; K-side outcome differs from Y-side outcome on {mis} seeds")
    for (c, o), v in sorted(y.items()):
        n = sum(v.values())
        lo, hi = wilson(v["W"], n)
        print(f"  {c:<10} vs {o:<8} {v['W']}-{v['D']}-{v['L']}  win {100*v['W']/n:.0f}%  CI[{100*lo:.0f},{100*hi:.0f}]  n={n}")


if __name__ == "__main__":
    main()
