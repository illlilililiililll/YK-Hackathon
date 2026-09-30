"""Fixed local opponent 'pack': a single-blob style (inspired by replay geometry: K flags arrive with ~8 escort W).
ENG/HALL/DEPOT first, then all W in ONE pack that walks with 2 F to the nearest enemy-owned (else neutral)
building; new W rally to the pack. NOTE: it is NOT a faithful proxy of the official K bots -- locally v3 beats it,
while real K bots beat v3 ~70% of the time. Written from the rules + replay statistics only.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "bots", "dist", "starter", "python"))
from protocol import spawn, move, run
from search import bfs

EARLY = {"ENG": 6, "HALL": 5, "DEPOT": 3, "HOSPITAL": 1}


def man(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def decide(view, init):
    me, op = view.team, view.opp
    F = sorted(view.my_units("F"), key=lambda u: (u["y"], u["x"]))
    Wu = sorted(view.my_units("W"), key=lambda u: (u["y"], u["x"]))
    nf, nw = sum(u["count"] for u in F), sum(u["count"] for u in Wu)
    eng = sum(b["type"] == "ENG" and b["owner"] == me for b in view.buildings)
    wc = max(2, 3 - eng)
    budget = view.my_resource
    mf = min(max(0, 2 - nf), budget // 5)
    cmds = []
    if mf:
        cmds.append(spawn("F", mf))
    mw = (budget - 5 * mf) // wc
    if mw:
        cmds.append(spawn("W", mw))
    base = init.bases[me]
    nw_all = nw + mw
    stacks = {(u["x"], u["y"]): u["count"] for u in Wu}
    if mw:
        stacks[base] = stacks.get(base, 0) + mw
    pack = max(stacks, key=lambda p: (stacks[p], -man(p, init.bases[op]))) if stacks else base
    blds = view.buildings
    todo = [b for b in blds if b["owner"] != me]
    if not todo:
        return cmds

    def cost(b):
        d = man(pack, (b["x"], b["y"]))
        pri = EARLY.get(b["type"], 0) if view.turn < 25 else 0
        return d - (2 if b["owner"] == op else 0) - pri
    tgt = min(todo, key=lambda b: (cost(b), b["id"]))
    goal = {(tgt["x"], tgt["y"])}
    on_target = pack in goal
    for pos, n in sorted(stacks.items()):
        if pos == pack:
            if on_target:
                continue
            s = bfs(pos, goal, init)
        else:
            s = bfs(pos, {pack}, init)
        if s:
            cmds.append(move(pos[0], pos[1], "W", n, s))
    for u in F:
        pos = (u["x"], u["y"])
        if pos in goal:
            continue
        s = bfs(pos, {pack} if pos != pack else goal, init)
        if s:
            cmds.append(move(pos[0], pos[1], "F", u["count"], s))
    return cmds


if __name__ == "__main__":
    run(decide)
