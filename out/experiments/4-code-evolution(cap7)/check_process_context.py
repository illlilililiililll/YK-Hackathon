"""Compare process-check seeds with both policies under identical in-process conditions."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))   # folder name has parentheses: import evolve directly
from engine.config import load_config
from runner import InProcessBot, run_match
from evolve import HERE, decide_for, seed_sources


def main():
    fixed, _ = seed_sources()
    rows = []
    for seed in range(600, 605):
        for name in ("v3", "cap7"):
            _, result = run_match(seed, load_config(), InProcessBot(decide_for(fixed[name])),
                                  InProcessBot(decide_for(fixed["v3"])))
            rows.append(dict(policy=name, result=result))
            print(seed, name, result, flush=True)
    (HERE / "process-seed-context.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
