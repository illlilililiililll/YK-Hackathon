"""Bounded, resumable local weight search around the cap7 policy (official engine, in-process).

One workflow, three recorded rounds. The round-specific choices are the PRESETS below (this file replaces the former
heartbeat_search.py, heartbeat_search_20260929.py and heartbeat-20260929-1000/search.py):

  train      candidate settings x known opponents, seeds `train`, side Y
  select     best train (points, score_diff) must beat cap7 by >= 2 points, else no hold-out is opened
  hold-out   cap7 vs the selected setting on unused seeds (Y, plus a small K symmetry check)
  adopt      >= +3 points, better mean score diff, 0 forfeits (and, where `by_opponent` is set, no opponent > 2 points worse)

  python out/tools/evaluation/weight_search.py --list
  python out/tools/evaluation/weight_search.py --preset 20260929-1000
  python out/tools/evaluation/weight_search.py --preset 20260929-1000 --out-dir /tmp/check   # e.g. after copying games.jsonl there

Rows are appended to <out-dir>/games.jsonl as they finish and finished (phase, candidate, opponent, seed, side) keys
are skipped, so an interrupted run resumes and a finished one replays nothing (it only rewrites result.json).
Opponents are local stand-ins (parameter variants of the v3 policy + the official Lv2), not real teams.
"""
import argparse
import json
import sys
import time
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "bots/dist/starter/python")]

from engine.config import load_config
from out.tools.evaluation.policy_search import DEFAULT, match, policy, render_policy, summarize
import example_lv2

CAP7_SRC = ROOT / "out/experiments/4-code-evolution(cap7)/candidates/cap7.py"
G1_SRC = ROOT / "out/experiments/4-code-evolution(cap7)/candidates/g1-safe_goal.py"
WS = ROOT / "out/experiments/5-weight-search-rounds(cap7)"

CAP7 = dict(DEFAULT, cap=7, reserve=1, plaza_reserve=0)


def cap7(**changes):
    return dict(CAP7, **changes)


PRESETS = {
    # 2026-09-28 22:00 public round. Unseen mixed attacker runs as separate `unseen-*` phases; no time/game budget.
    "20260928": dict(
        train=range(700, 704), holdout=range(800, 808), k_seeds=range(800, 802),
        settings={"cap7": CAP7,
                  "cap5-zero": dict(DEFAULT, cap=5, reserve=0, plaza_reserve=0),
                  "cap6-zero": dict(DEFAULT, cap=6, reserve=0, plaza_reserve=0),
                  "cap5-low": dict(DEFAULT, cap=5, reserve=1, plaza_reserve=0),
                  "cap6-low": dict(DEFAULT, cap=6, reserve=1, plaza_reserve=0)},
        cap7_opponent=False, unseen="unseen-mixed-attack", unseen_in_holdout=False,
        max_games=None, max_seconds=None, seconds_since="run", timed_rows=False,
        by_opponent=None, adopt_key_first=False, report_games=False, report_seconds=False),
    # 2026-09-29 02:13 run (no new public matches). Hold-out includes the unseen opponent; 254 games / 360 s cumulative.
    "20260929-0200": dict(
        train=range(900, 903), holdout=range(1000, 1006), k_seeds=range(1000, 1002),
        settings={"cap7": CAP7,
                  "danger0": cap7(danger=0), "danger8": cap7(danger=8), "bonus0": cap7(bonus=0), "score2": cap7(score=2),
                  "cap9-reserve2": dict(DEFAULT, cap=9, reserve=2, plaza_reserve=1)},
        cap7_opponent=True, unseen="unseen-mixed", unseen_in_holdout=True,
        max_games=254, max_seconds=360, seconds_since="all-runs", timed_rows=True,
        by_opponent="points", adopt_key_first=False, report_games=True, report_seconds=True),
    # 2026-09-29 10:00 public round. 240 games / 360 s per invocation; per-opponent check counts wins.
    "20260929-1000": dict(
        train=range(1100, 1103), holdout=range(1200, 1206), k_seeds=range(1200, 1202),
        settings={"cap7": CAP7,
                  "cap5-low": dict(DEFAULT, cap=5, reserve=1, plaza_reserve=0),
                  "danger6": cap7(danger=6), "bonus3": cap7(bonus=3), "score-half": cap7(score=.5)},
        cap7_opponent=True, unseen="unseen-mixed", unseen_in_holdout=True,
        max_games=240, max_seconds=360, seconds_since="run", timed_rows=False,
        by_opponent="wins", adopt_key_first=True, report_games=True, report_seconds=False),
}


def points(row):
    return 1 if row["winner"] == row["side"] else .5 if row["winner"] == "DRAW" else 0


def loaded(name, path):
    module = types.ModuleType(name)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module.decide


def search(preset, out_dir):
    P = PRESETS[preset]
    rows_file = out_dir / "games.jsonl"
    settings = P["settings"]
    assert render_policy(settings["cap7"]) == CAP7_SRC.read_text(encoding="utf-8")
    out_dir.mkdir(parents=True, exist_ok=True)
    bots = {name: policy(name, values) for name, values in settings.items()}
    opponents = {"v2": policy("opp-v2", dict(DEFAULT, cap=12)), "v3": policy("opp-v3", DEFAULT)}
    if P["cap7_opponent"]:
        opponents["cap7"] = policy("opp-cap7", settings["cap7"])
    opponents.update({
        "g1-safe-goal": loaded("opp-g1", G1_SRC),
        "fast-attack": policy("opp-fast", dict(DEFAULT, cap=3, reserve=0, plaza_reserve=0)),
        "slow-defense": policy("opp-slow", dict(DEFAULT, cap=8, reserve=6, plaza_reserve=4, danger=8)),
        "lv2": example_lv2.decide,
        P["unseen"]: policy("opp-unseen", dict(DEFAULT, cap=5, reserve=0, plaza_reserve=0, score=1.8, bonus=0, danger=0)),
    })
    known = tuple(name for name in opponents if name != P["unseen"])
    rows = [json.loads(line) for line in rows_file.read_text(encoding="utf-8").splitlines()] if rows_file.exists() else []
    done = {(r["phase"], r["candidate"], r["opponent"], r["seed"], r["side"]) for r in rows}
    config = load_config()
    began = time.monotonic()
    previous_seconds = sum(r["match_seconds"] for r in rows) if P["seconds_since"] == "all-runs" else 0

    def run(phase, names, seeds, sides, opponent_names):
        for name in names:
            for opp in opponent_names:
                for seed in seeds:
                    for side in sides:
                        key = phase, name, opp, seed, side
                        if key in done:
                            continue
                        if P["max_games"] and (len(rows) >= P["max_games"]
                                               or previous_seconds + time.monotonic() - began >= P["max_seconds"]):
                            raise RuntimeError(f"budget exhausted after {len(rows)} games")
                        started = time.monotonic()
                        row = match(name, bots[name], opp, opponents[opp], seed, side, config)
                        row["phase"] = phase
                        if P["timed_rows"]:
                            row.update(reward=points(row), match_seconds=round(time.monotonic() - started, 3))
                        with rows_file.open("a", encoding="utf-8") as file:
                            file.write(json.dumps(row, ensure_ascii=False) + "\n")
                        rows.append(row)
                        done.add(key)
            print(phase, name, summarize([r for r in rows if r["phase"] == phase and r["candidate"] == name]), flush=True)

    def by_phase(phase, name):
        return summarize([r for r in rows if r["phase"] == phase and r["candidate"] == name])

    run("train", settings, P["train"], ("Y",), known)
    train = {name: by_phase("train", name) for name in settings}
    leader = max(settings, key=lambda n: (train[n]["points"], train[n]["score_diff"]))
    winner = leader if leader != "cap7" and train[leader]["points"] >= train["cap7"]["points"] + 2 else None
    report = dict(train_seeds=list(P["train"]), holdout_seeds=list(P["holdout"]), settings=settings,
                  train=train, selected_for_holdout=winner)
    if P["adopt_key_first"]:
        report["adopt"] = False
    if winner:
        names = ("cap7", winner)
        hold_opps = tuple(opponents) if P["unseen_in_holdout"] else known
        run("holdout-Y", names, P["holdout"], ("Y",), hold_opps)
        run("holdout-K", names, P["k_seeds"], ("K",), hold_opps)
        if not P["unseen_in_holdout"]:
            run("unseen-Y", names, P["holdout"], ("Y",), (P["unseen"],))
            run("unseen-K", names, P["k_seeds"], ("K",), (P["unseen"],))
        report["holdout"] = {n: {s: by_phase("holdout-" + s, n) for s in "YK"} for n in names}
        if not P["unseen_in_holdout"]:
            report["unseen_diagnostic"] = {n: {s: by_phase("unseen-" + s, n) for s in "YK"} for n in names}
        base, challenger = (report["holdout"][n]["Y"] for n in names)
        adopt = (challenger["points"] >= base["points"] + 3 and challenger["score_diff"] > base["score_diff"]
                 and challenger["forfeits"] == 0)
        if P["by_opponent"]:
            score = points if P["by_opponent"] == "points" else (lambda r: r["winner"] == "Y")
            by_opp = {n: {op: sum(score(r) for r in rows if r["phase"] == "holdout-Y" and r["candidate"] == n
                                  and r["opponent"] == op) for op in opponents} for n in names}
            report["holdout_by_opponent"] = by_opp
            adopt = adopt and all(by_opp[winner][op] >= by_opp["cap7"][op] - 2 for op in opponents)
        report["adopt"] = adopt
    else:
        report["adopt"] = False
    if P["report_games"]:
        report["games"] = len(rows)
    if P["report_seconds"]:
        report["match_seconds"] = round(sum(r["match_seconds"] for r in rows), 1)
    (out_dir / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("VERDICT adopt=%s challenger=%s games=%d" % (report["adopt"], winner, len(rows)), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--preset", choices=sorted(PRESETS))
    parser.add_argument("--out-dir", type=Path, help="default: out/experiments/5-weight-search-rounds(cap7)/<preset>")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list or not args.preset:
        for name, P in PRESETS.items():
            print(name, "train", P["train"], "holdout", P["holdout"], "candidates", list(P["settings"]))
        return
    search(args.preset, args.out_dir or WS / args.preset)


if __name__ == "__main__":
    main()
