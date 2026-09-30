"""Intent check on official replays: at each turn where one of Y's buildings was flipped, how many W would a
source have put ON that building (from the real observation of the turn before), versus the K W that stood there?

  python "out/experiments/8-round-0929-2200(opus)/counterfactual_defense.py" --src A --src B <replays...>
  (variants via INDEP_PARAMS in the environment are read at import time; use --params to set one per source:
   --src out/v6-claude/source --params "" --src <candidate> --params "defend=1")

Caveat printed with the result: K's moves are held fixed, so this measures whether the rule RESPONDS, not
whether it would win; and these are the games the hypothesis came from (not a held-out test).
"""
import argparse, glob, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools", "evaluation"))
from replay_commands import load_decide, init_block, turn_block  # noqa: E402

DIRS = {"U": (0, -1), "D": (0, 1), "L": (-1, 0), "R": (1, 0)}


def w_on(cmds, cell, view_units, side):
    """W of `side` ending on cell: those staying there + those moving in."""
    x, y = cell
    here = sum(u["count"] for u in view_units if u["team"] == side and u["kind"] == "W" and (u["x"], u["y"]) == cell)
    out = inn = 0
    for ln in cmds:
        tk = ln.split()
        if len(tk) == 6 and tk[0] == "MOVE" and tk[3] == "W":
            sx, sy, n, d = int(tk[1]), int(tk[2]), int(tk[4]), tk[5]
            dx, dy = DIRS[d]
            if (sx, sy) == cell:
                out += n
            if (sx + dx, sy + dy) == cell:
                inn += n
    return max(0, here - out) + inn


def run(src, params, path):
    os.environ["INDEP_PARAMS"] = "" if params == "none" else params
    decide, cb = load_decide(src)
    g = json.load(open(path, encoding="utf-8"))
    side = g["side"]
    T = g["turns"]
    init = cb.parse_init(init_block(T[0]["observation"], side))
    rows = []
    for i in range(1, len(T)):
        prev = T[i - 1]["observation"]
        view = cb.parse_turn(turn_block(T[i]["turn"], prev, T[i - 1].get("revealed"), side), init)
        out = list(decide(view, init))
        o = T[i]["observation"]
        pb = {b["id"]: b["owner"] for b in prev["buildings"]}
        for b in o["buildings"]:
            if pb[b["id"]] == side and b["owner"] != side:
                c = (b["x"], b["y"])
                kw = sum(u[4] for u in o["units"] if u[0] != side and u[1] == "W" and (u[2], u[3]) == c)
                rows.append((i, b["type"], kw, w_on(out, c, view.units, side)))
    return rows


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", action="append", required=True)
    ap.add_argument("--params", action="append", required=True)
    ap.add_argument("replays", nargs="+")
    a = ap.parse_args()
    files = [f for p in a.replays for f in sorted(glob.glob(p))]
    tot = {k: [0, 0, 0] for k in range(len(a.src))}
    for f in files:
        cells = []
        for k, (s, p) in enumerate(zip(a.src, a.params)):
            rows = run(s, p, f)
            n = len(rows)
            placed = sum(1 for r in rows if r[3] > 0)
            beat = sum(1 for r in rows if r[3] > r[2])
            tot[k][0] += n; tot[k][1] += placed; tot[k][2] += beat
            cells.append(f"[{p or 'v6'}] flips {n}: W placed {placed}, W > K W on cell {beat}")
        print(f"{os.path.basename(f)[:26]:<28}" + " | ".join(cells))
    for k, (s, p) in enumerate(zip(a.src, a.params)):
        n, placed, beat = tot[k]
        print(f"TOTAL [{p or 'v6'}]: flips {n}; source would have had W on the building in {placed} ({placed / max(1, n):.0%}); "
              f"more W than the K W that were there in {beat} ({beat / max(1, n):.0%})")
    print("Caveat: K's moves held fixed (response check only); these games generated the hypothesis (not held out).")


if __name__ == "__main__":
    main()
