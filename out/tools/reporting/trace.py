"""Turn-by-turn trace of a runner-format replay (.json or .json.gz).

  python out/tools/reporting/trace.py <replay> [--from 1] [--to 25] [--me Y]
Shows per turn: resources, my/enemy F cells, W stacks (top N), building owners changed this turn, events.
"""
import argparse, gzip, json, sys


def load(p):
    return json.load(gzip.open(p, "rt", encoding="utf-8") if p.endswith(".gz") else open(p, encoding="utf-8"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("replay"); ap.add_argument("--from", dest="t0", type=int, default=1)
    ap.add_argument("--to", dest="t1", type=int, default=25); ap.add_argument("--me", default="Y")
    ap.add_argument("--top", type=int, default=4)
    a = ap.parse_args()
    g = load(a.replay)
    me, op = a.me, ("K" if a.me == "Y" else "Y")
    bt = {b["id"]: b for b in g["map"]["buildings"]}
    print("result:", g["result"], "| bases:", g["map"]["bases"])
    print("buildings:", " ".join(f"{b['id']}:{b['type'][:3]}{b['score']}@{b['x']},{b['y']}" for b in g["map"]["buildings"]))
    prev = {b["id"]: "N" for b in g["map"]["buildings"]}
    for t in g["turns"]:
        st = t["state"]
        if a.t0 <= t["turn"] <= a.t1:
            def stacks(team, kind):
                s = sorted(((c, (x, y)) for tm, k, x, y, c in st["units"] if tm == team and k == kind), reverse=True)
                return s
            fmt = lambda s, n: " ".join(f"{c}@{p[0]},{p[1]}" for c, p in s[:n]) + (f" (+{len(s)-n} more)" if len(s) > n else "")
            ch = [f"{bt[b['id']]['type'][:3]}{b['id']}:{prev[b['id']]}>{b['owner']}" for b in st["buildings"] if b["owner"] != prev[b["id"]]]
            ev = [f"{e['type'][:3]}{'@%d,%d' % (e['x'], e['y'])}" for e in t["events"]]
            own = lambda team: sum(bt[b["id"]]["score"] for b in st["buildings"] if b["owner"] == team)
            print(f"T{t['turn']:>3} res {st['resources'][me]:>2}/{st['resources'][op]:>2} pts {own(me):>2}/{own(op):>2} "
                  f"| myW {fmt(stacks(me,'W'), a.top)} | myF {fmt(stacks(me,'F'), 6)} "
                  f"| opW {fmt(stacks(op,'W'), a.top)} | opF {fmt(stacks(op,'F'), 6)}")
            if ch or ev:
                print(f"      owners: {' '.join(ch)}   events: {' '.join(ev)}")
        prev = {b["id"]: b["owner"] for b in st["buildings"]}


if __name__ == "__main__":
    main()
