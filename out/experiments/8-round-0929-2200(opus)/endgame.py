"""Turn-by-turn tail of official replays: true score, occupation, W/F, stock, owner changes, Y spawns.

  python "out/experiments/8-round-0929-2200(opus)/endgame.py" <replay> [from_turn=135] [to_turn=160]
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from round_diag import true_scores, cnt  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
p = sys.argv[1]
a = int(sys.argv[2]) if len(sys.argv) > 2 else 135
b = int(sys.argv[3]) if len(sys.argv) > 3 else 160
g = json.load(open(p, encoding="utf-8"))
sc, bl = true_scores(g)
T = g["turns"]
print(os.path.basename(p), g["result"])
for i in range(max(1, a), min(b, len(T) - 1) + 1):
    o, pr = T[i]["observation"], T[i - 1]["observation"]
    s = {x: sum(sc.get(q["id"], 0) for q in o["buildings"] if q["owner"] == x) for x in "YK"}
    pb = {q["id"]: q["owner"] for q in pr["buildings"]}
    ch = [f"{bl[q['id']]['type'][:4]}{sc.get(q['id'])}@{q['x']},{q['y']}:{pb[q['id']]}>{q['owner']}" for q in o["buildings"] if q["owner"] != pb[q["id"]]]
    sp = [ln for ln in (T[i].get("command") or {}).get("lines", []) if ln.startswith("SPAWN")]
    occ = o.get("occTurns", {})
    print(f"T{i:>3} score {s['Y']:>2}:{s['K']:<2} occY {occ.get('Y')} W {cnt(o['units'], 'Y', 'W')}:{cnt(o['units'], 'K', 'W')} "
          f"F {cnt(o['units'], 'Y', 'F')}:{cnt(o['units'], 'K', 'F')} res {o['resources']['Y']}:{o['resources']['K']} {sp} {' '.join(ch)}")
