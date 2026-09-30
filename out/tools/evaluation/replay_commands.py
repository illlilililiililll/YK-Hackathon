"""Attribute an official replay to a source: feed the recorded observations turn by turn to a candidate's
decide() and compare its output with the Y commands the server recorded.

  python out/tools/evaluation/replay_commands.py --src out/v6-claude/source out/official-replays/NN_*.json [...]

The agents are deterministic, so the source that actually played reproduces every recorded turn exactly
(command order included); another source diverges within a few turns. Output per replay and source:
identical turns / compared turns, and the first differing turn. It is a measurement: exit code 0 always.
Input of turn t = state after turn t-1 (observation of turn t-1; building scores as revealed to that side).
"""
import argparse, glob, importlib.util, json, os, sys

HELPERS = ("campus_bot", "protocol", "_generated", "search", "brain", "main")


def load_decide(src):
    src = os.path.abspath(src)
    for m in HELPERS:
        sys.modules.pop(m, None)
    sys.path.insert(0, src)
    try:
        spec = importlib.util.spec_from_file_location("cand_main", os.path.join(src, "main.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        import campus_bot as cb
    finally:
        sys.path.remove(src)
    fn = mod._make_decide() if hasattr(mod, "_make_decide") else mod.decide
    return fn, cb


def init_block(obs0, side):
    rows = obs0["map"]
    hs = sorted((x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch == "H")
    a, b = hs  # Y's base is on the Sinchon side (x <= 4 by the map generator)
    bases = {"Y": a, "K": b} if a[0] <= 4 else {"Y": b, "K": a}
    lines = [f"INIT {len(rows[0])} {len(rows)}", f"TEAM {side}"] + ["MAP " + r for r in rows]
    bl = sorted(obs0["buildings"], key=lambda b: b["id"])
    lines.append(f"BUILDINGS {len(bl)}")
    lines += [f"{b['id']} {b['x']} {b['y']} {b['type']}" for b in bl]
    lines += [f"BASE Y {bases['Y'][0]} {bases['Y'][1]}", f"BASE K {bases['K'][0]} {bases['K'][1]}"]
    return lines


KO = {"Y": 0, "K": 1}
UO = {"F": 0, "W": 1, "S": 2}


def turn_block(t, obs, revealed, side):
    opp = "K" if side == "Y" else "Y"
    units = sorted(obs["units"], key=lambda u: (KO[u[0]], UO[u[1]], u[3], u[2]))
    sc = {int(k): v for k, v in (revealed or {}).get("buildingScores", {}).items()}
    lines = [f"TURN {t}", f"RESOURCE {obs['resources'][side]} {obs['resources'][opp]}", f"UNITS {len(units)}"]
    lines += [f"{tm} {k} {x} {y} {c}" for tm, k, x, y, c in units]
    bl = sorted(obs["buildings"], key=lambda b: b["id"])
    lines.append(f"BUILDINGS {len(bl)}")
    lines += [f"{b['id']} {b['x']} {b['y']} {b['type']} {b['owner']} {b['stage']} {sc.get(b['id'], -1)}" for b in bl]
    return lines


def compare(src, path, max_turns=None):
    decide, cb = load_decide(src)
    g = json.load(open(path, encoding="utf-8"))
    side = g["side"]
    T = g["turns"]
    init = cb.parse_init(init_block(T[0]["observation"], side))
    same = n = 0
    first = None
    for i in range(1, len(T)):
        if max_turns and i > max_turns:
            break
        rec = (T[i].get("command") or {}).get("lines")
        if rec is None:
            continue
        view = cb.parse_turn(turn_block(T[i]["turn"], T[i - 1]["observation"], T[i - 1].get("revealed"), side), init)
        try:
            out = list(decide(view, init))
        except Exception as e:  # noqa: BLE001 - a crash counts as a mismatch
            out = [f"<exception {type(e).__name__}: {e}>"]
        n += 1
        if out == rec:
            same += 1
        elif first is None:
            first = (T[i]["turn"], out[:6], rec[:6])
    return n, same, first


def label(src):
    p = os.path.normpath(src)
    return os.path.basename(os.path.dirname(p)) if os.path.basename(p) == "source" else os.path.basename(p)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", action="append", required=True, help="source folder with main.py (repeatable)")
    ap.add_argument("--max-turns", type=int, default=None)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("replays", nargs="+")
    a = ap.parse_args()
    files = [f for p in a.replays for f in sorted(glob.glob(p))]
    for f in files:
        cells = []
        for s in a.src:
            n, same, first = compare(s, f, a.max_turns)
            cells.append(f"{label(s)} {same}/{n}" + ("" if first is None else f" (first diff T{first[0]})"))
            if a.verbose and first:
                print(f"    {label(s)} T{first[0]}\n      got {first[1]}\n      rec {first[2]}")
        print(f"{os.path.basename(f)[:40]:<42}", " | ".join(cells))


if __name__ == "__main__":
    main()
