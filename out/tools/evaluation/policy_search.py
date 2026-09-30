"""Bounded, reproducible policy search against the official local engine."""
import json
import statistics
import sys
import time
import types
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "bots/dist/starter/python")]

from engine.config import load_config
from runner import InProcessBot, run_match
import example_lv2

OUT = ROOT / "out/experiments/3-policy-weight-search(cap7)"
ZIPS = {"v2": "out/v1-v2-codex/v2.zip", "v3": "out/v3-codex/v3.zip"}


def original(version):
    with zipfile.ZipFile(ROOT / ZIPS[version]) as archive:
        return archive.read("main.py").decode()


DEFAULT = dict(cap=6, reserve=4, plaza_reserve=2, score=1, bonus=2, danger=4)


def render_policy(settings, source=None):
    source = source or original("v3")
    changes = (
        ("min(6, len(targets) + 2)", "min(CAP, len(targets) + 2)"),
        ('reserve = 4 if buildings[7, 7]["owner"] != own else 2',
         'reserve = RESERVE if buildings[7, 7]["owner"] != own else PLAZA_RESERVE'),
        ('bonus = 2 if b["type"] in ("DEPOT", "HOSPITAL", "HALL") else 0',
         'bonus = BONUS if b["type"] in ("DEPOT", "HOSPITAL", "HALL") else 0'),
        ('d - score - bonus + (4 if goal in enemy_w else 0)',
         'd - SCORE_WEIGHT * score - bonus + (DANGER if goal in enemy_w else 0)'),
    )
    for old, new in changes:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    constants = f"CAP={settings['cap']}\nRESERVE={settings['reserve']}\nPLAZA_RESERVE={settings['plaza_reserve']}\nSCORE_WEIGHT={settings['score']}\nBONUS={settings['bonus']}\nDANGER={settings['danger']}\n"
    marker = "\ndef decide(view, init):"
    assert source.count(marker) == 1
    return source.replace(marker, "\n" + constants + marker)


def policy(name, settings, source=None):
    module = types.ModuleType(name)
    exec(compile(render_policy(settings, source), name, "exec"), module.__dict__)
    return module.decide


class TimedBot(InProcessBot):
    def __init__(self, decide, name):
        super().__init__(decide, name)
        self.max_ms = 0
        self.max_bytes = 0
        self.max_lines = 0

    def collect_turn(self):
        start = time.perf_counter()
        lines, status = super().collect_turn()
        self.max_ms = max(self.max_ms, (time.perf_counter() - start) * 1000)
        self.max_bytes = max(self.max_bytes, len(("\n".join(lines) + "\nEND\n").encode()))
        self.max_lines = max(self.max_lines, len(lines) + 1)
        return lines, status


def match(name, decide, opponent_name, opponent, seed, side, config):
    # A real match starts a fresh bot process; clear its per-map distance cache here.
    for bot in (decide, opponent):
        bot.__globals__.pop("_dist", None)
        if "distances" in bot.__globals__:
            bot.__globals__["_dist"] = None
    candidate = TimedBot(decide, name)
    other = InProcessBot(opponent, "opponent")
    y, k = (candidate, other) if side == "Y" else (other, candidate)
    replay, result = run_match(seed, config, y, k)
    states = [replay["turns"][min(t - 1, len(replay["turns"]) - 1)]["state"]
              for t in (20, len(replay["turns"]))]
    def metrics(state):
        return [sum(b["owner"] == side for b in state["buildings"]),
                sum(u[4] * {"F": 5, "W": 3, "S": 2}[u[1]]
                    for u in state["units"] if u[0] == side)]
    return dict(candidate=name, opponent=opponent_name, seed=seed, side=side,
                winner=result["winner"], reason=result["reason"],
                forfeit=result.get("forfeit"), score=result["score"],
                turns=result["turns"], at20=metrics(states[0]), final=metrics(states[1]),
                max_ms=round(candidate.max_ms, 3), max_bytes=candidate.max_bytes,
                max_lines=candidate.max_lines)


def summarize(rows):
    points = [1 if r["winner"] == r["side"] else .5 if r["winner"] == "DRAW" else 0 for r in rows]
    return dict(games=len(rows), wins=points.count(1), draws=points.count(.5),
                losses=points.count(0), points=sum(points),
                score_diff=round(statistics.mean(r["score"][r["side"]] - r["score"]["K" if r["side"] == "Y" else "Y"] for r in rows), 2),
                at20_buildings=round(statistics.mean(r["at20"][0] for r in rows), 2),
                at20_value=round(statistics.mean(r["at20"][1] for r in rows), 2),
                forfeits=sum(r["reason"] == "forfeit" and r["forfeit"]["team"] == r["side"] for r in rows),
                max_ms=max(r["max_ms"] for r in rows), max_bytes=max(r["max_bytes"] for r in rows),
                max_lines=max(r["max_lines"] for r in rows))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("train", "holdout", "train2", "holdout2", "final"))
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    variants = {
        "v3": DEFAULT,
        "cap4": dict(DEFAULT, cap=4),
        "cap5": dict(DEFAULT, cap=5),
        "low-reserve": dict(DEFAULT, reserve=1, plaza_reserve=0),
        "high-reserve": dict(DEFAULT, reserve=7, plaza_reserve=4),
        "score-focus": dict(DEFAULT, score=1.6, bonus=1),
        "safe-flags": dict(DEFAULT, danger=8, bonus=3),
        "attack-mix": dict(DEFAULT, cap=4, reserve=1, plaza_reserve=0, score=1.4),
        "large-score": dict(DEFAULT, score=2.5, bonus=0),
        "large-bonus": dict(DEFAULT, score=.6, bonus=5),
        "no-danger": dict(DEFAULT, danger=0),
        "cap7-low": dict(DEFAULT, cap=7, reserve=1, plaza_reserve=0),
    }
    bots = {name: policy(name, settings) for name, settings in variants.items()}
    v2_source = original("v2").replace("min(12, len(targets) + 2)", "min(6, len(targets) + 2)")
    assert v2_source == original("v3")
    opponents = {
        "v2": policy("v2", dict(DEFAULT, cap=12)),
        "v3": bots["v3"],
        "fast-attack": policy("fast-attack", dict(DEFAULT, cap=3, reserve=0, plaza_reserve=0)),
        "slow-defense": policy("slow-defense", dict(DEFAULT, cap=8, reserve=6, plaza_reserve=4, danger=8)),
        "lv2": example_lv2.decide,
    }
    seeds = {"train": range(20, 24), "holdout": range(100, 108),
             "train2": range(30, 36), "holdout2": range(200, 208),
             "final": range(300, 320)}[args.phase]
    names = {"train": list(variants)[:8],
             "holdout": ["v3", "cap4", "low-reserve", "high-reserve"],
             "train2": ["v3", "large-score", "large-bonus", "no-danger", "cap7-low"],
             "holdout2": ["v3", "large-bonus", "cap7-low"],
             "final": ["v3", "cap7-low"]}[args.phase]
    if args.phase == "final":
        opponents.pop("lv2")
    config = load_config()
    rows = []
    for name in names:
        for opponent_name, opponent in opponents.items():
            for seed in seeds:
                for side in (("Y",) if args.phase.startswith("train") or args.phase == "final" else ("Y", "K")):
                    rows.append(match(name, bots[name], opponent_name, opponent, seed, side, config))
        print(args.phase, name, summarize([r for r in rows if r["candidate"] == name]), flush=True)
    payload = dict(phase=args.phase, seeds=list(seeds), policies={n: variants[n] for n in names},
                   opponents={n: (dict(DEFAULT, cap=12) if n == "v2" else
                                  dict(DEFAULT, cap=3, reserve=0, plaza_reserve=0) if n == "fast-attack" else
                                  dict(DEFAULT, cap=8, reserve=6, plaza_reserve=4, danger=8) if n == "slow-defense" else
                                  DEFAULT if n == "v3" else "official example_lv2.py") for n in opponents},
                   results=rows)
    (OUT / f"{args.phase}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
