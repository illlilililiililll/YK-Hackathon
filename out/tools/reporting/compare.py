"""Paired comparison of candidates against a baseline from eval_matches results (same seeds/opponents/side).

  python out/tools/reporting/compare.py out/experiments/7-independent-agent(v6)/phase3-selection/p3-design-A/results.jsonl [more.jsonl ...] --base base [--side Y]

Per candidate x opponent: W-D-L, Wilson 95% interval of the win rate, mean margin/occupation diff, max turn ms.
Paired vs base: seeds where the candidate turned a non-win into a win (+) or a win into a non-win (-), and an exact two-sided
McNemar (sign-test) p-value on those discordant pairs. Small counts are flagged: <=2 net games = inconclusive.
"""
import argparse, json, math, sys
from collections import defaultdict


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def mcnemar_p(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--base", required=True)
    ap.add_argument("--side", default="Y")
    ap.add_argument("--opps", default=None, help="comma list to restrict opponents")
    a = ap.parse_args()
    rows = []
    for f in a.files:
        rows += [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if r["side"] == a.side]
    if a.opps:
        keep = set(a.opps.split(","))
        rows = [r for r in rows if r["opp"] in keep]
    by = defaultdict(dict)                                   # (cand, opp) -> seed -> row
    for r in rows:
        by[(r["cand"], r["opp"])][r["seed"]] = r
    cands = sorted({c for c, _ in by}, key=lambda c: (c != a.base, c))
    opps = sorted({o for _, o in by})
    o_ = "K" if a.side == "Y" else "Y"
    print(f"{'cand':<12}{'opp':<8}{'n':>4} {'W-D-L':>9} {'win%':>6} {'95% CI':>12} {'margin':>7} {'occ':>6} {'ff':>3} {'maxms':>6}   paired vs {a.base}: +gain -loss net  p")
    tot = defaultdict(lambda: [0, 0, 0, 0, 0])
    for c in cands:
        for o in opps:
            rs = by.get((c, o))
            if not rs:
                continue
            n = len(rs)
            w = sum(r["outcome"] == "W" for r in rs.values()); d = sum(r["outcome"] == "D" for r in rs.values()); l = n - w - d
            lo, hi = wilson(w, n)
            mar = sum(r["margin"] for r in rs.values()) / n
            occ = sum(r["final"]["occ"][a.side] - r["final"]["occ"][o_] for r in rs.values()) / n
            ff = sum(1 for r in rs.values() if r["forfeit"])
            mx = max(r["cand_max_ms"] for r in rs.values())
            pair = ""
            if c != a.base and (a.base, o) in by:
                base = by[(a.base, o)]
                common = sorted(set(base) & set(rs))
                g = sum(1 for s in common if base[s]["outcome"] != "W" and rs[s]["outcome"] == "W")
                ls = sum(1 for s in common if base[s]["outcome"] == "W" and rs[s]["outcome"] != "W")
                pair = f"   +{g:<3} -{ls:<3} {g-ls:+d}  p={mcnemar_p(g, ls):.2f}{'  (inconclusive)' if abs(g-ls) <= 2 else ''}"
                tot[c][3] += g; tot[c][4] += ls
            print(f"{c:<12}{o:<8}{n:>4} {f'{w}-{d}-{l}':>9} {100*w/n:>6.1f} {f'{100*lo:.0f}-{100*hi:.0f}':>12} {mar:>7.1f} {occ:>6.0f} {ff:>3} {mx:>6.0f}{pair}")
            tot[c][0] += n; tot[c][1] += w; tot[c][2] += ff
    print("\nTOTAL over listed opponents:")
    for c in cands:
        n, w, ff, g, ls = tot[c]
        lo, hi = wilson(w, n)
        extra = f"  paired vs {a.base}: +{g} -{ls} net {g-ls:+d} p={mcnemar_p(g, ls):.2f}" if c != a.base else ""
        print(f"  {c:<12} {w}/{n} wins ({100*w/n:.1f}%, CI {100*lo:.0f}-{100*hi:.0f}) forfeits {ff}{extra}")


if __name__ == "__main__":
    main()
