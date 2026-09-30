"""For each Y building neutralized by a K flag in the official replays: was Y able to defend it?

Reads raw replay JSON only. For loss turn t at building b (K flag present at b after turn t), reports the
Y warriors near b at the START of turn t (= observation of turn t-1: where units stood before that turn's
moves) and K's escort at b, aggregated by version (v2/v3 by peak-F signature) and by region.
"""
import glob, json, os, sys
from collections import defaultdict


def man(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def main(d):
    sys.stdout.reconfigure(encoding="utf-8")
    agg = defaultdict(list)
    # games 01-47 only (v2/v3, version by peak flags); games 48+ (v6) are analysed in experiment 8
    for f in sorted(f for f in glob.glob(os.path.join(d, "[0-9][0-9]_*.json")) if int(os.path.basename(f)[:2]) <= 47):
        g = json.load(open(f, encoding="utf-8"))
        T = g["turns"]
        obs = [t["observation"] for t in T]
        fpeak = max(sum(u[4] for u in o["units"] if u[0] == "Y" and u[1] == "F") for o in obs[:16])
        ver = "v2" if fpeak >= 8 else "v3"
        won = g["result"]["winner"] == "Y"
        for t in range(2, len(T)):
            p, o = obs[t - 1], obs[t]
            pb = {b["id"]: b for b in p["buildings"]}
            for b in o["buildings"]:
                if pb[b["id"]]["owner"] == "Y" and b["owner"] != "Y":
                    pos = (b["x"], b["y"])
                    kinds = {e["kind"] for e in o["events"] if e.get("buildingId") == b["id"]}
                    kf = sum(u[4] for u in o["units"] if u[0] == "K" and u[1] == "F" and (u[2], u[3]) == pos)
                    kw_at = sum(u[4] for u in o["units"] if u[0] == "K" and u[1] == "W" and (u[2], u[3]) == pos)
                    yw = [(man((u[2], u[3]), pos), u[4]) for u in p["units"] if u[0] == "Y" and u[1] == "W"]
                    yw_near = min((dd for dd, _ in yw), default=99)
                    yw3 = sum(n for dd, n in yw if dd <= 3)
                    yw1 = sum(n for dd, n in yw if dd <= 1)
                    yf_here = sum(u[4] for u in p["units"] if u[0] == "Y" and u[1] == "F" and (u[2], u[3]) == pos)
                    region = "home(x<=4)" if b["x"] <= 4 else "center" if b["x"] <= 9 else "K-home"
                    cause = "pulled" if "pulled" in kinds else "neutral" if "neutral" in kinds else "other"
                    agg[(ver, "win" if won else "loss")].append(
                        dict(t=t, region=region, cause=cause, yw_near=yw_near, yw3=yw3, yw1=yw1, kw_at=kw_at, kf=kf,
                             yf_here=yf_here, type=b["type"]))
    for k, rs in sorted(agg.items()):
        n = len(rs)
        m = lambda f: sum(f(r) for r in rs) / n
        print(f"\n== {k[0]} {k[1]}s: {n} Y-building losses")
        print(" cause: " + ", ".join(f"{c}={sum(r['cause']==c for r in rs)}" for c in ("neutral", "pulled", "other")))
        print(" region: " + ", ".join(f"{c}={sum(r['region']==c for r in rs)}" for c in ("home(x<=4)", "center", "K-home")))
        print(f" no Y W within 3 cells before the loss turn: {sum(r['yw3']==0 for r in rs)/n:.0%}; any within 1: "
              f"{sum(r['yw1']>0 for r in rs)/n:.0%}; mean nearest-Y-W dist {m(lambda r: min(r['yw_near'], 20)):.1f}; "
              f"mean Y W within 3 {m(lambda r: r['yw3']):.1f}")
        print(f" K escort W on the building: mean {m(lambda r: r['kw_at']):.1f}; share with K W>0 there: "
              f"{sum(r['kw_at']>0 for r in rs)/n:.0%}; K flags mean {m(lambda r: r['kf']):.1f}; "
              f"Y flag was on building: {sum(r['yf_here']>0 for r in rs)/n:.0%}")
        by_type = defaultdict(int)
        for r in rs:
            by_type[r["type"]] += 1
        print(" by type:", dict(sorted(by_type.items(), key=lambda kv: -kv[1])))


if __name__ == "__main__":
    main(sys.argv[1])
