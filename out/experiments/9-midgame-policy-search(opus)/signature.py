"""Does a local opponent beat us the way real teams did? Midgame signature of official v6 games vs local games.

  python "out/experiments/9-midgame-policy-search(opus)/signature.py" --official out/official-replays/<48-71>_*.json \
      --local "out/experiments/9-midgame-policy-search(opus)/screen/results.jsonl" [--cand EG20]

Per group (official win/loss; local opponent x outcome), means of out/tools/evaluation/midgame_metrics.py for OUR side
(official: Y; local: the candidate's side) and the same quantity for the opponent where useful:
flips / bare% / val / sup1% / sup3% / lost score-turns / score-turn diff / HALL+ENG-turn diff / decisive in T11-140.
"""
import argparse, glob, json, os, sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools", "evaluation"))
from midgame_metrics import load, metrics  # noqa: E402


def row(m, s, e, outcome):
    a, b = m[s], m[e]
    return dict(outcome=outcome, flips=a["flips"], bare=a["flips_bare"], val=a["flips_val"], sup1=a["sup1"], sup3=a["sup3"],
                lost=a["lost_st"], st=a["score_turns"] - b["score_turns"], prod=a["hall_t"] + a["eng_t"] - b["hall_t"] - b["eng_t"],
                mid_dec=a["decisive"] is not None and a["decisive"] <= 140, oflips=b["flips"])


def show(name, rs):
    n = len(rs)
    f = sum(r["flips"] for r in rs) or 1
    mean = lambda k: sum(r[k] for r in rs) / n
    print(f"{name:<22}{n:>4}  flips {mean('flips'):5.1f} (opp {mean('oflips'):5.1f})  bare {sum(r['bare'] for r in rs) / f:4.0%}"
          f"  val {mean('val'):4.1f}  sup1 {sum(r['sup1'] for r in rs) / f:4.0%}  sup3 {sum(r['sup3'] for r in rs) / f:4.0%}"
          f"  lost_st {mean('lost'):6.0f}  st_diff {mean('st'):6.0f}  prod_diff {mean('prod'):6.1f}  decisive<=140 {mean('mid_dec'):4.0%}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--official", nargs="*", default=[])
    ap.add_argument("--local", nargs="*", default=[])
    ap.add_argument("--cand", default=None)
    a = ap.parse_args()
    g = defaultdict(list)
    for p in sorted(x for q in a.official for x in glob.glob(q)):
        rep = load(p)
        out = {"Y": "W", "K": "L", "DRAW": "D"}[rep["result"]["winner"]]
        g[("official", out)].append(row(metrics(rep), "Y", "K", out))
    for p in a.local:
        for r in map(json.loads, open(p, encoding="utf-8")):
            if a.cand and r["cand"] != a.cand:
                continue
            s = r["side"]
            g[(r["opp"], r["outcome"])].append(row(r["mid"], s, "K" if s == "Y" else "Y", r["outcome"]))
    for k in sorted(g, key=lambda k: (k[0] != "official", k)):
        show(f"{k[0]} {k[1]}", g[k])


if __name__ == "__main__":
    main()
