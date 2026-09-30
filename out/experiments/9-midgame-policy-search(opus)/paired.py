"""Paired candidate-vs-baseline table (PLAN.md reward): points W=1, D=0.5, L=0 on identical (opponent, seed, side).

  python "out/experiments/9-midgame-policy-search(opus)/paired.py" <results.jsonl ...> [--base base] [--pool F76,G0,D4,pressure]

Per candidate: points per opponent (delta vs base), over the pool: +better/-worse games (discordant pairs) and the exact
one-sided sign test p = P(X >= better | n = discordant, 1/2); midgame diagnostics of the candidate's side (means over all games
in the pool, `midgame_metrics.py`): own flips T11-140, lost score-turns, score-turn and HALL+ENG-turn differences; forfeits; max ms.
"""
import argparse, json, sys
from collections import defaultdict
from math import comb

PTS = {"W": 1.0, "D": 0.5, "L": 0.0}


def sign_p(k, n):
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--base", default="base")
    ap.add_argument("--pool", default="F76,G0,D4,pressure")
    ap.add_argument("--sides", default=None, help="restrict to these sides, e.g. Y")
    a = ap.parse_args()
    pool = a.pool.split(",")
    R = {}
    for f in a.files:
        for r in map(json.loads, open(f, encoding="utf-8")):
            if a.sides and r["side"] not in a.sides.split(","):
                continue
            R[(r["cand"], r["opp"], r["seed"], r["side"])] = r
    cands = sorted({k[0] for k in R}, key=lambda c: (c != a.base, c))
    opps = sorted({k[1] for k in R}, key=lambda o: (o not in pool, o))
    print(f"{'cand':<8}" + "".join(f"{o:>13}" for o in opps) + f"   pool: pts  +/-   p(sign)   flips lost_st  st_diff prod_diff  ff maxms")
    for c in cands:
        cells, better, worse, tot, diag, ff, mx = [], 0, 0, 0.0, defaultdict(float), 0, 0.0
        n_pool = 0
        for o in opps:
            keys = [k for k in R if k[0] == c and k[1] == o]
            pts = sum(PTS[R[k]["outcome"]] for k in keys)
            bpts = sum(PTS[R[(a.base,) + k[1:]]["outcome"]] for k in keys if (a.base,) + k[1:] in R)
            cells.append(f"{pts:>6.1f}" + (f" ({pts - bpts:+.0f})" if c != a.base else "      "))
            for k in keys:
                r = R[k]
                ff += bool(r["forfeit"])
                mx = max(mx, r["cand_max_ms"])
                if o not in pool:
                    continue
                n_pool += 1
                tot += PTS[r["outcome"]]
                b = R.get((a.base,) + k[1:])
                if b:
                    d = PTS[r["outcome"]] - PTS[b["outcome"]]
                    better += d > 0
                    worse += d < 0
                s, e = r["side"], ("K" if r["side"] == "Y" else "Y")
                m = r["mid"]
                diag["flips"] += m[s]["flips"]
                diag["lost"] += m[s]["lost_st"]
                diag["st"] += m[s]["score_turns"] - m[e]["score_turns"]
                diag["prod"] += m[s]["hall_t"] + m[s]["eng_t"] - m[e]["hall_t"] - m[e]["eng_t"]
        n = n_pool or 1
        p = sign_p(better, better + worse) if c != a.base else float("nan")
        print(f"{c:<8}" + "".join(f"{x:>13}" for x in cells) +
              f"   {tot:6.1f} +{better}/-{worse}  {p:7.3f}  {diag['flips'] / n:6.1f} {diag['lost'] / n:7.0f} {diag['st'] / n:8.0f} {diag['prod'] / n:9.1f} {ff:3d} {mx:5.0f}")


if __name__ == "__main__":
    main()
