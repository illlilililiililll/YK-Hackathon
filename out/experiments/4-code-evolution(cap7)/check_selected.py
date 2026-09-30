"""Run the chosen source as a real subprocess against v3 on fresh local seeds."""
import json
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))   # folder name has parentheses: import evolve directly
from engine.config import load_config
from runner import InProcessBot, SubprocessBot, run_match
from evolve import HERE, decide_for


def main():
    record = json.loads((HERE / "verdict.json").read_text(encoding="utf-8"))
    selected = next(x for x in record["finalists"] if x["id"] == record["verdict"]["chosen"])
    v3 = next(x for x in record["finalists"] if x["id"] == "v3")
    command = f"PYTHONPATH=bots/dist/starter/python {shlex.quote(sys.executable)} {shlex.quote(selected['source'])}"
    results = []
    for seed in range(600, 605):
        candidate = SubprocessBot(command, selected["id"])
        _, result = run_match(seed, load_config(), candidate, InProcessBot(decide_for(v3)))
        results.append(dict(result, max_turn_ms=round(candidate.max_turn_ms, 2)))
        print(seed, results[-1], flush=True)
    (HERE / "selected-subprocess-check.json").write_text(json.dumps(
        {"source": selected, "opponent": "v3", "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    assert all(r["reason"] != "forfeit" for r in results)


if __name__ == "__main__":
    main()
