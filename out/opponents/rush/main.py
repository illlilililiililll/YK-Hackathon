"""Fixed local opponent 'rush': W-heavy blob that hunts enemy F, then enemy buildings. Written from the rules only."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "bots", "dist", "starter", "python"))
from protocol import spawn, move, run
from search import bfs


def decide(view, init):
    me, op = view.team, view.opp
    F = sorted(view.my_units("F"), key=lambda u: (u["y"], u["x"]))
    Wu = sorted(view.my_units("W"), key=lambda u: (u["y"], u["x"]))
    nf, nw = sum(u["count"] for u in F), sum(u["count"] for u in Wu)
    eng = sum(b["type"] == "ENG" and b["owner"] == me for b in view.buildings)
    wc = max(2, 3 - eng)
    budget = view.my_resource
    mf = min(max(0, 1 + nw // 4 - nf), budget // 5)
    cmds = []
    if mf:
        cmds.append(spawn("F", mf))
    mw = (budget - 5 * mf) // wc
    if mw:
        cmds.append(spawn("W", mw))
    ef = {(u["x"], u["y"]) for u in view.units if u["team"] == op and u["kind"] == "F"}
    eb = {(b["x"], b["y"]) for b in view.buildings if b["owner"] == op}
    nonown = {(b["x"], b["y"]) for b in view.buildings if b["owner"] != me}
    goal = ef or eb or nonown
    for u in Wu:
        s = bfs((u["x"], u["y"]), goal, init)
        if s:
            cmds.append(move(u["x"], u["y"], "W", u["count"], s))
    for u in F:
        s = bfs((u["x"], u["y"]), nonown - ef, init)
        if s:
            cmds.append(move(u["x"], u["y"], "F", u["count"], s))
    return cmds


if __name__ == "__main__":
    run(decide)
