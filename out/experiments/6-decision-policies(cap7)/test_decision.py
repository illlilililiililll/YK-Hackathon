"""Small checks for the two new decision branches and their combination."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "bots/dist/starter/python"))
from campus_bot import Init, View


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check():
    here = Path(__file__).resolve().parent
    bots = {name: load(name, path) for name, path in {
        "cap7": ROOT / "out/v0-unsubmitted/cap7-codex/source/main.py",
        "defense": here / "defense.py",
        "adaptive": here / "adaptive.py",
        "combined": here / "combined.py",
        "local-superiority": here / "local-superiority.py",
    }.items()}
    sites = [(7, 7, "PLAZA", "N"), (5, 5, "HALL", "Y"), (10, 10, "HALL", "K")]
    init_buildings = [dict(id=i, x=x, y=y, type=kind) for i, (x, y, kind, _) in enumerate(sites)]
    view_buildings = [dict(**b, owner=owner, stage=2 if owner != "N" else 0, score=3)
                      for b, (_, _, _, owner) in zip(init_buildings, sites)]
    init = Init(15, 15, "Y", [list("." * 15) for _ in range(15)], init_buildings,
                {"Y": (1, 1), "K": (13, 13)})
    units = [dict(team=t, kind=k, x=x, y=y, count=n) for t, k, x, y, n in (
        ("Y", "F", 5, 5, 1), ("Y", "F", 2, 2, 1), ("Y", "W", 5, 5, 4),
        ("K", "F", 10, 10, 1), ("K", "W", 6, 5, 2), ("K", "W", 5, 7, 10),
        ("K", "W", 10, 5, 15))]
    view = View(15, init, 30, 20, units, view_buildings)
    cmds = {name: bot.decide(view, init) for name, bot in bots.items()}
    def spawned(name, kind):
        return sum(int(line.split()[2]) for line in cmds[name]
                   if line.startswith("SPAWN " + kind + " "))
    assert spawned("adaptive", "F") < spawned("cap7", "F")
    assert spawned("combined", "W") > spawned("cap7", "W")
    def leaving(name):
        return sum(int(line.split()[4]) for line in cmds[name]
                   if line.startswith("MOVE 5 5 W "))
    assert leaving("cap7") == 4
    assert leaving("defense") <= 1
    assert leaving("combined") <= 1
    assert leaving("local-superiority") == 0
    print("decision checks passed")


if __name__ == "__main__":
    check()
