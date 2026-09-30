"""Unit counts, resources, buildings at chosen turns of a runner replay (.json / .json.gz), plus flags lost per side.

  python "out/experiments/8-round-0929-2200(opus)/replay_macro.py" <replay> [turns, default 5,10,20,30,40]
Flags lost = F before + F spawned - F after, summed over turns (flags only leave the board by dying).
"""
import gzip, json, sys


def counts(state):
    c = {}
    for tm, k, x, y, n in state["units"]:
        c[tm + k] = c.get(tm + k, 0) + n
    return c


def spawned(cmds, kind):
    n = 0
    for ln in cmds:
        tk = ln.split()
        if len(tk) in (3, 5) and tk[0] == "SPAWN" and tk[1] == kind:
            n += int(tk[2])
    return n


def main():
    p = sys.argv[1]
    turns = [int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else "5,10,20,30,40").split(",")]
    g = json.load(gzip.open(p, "rt", encoding="utf-8") if p.endswith(".gz") else open(p, encoding="utf-8"))
    print(g["result"])
    prev = {}
    lost = {"Y": 0, "K": 0}
    for t in g["turns"]:
        c = counts(t["state"])
        # spawn requests can exceed stock; the applied list holds what the engine parsed, not what it paid for,
        # so bound the spawned flags by the observed increase at the base (approximation, good enough for totals)
        for side in "YK":
            want = spawned(t["commands"][side], "F")
            before, after = prev.get(side + "F", 0), c.get(side + "F", 0)
            lost[side] += max(0, before + want - after) if want == 0 else max(0, before - after)
        prev = c
        if t["turn"] in turns:
            nb = {o: sum(1 for b in t["state"]["buildings"] if b["owner"] == o) for o in "YK"}
            print(t["turn"], dict(sorted(c.items())), "res", t["state"]["resources"], "bld", nb, "F lost so far", dict(lost))
    print("flags lost (lower bound when spawning):", lost)


if __name__ == "__main__":
    main()
