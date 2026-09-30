"""Replay three preselected paired training cases without changing selection scores."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "bots/dist/starter/python")]
from engine.config import load_config
from runner import InProcessBot, run_match

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("decision_evaluate", HERE / "evaluate.py")
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)


def policy_path(name):
    if name == "cap7":
        return ROOT / "out/v0-unsubmitted/cap7-codex/source/main.py"
    if name == "v3":
        return ROOT / "bots/dist/starter/python/main.py"
    return HERE / f"{name}.py"


def main():
    recorded = {(r["candidate"], r["opponent"], r["seed"]): r for r in
                (json.loads(line) for line in (HERE / "games.jsonl").read_text(encoding="utf-8").splitlines())
                if r["phase"] == "train"}
    cases = (("cap7", "adaptive", "cap7", 1100),
             ("cap7", "adaptive", "cap7", 1103),
             ("cap7", "defense", "v3", 1100))
    folder = HERE / "cases"
    folder.mkdir(exist_ok=True)
    details = []
    for first, second, opponent, seed in cases:
        for name in (first, second):
            decide = ev.load("candidate", policy_path(name))
            other = ev.load("opponent", policy_path(opponent))
            replay, result = run_match(seed, load_config(), InProcessBot(decide, name),
                                       InProcessBot(other, opponent))
            old = recorded[name, opponent, seed]
            assert (result["winner"], result["score"], result["turns"]) == (
                old["winner"], old["score"], old["turns"])
            path = folder / f"{name}_vs_{opponent}_seed{seed}.json"
            path.write_text(json.dumps(replay, ensure_ascii=False), encoding="utf-8")
            diagnostics = ev.diagnostics(replay, "Y")
            details.append(dict(file=path.name, candidate=name, opponent=opponent,
                                seed=seed, result=result, diagnostics=diagnostics))
            print(path.name, result["winner"], result["score"],
                  diagnostics["snapshots"], diagnostics["first_big_reversal"], flush=True)
    (HERE / "cases.json").write_text(json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
