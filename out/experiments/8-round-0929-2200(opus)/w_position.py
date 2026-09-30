"""Where are the warriors? For each side at T15/20/30/40 of official replays: share of W standing ON own buildings,
within 2 steps of own buildings (not on), within 2 of enemy buildings, elsewhere; stack count, largest stack share,
and "mass at the front": largest number of that side's W within radius 2 of any single cell.

  python "out/experiments/8-round-0929-2200(opus)/w_position.py" <replays...>
"""
import glob, json, sys
from collections import defaultdict


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    acc = defaultdict(lambda: defaultdict(list))
    for f in sorted(x for p in sys.argv[1:] for x in glob.glob(p)):
        g = json.load(open(f, encoding="utf-8"))
        win = g["result"]["winner"] == "Y"
        T = g["turns"]
        for t in (15, 20, 30, 40):
            if t >= len(T):
                continue
            o = T[t]["observation"]
            for s, e in (("Y", "K"), ("K", "Y")):
                own = {(b["x"], b["y"]) for b in o["buildings"] if b["owner"] == s}
                enb = {(b["x"], b["y"]) for b in o["buildings"] if b["owner"] == e}
                ws = [((u[2], u[3]), u[4]) for u in o["units"] if u[0] == s and u[1] == "W"]
                tot = sum(n for _, n in ws) or 1
                md = lambda c, S: min((abs(c[0] - q[0]) + abs(c[1] - q[1]) for q in S), default=99)
                on = sum(n for c, n in ws if c in own)
                near = sum(n for c, n in ws if c not in own and md(c, own) <= 2)
                front = sum(n for c, n in ws if c not in own and md(c, own) > 2 and md(c, enb) <= 2)
                mass = max((sum(n for c, n in ws if abs(c[0] - x) + abs(c[1] - y) <= 2) for x in range(15) for y in range(15)), default=0)
                k = ("win" if win else "loss", s, t)
                acc[k]["on"].append(on / tot); acc[k]["near"].append(near / tot); acc[k]["front"].append(front / tot)
                acc[k]["stacks"].append(len(ws)); acc[k]["mass"].append(mass); acc[k]["total"].append(tot)
    for k in sorted(acc):
        a = acc[k]
        m = lambda v: sum(v) / len(v)
        print(f"{k[0]:<5} {k[1]} T{k[2]:<3} W {m(a['total']):5.1f}  on-own {m(a['on']):.0%}  near-own {m(a['near']):.0%}  "
              f"near-enemy-bld {m(a['front']):.0%}  stacks {m(a['stacks']):4.1f}  max W within r2 of a cell {m(a['mass']):5.1f}")


if __name__ == "__main__":
    main()
