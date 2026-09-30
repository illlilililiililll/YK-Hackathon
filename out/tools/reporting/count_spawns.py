"""Count base spawns (3-token SPAWN) vs explicit-site spawns (5-token SPAWN) in a runner replay for one side.

  python out/tools/reporting/count_spawns.py <replay.json[.gz]> [--side Y]
"""
import argparse, gzip, json
from collections import Counter

ap = argparse.ArgumentParser()
ap.add_argument("replay"); ap.add_argument("--side", default="Y")
a = ap.parse_args()
g = json.load(gzip.open(a.replay, "rt", encoding="utf-8") if a.replay.endswith(".gz") else open(a.replay, encoding="utf-8"))
c = Counter()
first = {}
for t in g["turns"]:
    for ln in t["commands"][a.side]:
        tk = ln.split()
        if tk and tk[0] == "SPAWN":
            key = f"{'site' if len(tk) == 5 else 'base'}:{tk[1]}"
            c[key] += int(tk[2])
            if len(tk) == 5:
                first.setdefault(" ".join(tk[3:]), t["turn"])
print(dict(c), "explicit-site first seen (site -> turn):", first)
