"""Read per-seed replay metrics of runs produced by out/tools/evaluation/subprocess_eval.py.

  python out/tools/reporting/local_metrics.py <run dir> [<run dir> ...]

Each run dir holds summary.json and replays/seed-N.json (the replays are git-ignored; regenerate them first,
or read the committed metrics.txt next to summary.json).
"""
import json
import statistics
import sys
from pathlib import Path


for name in sys.argv[1:]:
    folder = Path(name)
    data = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    side = data["args"]["side"]
    replays = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("replays/seed-*.json"))]
    assert len(replays) == len(data["results"])
    def metrics(replay, turn):
        state = replay["turns"][min(turn - 1, len(replay["turns"]) - 1)]["state"]
        buildings = sum(b["owner"] == side for b in state["buildings"])
        value = sum(u[4] * {"F": 5, "W": 3, "S": 2}[u[1]] for u in state["units"] if u[0] == side)
        return buildings, value
    at20 = [metrics(r, 20) for r in replays]
    final = [metrics(r, len(r["turns"])) for r in replays]
    mean = lambda values: round(statistics.mean(values), 1)
    print(folder.name, data["summary"], "score", mean(r["score"][side] for r in data["results"]),
          "t20 buildings/value", (mean(x[0] for x in at20), mean(x[1] for x in at20)),
          "final buildings/value", (mean(x[0] for x in final), mean(x[1] for x in final)))
