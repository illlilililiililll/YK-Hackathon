"""Fixed local opponent 'turtle': takes only buildings on its own half, keeps W guards, kills F near its buildings."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "bots", "dist", "starter", "python"))
from protocol import spawn, move, run
from search import bfs


def decide(view, init):
    me, op = view.team, view.opp
    bx, by = init.bases[me]
    ox, oy = init.bases[op]
    F = sorted(view.my_units("F"), key=lambda u: (u["y"], u["x"]))
    Wu = sorted(view.my_units("W"), key=lambda u: (u["y"], u["x"]))
    nf, nw = sum(u["count"] for u in F), sum(u["count"] for u in Wu)
    mine_half = {(b["x"], b["y"]) for b in view.buildings
                 if abs(b["x"] - bx) + abs(b["y"] - by) <= abs(b["x"] - ox) + abs(b["y"] - oy)}
    todo = {(b["x"], b["y"]) for b in view.buildings if b["owner"] != me} & mine_half
    owned = {(b["x"], b["y"]) for b in view.buildings if b["owner"] == me}
    eng = sum(b["type"] == "ENG" and b["owner"] == me for b in view.buildings)
    wc = max(2, 3 - eng)
    budget = view.my_resource
    mf = min(max(0, min(len(todo), 2) - nf), budget // 5)
    cmds = []
    if mf:
        cmds.append(spawn("F", mf))
    mw = (budget - 5 * mf) // wc
    if mw:
        cmds.append(spawn("W", mw))
    ef = {(u["x"], u["y"]) for u in view.units if u["team"] == op and u["kind"] == "F"}
    threat = {e for e in ef if any(abs(e[0] - x) + abs(e[1] - y) <= 5 for x, y in owned | {(bx, by)})}
    guarded = set()
    for u in Wu:
        pos = (u["x"], u["y"])
        goal = threat or ((owned - guarded) if pos not in owned or pos in guarded else set())
        s = bfs(pos, goal, init) if goal else None
        if s:
            cmds.append(move(u["x"], u["y"], "W", u["count"], s))
        elif pos in owned:
            guarded.add(pos)
    for u in F:
        s = bfs((u["x"], u["y"]), todo - ef, init)
        if s:
            cmds.append(move(u["x"], u["y"], "F", u["count"], s))
    return cmds


if __name__ == "__main__":
    run(decide)
