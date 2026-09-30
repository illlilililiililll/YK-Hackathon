"""One runnable integrity check for the completed evolutionary search."""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))   # folder name has parentheses: import evolve directly
from evolve import HERE, ROOT, SOURCES, FINAL_SEEDS, TRAIN_SEEDS, final_summary, read_rows


def main():
    rows = read_rows()
    keys = [(r["phase"], r["candidate"], r["opponent"], r["seed"], r["side"]) for r in rows]
    assert len(keys) == len(set(keys)) == 566
    assert set(TRAIN_SEEDS).isdisjoint(FINAL_SEEDS)
    assert all(r["seed"] in (TRAIN_SEEDS if r["phase"] == "train" else FINAL_SEEDS) for r in rows)
    assert all(r["reason"] != "forfeit" for r in rows)
    assert sum(r["phase"] == "train" for r in rows) == 216
    assert sum(r["phase"] == "final" for r in rows) == 350
    for number in (1, 2):
        generation = json.loads((HERE / f"generation-{number}.json").read_text(encoding="utf-8"))
        for item in generation["candidates"]:
            assert hashlib.sha256((SOURCES / Path(item["source"]).name).read_bytes()).hexdigest() == item["sha256"]
            assert (HERE / f"{item['id']}-smoke.json").exists()
    record = json.loads((HERE / "verdict.json").read_text(encoding="utf-8"))
    assert final_summary(record["finalists"], rows)["chosen"] == record["verdict"]["chosen"]
    print("ok", len(rows), "games", record["verdict"]["chosen"])


if __name__ == "__main__":
    main()
