"""Resume-safe paired matches and turn diagnostics for independent decision policies."""
import json
import statistics
import sys
import time
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "bots/dist/starter/python")]

from engine.config import load_config
from runner import InProcessBot, run_match
from out.tools.evaluation.policy_search import DEFAULT, TimedBot, policy
import example_lv2

HERE = Path(__file__).resolve().parent
ROWS = HERE / "games.jsonl"
TRAIN = range(1100, 1104)
HOLDOUT = range(1200, 1206)
MAX_GAMES, MAX_SECONDS = 486, 850


def load(name, path):
    module = types.ModuleType(name)
    source = path.read_text(encoding="utf-8")
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module.decide


def stock(state, side, kind):
    return sum(u[4] for u in state["units"] if u[0] == side and u[1] == kind)


def gap(state, side, kind):
    other = "K" if side == "Y" else "Y"
    return stock(state, side, kind) - stock(state, other, kind)


def building_gap(state, side):
    other = "K" if side == "Y" else "Y"
    return sum(b["owner"] == side for b in state["buildings"]) - sum(
        b["owner"] == other for b in state["buildings"])


def spawned(entry, side, kind):
    return sum(int(line.split()[2]) for line in entry["commands"][side]
               if line.startswith("SPAWN " + kind + " "))


def proximity(state, side, sites, radius):
    other = "K" if side == "Y" else "Y"
    foes = [(u[2], u[3]) for u in state["units"] if u[0] == other and u[1] == "W"]
    friends = [(u[2], u[3]) for u in state["units"] if u[0] == side and u[1] == "W"]
    threatened = covered = 0
    for x, y, count in sites:
        if any(abs(x - qx) + abs(y - qy) <= radius for qx, qy in foes):
            threatened += count
            covered += count * any(abs(x - qx) + abs(y - qy) <= 1 for qx, qy in friends)
    return threatened, covered


def diagnostics(replay, side):
    turns = replay["turns"]
    bmap = {b["id"]: (b["x"], b["y"]) for b in replay["map"]["buildings"]}
    counts = {kind: 0 for kind in "FW"}
    losses = {kind: 0 for kind in "FW"}
    owned_lost = threatened_flags = escorted_flags = 0
    threatened_sites = guarded_sites = f_only_behind = 0
    previous = None
    max_w = max_buildings = 0
    reversal = None
    for entry in turns:
        state = entry["state"]
        before_w_gap = gap(previous, side, "W") if previous else 0
        created = {kind: spawned(entry, side, kind) for kind in "FW"}
        for kind in "FW":
            counts[kind] += created[kind]
            losses[kind] += max(0, (stock(previous, side, kind) if previous else 0)
                                + created[kind] - stock(state, side, kind))
        if 21 <= entry["turn"] <= 40 and before_w_gap < 0 and created["F"] and not created["W"]:
            f_only_behind += 1
        if previous:
            owned_lost += sum(b["owner"] == side and state["buildings"][i]["owner"] != side
                              for i, b in enumerate(previous["buildings"]))
        fs = [(u[2], u[3], u[4]) for u in state["units"] if u[0] == side and u[1] == "F"]
        t, c = proximity(state, side, fs, 2)
        threatened_flags += t
        escorted_flags += c
        sites = [(bmap[b["id"]][0], bmap[b["id"]][1], 1)
                 for b in state["buildings"] if b["owner"] == side]
        t, c = proximity(state, side, sites, 2)
        threatened_sites += t
        guarded_sites += c
        wg, bg = gap(state, side, "W"), building_gap(state, side)
        if entry["turn"] >= 10 and reversal is None and ((max_w >= 10 and wg <= -10)
                                                          or (max_buildings >= 2 and bg <= -2)):
            reversal = {"turn": entry["turn"], "kind": "W" if max_w >= 10 and wg <= -10 else "buildings"}
        if entry["turn"] >= 10:
            max_w, max_buildings = max(max_w, wg), max(max_buildings, bg)
        previous = state
    snapshots = {str(n): {"actual_turn": min(n, len(turns)),
                          "W_gap": gap(turns[min(n, len(turns)) - 1]["state"], side, "W"),
                          "buildings_gap": building_gap(turns[min(n, len(turns)) - 1]["state"], side)}
                 for n in (10, 20, 40)}
    return dict(snapshots=snapshots, spawned=counts, estimated_lost=losses,
                threatened_flags=threatened_flags, escorted_flags=escorted_flags,
                threatened_owned_sites=threatened_sites, guarded_owned_sites=guarded_sites,
                owned_lost=owned_lost, f_only_while_w_behind_21_40=f_only_behind,
                first_big_reversal=reversal)


def match(name, decide, opponent_name, opponent, seed, side, config):
    for bot in (decide, opponent):
        bot.__globals__["_dist"] = None if "_dist" in bot.__globals__ else bot.__globals__.get("_dist")
        if "_prev_flags" in bot.__globals__:
            bot.__globals__["_prev_flags"] = (0, 0, 0)
    candidate = TimedBot(decide, name)
    other = InProcessBot(opponent, opponent_name)
    y, k = (candidate, other) if side == "Y" else (other, candidate)
    replay, result = run_match(seed, config, y, k)
    d = diagnostics(replay, side)
    return dict(candidate=name, opponent=opponent_name, seed=seed, side=side,
                winner=result["winner"], reason=result["reason"], forfeit=result.get("forfeit"),
                score=result["score"], turns=result["turns"], max_ms=round(candidate.max_ms, 3),
                max_bytes=candidate.max_bytes, max_lines=candidate.max_lines, **d)


def points(row):
    return 1 if row["winner"] == row["side"] else .5 if row["winner"] == "DRAW" else 0


def summary(rows):
    if not rows:
        return {}
    return dict(games=len(rows), wins=sum(points(r) == 1 for r in rows),
                draws=sum(points(r) == .5 for r in rows), losses=sum(points(r) == 0 for r in rows),
                points=sum(map(points, rows)),
                mean_score_diff=round(statistics.mean(r["score"][r["side"]] - r["score"]["K" if r["side"] == "Y" else "Y"] for r in rows), 2),
                mean_W_gap={n: round(statistics.mean(r["snapshots"][n]["W_gap"] for r in rows), 2) for n in ("10", "20", "40")},
                spawn_F=sum(r["spawned"]["F"] for r in rows), spawn_W=sum(r["spawned"]["W"] for r in rows),
                lost_F=sum(r["estimated_lost"]["F"] for r in rows), lost_W=sum(r["estimated_lost"]["W"] for r in rows),
                escort_rate=round(sum(r["escorted_flags"] for r in rows) / max(1, sum(r["threatened_flags"] for r in rows)), 3),
                site_guard_rate=round(sum(r["guarded_owned_sites"] for r in rows) / max(1, sum(r["threatened_owned_sites"] for r in rows)), 3),
                owned_lost=sum(r["owned_lost"] for r in rows),
                f_only_while_w_behind_21_40=sum(r["f_only_while_w_behind_21_40"] for r in rows),
                reversals=sum(r["first_big_reversal"] is not None for r in rows),
                forfeits=sum(r["reason"] == "forfeit" and r["forfeit"]["team"] == r["side"] for r in rows),
                max_ms=max(r["max_ms"] for r in rows), max_bytes=max(r["max_bytes"] for r in rows),
                max_lines=max(r["max_lines"] for r in rows))


def main():
    assert (ROOT / "out/v0-unsubmitted/cap7-codex/source/main.py").exists()
    candidates = {"v3": load("v3", ROOT / "bots/dist/starter/python/main.py"),
                  "cap7": load("cap7", ROOT / "out/v0-unsubmitted/cap7-codex/source/main.py")}
    candidates.update({n: load(n, HERE / f"{n}.py") for n in
                       ("defense", "adaptive", "combined", "defense-near2", "adaptive-margin4", "local-superiority")})
    opponents = {"v2": policy("op-v2", dict(DEFAULT, cap=12)),
                 "v3": load("op-v3", ROOT / "bots/dist/starter/python/main.py"),
                 "cap7": load("op-cap7", ROOT / "out/v0-unsubmitted/cap7-codex/source/main.py"),
                 "g1-safe-goal": load("op-g1", HERE.parent / "4-code-evolution(cap7)/candidates/g1-safe_goal.py"),
                 "fast-attack": policy("op-fast", dict(DEFAULT, cap=3, reserve=0, plaza_reserve=0)),
                 "slow-defense": policy("op-slow", dict(DEFAULT, cap=8, reserve=6, plaza_reserve=4, danger=8)),
                 "lv2": example_lv2.decide,
                 "unseen-mixed": policy("op-mixed", dict(DEFAULT, cap=5, reserve=0,
                                                     plaza_reserve=0, score=1.8, bonus=0, danger=0))}
    rows = [json.loads(line) for line in ROWS.read_text(encoding="utf-8").splitlines()] if ROWS.exists() else []
    done = {(r["phase"], r["candidate"], r["opponent"], r["seed"], r["side"]) for r in rows}
    spent = sum(r["match_seconds"] for r in rows)
    config = load_config()

    def run(phase, names, pool, seeds, sides):
        nonlocal spent
        for name in names:
            for op in pool:
                for seed in seeds:
                    for side in sides:
                        key = phase, name, op, seed, side
                        if key in done:
                            continue
                        if len(rows) >= MAX_GAMES or spent >= MAX_SECONDS:
                            raise RuntimeError(f"match budget exhausted at {len(rows)} games, {spent:.1f}s")
                        began = time.monotonic()
                        row = match(name, candidates[name], op, opponents[op], seed, side, config)
                        row.update(phase=phase, match_seconds=round(time.monotonic() - began, 3))
                        with ROWS.open("a", encoding="utf-8") as file:
                            file.write(json.dumps(row, ensure_ascii=False) + "\n")
                        rows.append(row)
                        done.add(key)
                        spent += row["match_seconds"]
            selected = [r for r in rows if r["phase"] == phase and r["candidate"] == name]
            print(phase, name, summary(selected), flush=True)

    known = tuple(n for n in opponents if n != "unseen-mixed")
    run("train", candidates, known, TRAIN, ("Y",))
    run("symmetry-K", ("v3", "cap7", "defense-near2", "adaptive", "combined"),
        known, range(1100, 1102), ("K",))
    train = {n: summary([r for r in rows if r["phase"] == "train" and r["candidate"] == n]) for n in candidates}
    opp_train = {n: {op: sum(points(r) for r in rows if r["phase"] == "train" and r["candidate"] == n and r["opponent"] == op)
                     for op in known} for n in candidates}
    eligible = [n for n in ("defense", "adaptive", "combined", "defense-near2", "adaptive-margin4", "local-superiority")
                if train[n]["points"] >= train["cap7"]["points"] + 2 and train[n]["forfeits"] == 0
                and all(opp_train[n][op] >= opp_train["cap7"][op] - 2 for op in known)]
    eligible.sort(key=lambda n: (train[n]["points"], train[n]["mean_score_diff"]), reverse=True)
    finalists = ("cap7",) + tuple(eligible[:2]) if eligible else ()
    report = dict(train_seeds=list(TRAIN), holdout_seeds=list(HOLDOUT), train=train,
                  train_by_opponent=opp_train, finalists=finalists, adopted=None,
                  symmetry_K_train_seeds=[1100, 1101],
                  symmetry_K={n: summary([r for r in rows if r["phase"] == "symmetry-K" and r["candidate"] == n])
                              for n in ("v3", "cap7", "defense-near2", "adaptive", "combined")})
    if finalists:
        run("holdout-Y", finalists, opponents, HOLDOUT, ("Y",))
        run("holdout-K", finalists, opponents, range(1200, 1202), ("K",))
        report["holdout"] = {n: {side: summary([r for r in rows if r["phase"] == "holdout-" + side and r["candidate"] == n])
                                 for side in "YK"} for n in finalists}
        by_op = {n: {op: sum(points(r) for r in rows if r["phase"] == "holdout-Y" and r["candidate"] == n and r["opponent"] == op)
                     for op in opponents} for n in finalists}
        report["holdout_by_opponent"] = by_op
        baseline = report["holdout"]["cap7"]
        for n in finalists[1:]:
            y, k = report["holdout"][n]["Y"], report["holdout"][n]["K"]
            if (y["points"] >= baseline["Y"]["points"] + 3
                    and y["mean_score_diff"] > baseline["Y"]["mean_score_diff"]
                    and y["forfeits"] == 0 and k["forfeits"] == 0
                    and k["points"] >= baseline["K"]["points"] - 3
                    and all(by_op[n][op] >= by_op["cap7"][op] - 2 for op in opponents)):
                if report["adopted"] is None or (y["points"], y["mean_score_diff"]) > (
                        report["holdout"][report["adopted"]]["Y"]["points"],
                        report["holdout"][report["adopted"]]["Y"]["mean_score_diff"]):
                    report["adopted"] = n
    report["games"] = len(rows)
    report["match_seconds"] = round(spent, 1)
    (HERE / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("VERDICT", report["adopted"], "games", len(rows), flush=True)


if __name__ == "__main__":
    main()
