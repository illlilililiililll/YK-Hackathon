"""Mean own/enemy W, F, buildings and score at fixed turns, per candidate and opponent, from eval_matches results.

  python out/tools/reporting/macro.py out/experiments/7-independent-agent(v6)/holdout/hold-rr/results.jsonl --cands indep1,base --opps v3,cap7,v2 [--side Y]
Compare with the official K benchmark (Phase 2): K W 26.6 / 67.0 and F 6.9 / 6.8 at T10 / T20; Y(v2,v3) W 22.7 / 52.8.
"""
import argparse, json, sys

sys.stdout.reconfigure(encoding="utf-8")
ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+"); ap.add_argument("--cands", required=True); ap.add_argument("--opps", required=True)
ap.add_argument("--side", default="Y")
a = ap.parse_args()
rows = []
for f in a.files:
    rows += [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
s, o = a.side, ("K" if a.side == "Y" else "Y")
print(f"{'cand':<8}{'opp':<6}{'T':>3}{'n':>5}   own W   own F  own bld  |  opp W   opp F  opp bld")
for c in a.cands.split(","):
    for op in a.opps.split(","):
        for T in ("10", "20"):
            rs = [r["timeline"][T] for r in rows if r["cand"] == c and r["opp"] == op and r["side"] == s and T in r["timeline"]]
            if not rs:
                continue
            m = lambda f: sum(f(x) for x in rs) / len(rs)
            print(f"{c:<8}{op:<6}{T:>3}{len(rs):>5}  {m(lambda x: x['units'][s]['W']):>6.1f} {m(lambda x: x['units'][s]['F']):>7.1f} {m(lambda x: x['nb'][s]):>8.1f}  |"
                  f" {m(lambda x: x['units'][o]['W']):>6.1f} {m(lambda x: x['units'][o]['F']):>7.1f} {m(lambda x: x['nb'][o]):>8.1f}")
