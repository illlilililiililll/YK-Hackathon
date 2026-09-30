"""Save and briefly inspect one reproducible local failure replay."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))   # folder name has parentheses: import evolve directly

from engine.config import load_config
from runner import InProcessBot, run_match
from evolve import ROOT, HERE, decide_for, opponents, seed_sources


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate")
    parser.add_argument("opponent")
    parser.add_argument("seed", type=int)
    args = parser.parse_args()
    fixed, gen1 = seed_sources()
    items = {x["id"]: x for x in list(fixed.values()) + gen1}
    candidate = decide_for(items[args.candidate])
    opponent = opponents(fixed, final=True)[args.opponent]
    replay, result = run_match(args.seed, load_config(), InProcessBot(candidate), InProcessBot(opponent))
    folder = HERE / "failures"
    folder.mkdir(exist_ok=True)
    path = folder / f"{args.candidate}-vs-{args.opponent}-seed{args.seed}.json"
    path.write_text(json.dumps(replay, ensure_ascii=False), encoding="utf-8")
    print(path, result)
    for turn in (10, 20, 40, result["turns"]):
        entry = replay["turns"][min(turn - 1, len(replay["turns"]) - 1)]
        state = entry["state"]
        owned = {side: sum(b["owner"] == side for b in state["buildings"]) for side in "YK"}
        units = {side: {kind: sum(u[4] for u in state["units"] if u[:2] == [side, kind])
                        for kind in "FW"} for side in "YK"}
        spawns = [c for c in entry["commands"]["Y"] if c.startswith("SPAWN")]
        print(turn, "owned", owned, "units", units, "resources", state["resources"], "Y spawn", spawns)


if __name__ == "__main__":
    main()
