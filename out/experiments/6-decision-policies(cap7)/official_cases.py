"""Reproduce v3 and compare isolated decisions on public official observations."""
import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "bots/dist/starter/python")]
from campus_bot import Init, View

HERE = Path(__file__).resolve().parent


def load(name, path):
    module = types.ModuleType(name)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


def counts(obs, side, kind):
    return sum(u[4] for u in obs["units"] if u[0] == side and u[1] == kind)


def snapshot(entry):
    obs = entry["observation"]
    return dict(turn=entry["turn"], buildings={s: sum(b["owner"] == s for b in obs["buildings"]) for s in "YK"},
                F={s: counts(obs, s, "F") for s in "YK"}, W={s: counts(obs, s, "W") for s in "YK"},
                Y_resource=obs["resources"]["Y"], Y_public_score=obs["scores"]["Y"])


def view_for(replay, turn):
    previous = replay["turns"][turn - 1]
    obs = previous["observation"]
    hs = [(x, y) for y, row in enumerate(obs["map"]) for x, cell in enumerate(row) if cell == "H"]
    first_move = next(line for line in replay["turns"][1]["command"]["lines"] if line.startswith("MOVE "))
    y_base = tuple(map(int, first_move.split()[1:3]))
    assert y_base in hs and len(hs) == 2
    buildings = [{key: b[key] for key in ("id", "x", "y", "type")} for b in obs["buildings"]]
    init = Init(15, 15, "Y", [list(row) for row in obs["map"]], buildings,
                {"Y": y_base, "K": next(h for h in hs if h != y_base)})
    scores = previous["revealed"]["buildingScores"]
    visible = [dict(b, score=scores.get(str(b["id"]), -1)) for b in obs["buildings"]]
    units = [dict(zip(("team", "kind", "x", "y", "count"), u)) for u in obs["units"]]
    return View(turn, init, obs["resources"]["Y"], obs["resources"]["K"], units, visible), init


def decisions(replay, turns, bots):
    result = {}
    for turn in turns:
        view, init = view_for(replay, turn)
        actual = replay["turns"][turn]["command"]["lines"]
        outcome = {}
        for name, module in bots.items():
            module._dist = None
            if hasattr(module, "_prev_flags"):
                module._prev_flags = (0, 0, 0)  # no off-policy loss estimate from a different history
            commands = module.decide(view, init)
            outcome[name] = dict(spawn=[line for line in commands if line.startswith("SPAWN ")],
                                 warrior_moves=[line for line in commands if " W " in line and line.startswith("MOVE ")],
                                 commands=commands)
        assert outcome["v3"]["commands"] == actual, (replay["gameId"], turn)
        result[str(turn)] = outcome
    return result


def official_diagnostics(replay):
    max_w = max_buildings = lost_f = owned_lost = 0
    first_reversal = first_w_reversal = first_building_reversal = None
    threatened_f = escorted_f = threatened_sites = guarded_sites = 0
    unguarded_examples = []
    previous = None
    for entry in replay["turns"]:
        obs = entry["observation"]
        turn = entry["turn"]
        own_w = [(u[2], u[3]) for u in obs["units"] if u[:2] == ["Y", "W"]]
        enemy_w = [(u[2], u[3]) for u in obs["units"] if u[:2] == ["K", "W"]]
        def near(x, y, group, radius):
            return any(abs(x - qx) + abs(y - qy) <= radius for qx, qy in group)
        for unit in obs["units"]:
            if unit[:2] == ["Y", "F"] and near(unit[2], unit[3], enemy_w, 2):
                threatened_f += unit[4]
                escorted_f += unit[4] * near(unit[2], unit[3], own_w, 1)
        for building in obs["buildings"]:
            if building["owner"] == "Y" and near(building["x"], building["y"], enemy_w, 2):
                threatened_sites += 1
                guarded = near(building["x"], building["y"], own_w, 1)
                guarded_sites += guarded
                if not guarded and len(unguarded_examples) < 5 and turn >= 20:
                    unguarded_examples.append((turn, building["id"], building["x"], building["y"]))
        if previous:
            commands = entry.get("command", {}).get("lines", [])
            produced = sum(int(line.split()[2]) for line in commands if line.startswith("SPAWN F "))
            lost_f += max(0, counts(previous, "Y", "F") + produced - counts(obs, "Y", "F"))
            owned_lost += sum(b["owner"] == "Y" and obs["buildings"][i]["owner"] != "Y"
                              for i, b in enumerate(previous["buildings"]))
        wgap = counts(obs, "Y", "W") - counts(obs, "K", "W")
        bgap = sum(b["owner"] == "Y" for b in obs["buildings"]) - sum(
            b["owner"] == "K" for b in obs["buildings"])
        if turn >= 10 and first_w_reversal is None and max_w >= 10 and wgap <= -10:
            first_w_reversal = turn
        if turn >= 10 and first_building_reversal is None and max_buildings >= 2 and bgap <= -2:
            first_building_reversal = turn
        if first_reversal is None and (first_w_reversal == turn or first_building_reversal == turn):
            first_reversal = (turn, "W" if first_w_reversal == turn else "buildings")
        if turn >= 10:
            max_w, max_buildings = max(max_w, wgap), max(max_buildings, bgap)
        previous = obs
    return dict(estimated_lost_F=lost_f, owned_lost=owned_lost, first_big_reversal=first_reversal,
                first_W_reversal=first_w_reversal, first_building_reversal=first_building_reversal,
                threatened_F=threatened_f, escorted_F=escorted_f,
                threatened_owned_sites=threatened_sites, guarded_owned_sites=guarded_sites,
                unguarded_examples=unguarded_examples)


def main():
    bots = {"v3": load("v3", ROOT / "bots/dist/starter/python/main.py"),
            "cap7": load("cap7", ROOT / "out/v0-unsubmitted/cap7-codex/source/main.py"),
            **{name: load(name, HERE / f"{name}.py") for name in ("defense", "adaptive", "combined")}}
    paths = [x for x in (ROOT / "out/official-replays").glob("[0-9][0-9]_*.json") if 20 <= int(x.name[:2]) <= 35]   # games 20-35 (the 9/28 22:00 round); later downloads 36-47 exist now
    assert len(paths) == 16
    f_only = 0
    by_game = {}
    for path in paths:
        replay = json.loads(path.read_text(encoding="utf-8"))
        if replay["result"]["winner"] != "K":
            continue
        turns = replay["turns"]
        count = 0
        for turn in range(21, min(40, len(turns) - 1) + 1):
            obs = turns[turn - 1]["observation"]
            commands = turns[turn].get("command", {}).get("lines", [])
            if (counts(obs, "Y", "W") < counts(obs, "K", "W")
                    and any(line.startswith("SPAWN F ") for line in commands)
                    and not any(line.startswith("SPAWN W ") for line in commands)):
                count += 1
        by_game[path.name[:2]] = count
        f_only += count
    case_results = {}
    for n, turns in ((31, (21, 30, 40)), (34, (20, 30, 40))):
        path = next((ROOT / "out/official-replays").glob(f"{n}_*.json"))
        replay = json.loads(path.read_text(encoding="utf-8"))
        case_results[str(n)] = dict(file=path.name, gameId=replay["gameId"],
                                    snapshots={str(t): snapshot(replay["turns"][t]) for t in (10, 20, 30, 40)},
                                    diagnostics=official_diagnostics(replay),
                                    counterfactual=decisions(replay, turns, bots))
    result = dict(loss_games=len(by_game), f_only_while_behind_21_40=f_only,
                  by_game=by_game, cases=case_results,
                  limitation="Candidate commands are isolated decisions on v3 observations; opponent code and original seed are unavailable.")
    (HERE / "official_cases.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("official", len(paths), "losses", len(by_game), "F-only behind", f_only,
          "reproduced commands", sum(len(x["counterfactual"]) for x in case_results.values()))
    for n in case_results:
        for turn, policies in case_results[n]["counterfactual"].items():
            print(n, turn, {name: data["spawn"] for name, data in policies.items()})


if __name__ == "__main__":
    main()
