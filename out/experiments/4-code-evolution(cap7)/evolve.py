"""Resume-safe two-generation code search using the official local engine."""
import hashlib
import json
import random
import shlex
import sys
import time
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "bots/dist/starter/python")]

from engine.config import load_config
from runner import InProcessBot, SubprocessBot, run_match
from out.tools.evaluation.policy_search import DEFAULT, match, original, policy, render_policy, summarize
import example_lv2

HERE = Path(__file__).resolve().parent
SOURCES = HERE / "candidates"
SOURCES.mkdir(exist_ok=True)
ROWS = HERE / "games.jsonl"
MAX_GAMES, MAX_SECONDS = 600, 900
TRAIN_SEEDS = range(400, 404)
FINAL_SEEDS = range(500, 508)
START = time.monotonic()
RNG = random.Random(20260928)
SPENT_BEFORE = 0


def identity(name, source, parent, operation, hypothesis, generation):
    path = SOURCES / f"{name}.py"
    if path.exists():
        assert path.read_text(encoding="utf-8") == source, name
    else:
        path.write_text(source, encoding="utf-8")
    return dict(id=name, source=str(path.relative_to(ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                parent=parent, operation=operation, hypothesis=hypothesis, generation=generation)


def read_rows():
    return [json.loads(line) for line in ROWS.read_text(encoding="utf-8").splitlines()] if ROWS.exists() else []


def append_row(row):
    with ROWS.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False) + "\n")
        file.flush()


def decide_for(item):
    source = (SOURCES / Path(item["source"]).name).read_text(encoding="utf-8")
    module = types.ModuleType(item["id"])
    exec(compile(source, item["source"], "exec"), module.__dict__)
    return module.decide


def change(source, operation):
    warrior_goals = 'goals = enemy_flags or {(b["x"], b["y"]) for b in targets if 5 <= b["x"] <= 9}'
    replacements = {
        "safe_goal": ('DANGER if goal in enemy_w else 0',
                      'DANGER if any(abs(goal[0]-x)+abs(goal[1]-y) <= 1 for x,y in enemy_w) else 0'),
        "focus_w": (warrior_goals,
                    'goals = ({min(enemy_flags, key=lambda p: maps[7, 7].get(p, 999))} if enemy_flags else {(b["x"], b["y"]) for b in targets if 5 <= b["x"] <= 9})'),
        "defend_w": (warrior_goals,
                     'threats = {p for p in enemy_flags if any(abs(p[0]-b["x"])+abs(p[1]-b["y"]) <= 2 for b in view.buildings if b["owner"] == own)}\n        goals = threats or enemy_flags or {(b["x"], b["y"]) for b in targets if 5 <= b["x"] <= 9}'),
        "adaptive_cap": ('min(CAP, len(targets) + 2)',
                         'min(max(3, CAP - (2 if sum(enemy_w.values()) > sum(warriors.values()) else 0)), len(targets) + 2)'),
        "independent_center": ('nearest_target = min(target_pos, key=lambda p: dist(base, p)) if target_pos else (7, 7)',
                               'nearest_target = min(target_pos, key=lambda p: dist(base, p) - (3 if 5 <= p[0] <= 9 else 0)) if target_pos else (7, 7)'),
        "independent_split": ('direction = direction_cache.setdefault(start, bfs(start, {warrior_goal}, init))',
                              'direction = bfs(start, foes or {warrior_goal}, init)'),
    }
    old, new = replacements[operation]
    if source.count(old) != 1:
        return None
    return source.replace(old, new)


HYPOTHESIS = {
    "safe_goal": "적 전투병과 인접한 점령 목표도 피하면 깃발병 생존이 오른다",
    "focus_w": "중앙에 가까운 적 깃발병 한 곳에 전투병을 모으면 교전이 유리하다",
    "defend_w": "소유 건물 부근의 적 깃발병을 먼저 추적하면 방어가 좋아진다",
    "adaptive_cap": "전투병 열세일 때 깃발병 생산 상한을 줄여 전투병 자원을 확보한다",
    "independent_center": "독립 정책의 초반 목표를 중앙으로 당겨 점수를 높인다",
    "independent_split": "독립 정책의 전투병을 분산 추적해 넓은 지역의 적 깃발병을 막는다",
}


def seed_sources():
    v3 = render_policy(DEFAULT)
    cap7 = (ROOT / "out/v0-unsubmitted/cap7-codex/source/main.py").read_text(encoding="utf-8")
    assert original("v3") == (ROOT / "bots/dist/starter/python/main.py").read_text(encoding="utf-8")
    independent = (HERE / "independent_main.py").read_text(encoding="utf-8")
    fixed = {
        "v3": identity("v3", v3, None, None, "기존 기준선", 0),
        "cap7": identity("cap7", cap7, "v3", "cap7-low", "이전 미사용 경기 우수 정책", 0),
        "independent": identity("independent", independent, None, "new-policy", "독립 생산·점령·집결 정책", 1),
    }
    gen1 = [fixed["independent"]]
    for op in ("safe_goal", "focus_w", "adaptive_cap"):
        src = change(cap7, op)
        assert src is not None
        gen1.append(identity("g1-" + op, src, "cap7", op, HYPOTHESIS[op], 1))
    return fixed, gen1


def opponents(fixed, final=False):
    pool = {
        "v2": policy("opp-v2", dict(DEFAULT, cap=12)),
        "v3": decide_for(fixed["v3"]),
        "cap7": decide_for(fixed["cap7"]),
        "fast-attack": policy("opp-fast", dict(DEFAULT, cap=3, reserve=0, plaza_reserve=0)),
        "slow-defense": policy("opp-slow", dict(DEFAULT, cap=8, reserve=6, plaza_reserve=4, danger=8)),
        "lv2": example_lv2.decide,
    }
    if final:
        pool["unseen-mixed-attack"] = policy("opp-unseen", dict(DEFAULT, cap=5, reserve=0, plaza_reserve=0, score=1.8, bonus=0, danger=0))
    return pool


def smoke(item):
    path = shlex.quote(item["source"])
    cmd = f"PYTHONPATH=bots/dist/starter/python {shlex.quote(sys.executable)} {path}"
    bot = SubprocessBot(cmd, item["id"])
    _, result = run_match(399, load_config(), bot, InProcessBot(example_lv2.decide), max_turns=1)
    return dict(result=result, max_turn_ms=round(bot.max_turn_ms, 2), passed=result["reason"] != "forfeit")


def points(row):
    return 1 if row["winner"] == row["side"] else .5 if row["winner"] == "DRAW" else 0


def tally(rows, candidate, side="Y"):
    selected = [r for r in rows if r["candidate"] == candidate and r["side"] == side]
    return summarize(selected)


def evaluate(items, pool, seeds, sides, phase, rows):
    index = {(r["candidate"], r["opponent"], r["seed"], r["side"], r["phase"]) for r in rows}
    config = load_config()
    for item in items:
        decide = decide_for(item)
        for opponent_name, opponent in pool.items():
            for seed in seeds:
                for side in sides(seed):
                    key = item["id"], opponent_name, seed, side, phase
                    if key in index:
                        continue
                    if len(rows) >= MAX_GAMES or SPENT_BEFORE + time.monotonic() - START >= MAX_SECONDS:
                        raise RuntimeError(f"budget exhausted: {len(rows)} games, {round(time.monotonic()-START)}s")
                    begun = time.monotonic()
                    row = match(item["id"], decide, opponent_name, opponent, seed, side, config)
                    row.update(phase=phase, generation=item["generation"], source_sha256=item["sha256"],
                               reward=points(row), match_seconds=round(time.monotonic()-begun, 3))
                    append_row(row)
                    rows.append(row)
                    index.add(key)
        own = [r for r in rows if r["candidate"] == item["id"] and r["phase"] == phase]
        print(phase, item["id"], summarize(own), flush=True)
    return rows


def generation_summary(items, rows, baseline):
    group = {item["id"]: [r for r in rows if r["candidate"] == item["id"] and r["phase"] == "train"] for item in items}
    base = group[baseline]
    base_by_opp = {op: sum(points(r) for r in base if r["opponent"] == op) for op in {r["opponent"] for r in base}}
    incumbent_by_opp = {op: sum(points(r) for r in group["cap7"] if r["opponent"] == op) for op in base_by_opp}
    result = {}
    for item in items:
        selected = group[item["id"]]
        by_opp = {op: sum(points(r) for r in selected if r["opponent"] == op) for op in base_by_opp}
        total = sum(points(r) for r in selected)
        forfeits = sum(r["reason"] == "forfeit" and r["forfeit"]["team"] == "Y" for r in selected)
        result[item["id"]] = dict(source_sha256=item["sha256"], parent=item["parent"], operation=item["operation"],
                                  hypothesis=item["hypothesis"], reward=total, by_opponent=by_opp,
                                  forfeits=forfeits, eligible=not forfeits and all(
                                      by_opp[op] >= base_by_opp[op] - 2 and by_opp[op] >= incumbent_by_opp[op] - 2
                                      for op in base_by_opp),
                                  summary=summarize(selected))
    candidates = [x for x in items if x["id"] != baseline]
    eligible = [x for x in candidates if result[x["id"]]["eligible"]]
    leader = max(eligible, key=lambda x: (result[x["id"]]["reward"], result[x["id"]]["summary"]["score_diff"], x["id"])) if eligible else next(x for x in items if x["id"] == "cap7")
    specialist = max(candidates, key=lambda x: (max(result[x["id"]]["by_opponent"][op] - base_by_opp[op] for op in base_by_opp), result[x["id"]]["reward"], x["id"]))
    return dict(policies=result, baseline_by_opponent=base_by_opp, incumbent_by_opponent=incumbent_by_opp,
                leader=leader["id"], specialist=specialist["id"])


def next_generation(fixed, gen1, summary):
    all_items = {x["id"]: x for x in list(fixed.values()) + gen1}
    parents = [all_items[x] for x in (summary["leader"], summary["specialist"], "cap7", "v3", "independent")]
    seen = {(SOURCES / Path(x["source"]).name).read_text(encoding="utf-8") for x in all_items.values()}
    children = []
    for parent in parents:
        source = (SOURCES / Path(parent["source"]).name).read_text(encoding="utf-8")
        choices = (["independent_center", "independent_split"] if parent["id"] == "independent" else
                   ["safe_goal", "focus_w", "defend_w", "adaptive_cap"])
        RNG.shuffle(choices)
        for op in choices:
            if op == parent["operation"]:
                continue
            evolved = change(source, op)
            if evolved is None:
                continue
            if evolved in seen:
                continue
            item = identity(f"g2-{len(children)+1}-{op}", evolved, parent["id"], op, HYPOTHESIS[op], 2)
            seen.add(evolved)
            children.append(item)
            break
        if len(children) == 3:
            break
    assert len(children) == 3, "Three distinct second-generation policies required"
    return children


def final_summary(items, rows):
    final_rows = [r for r in rows if r["phase"] == "final"]
    by = {item["id"]: {side: tally(final_rows, item["id"], side) for side in ("Y", "K")} for item in items}
    incumbent = max(("v3", "cap7"), key=lambda name: (by[name]["Y"]["points"], by[name]["Y"]["score_diff"], name))
    inc_opp = {op: sum(points(r) for r in final_rows if r["candidate"] == incumbent and r["side"] == "Y" and r["opponent"] == op)
               for op in {r["opponent"] for r in final_rows}}
    accepted = []
    for item in items:
        name = item["id"]
        if name in ("v3", "cap7"):
            continue
        opp = {op: sum(points(r) for r in final_rows if r["candidate"] == name and r["side"] == "Y" and r["opponent"] == op) for op in inc_opp}
        if (by[name]["Y"]["points"] >= max(by["v3"]["Y"]["points"], by["cap7"]["Y"]["points"]) + 3
                and all(opp[op] >= inc_opp[op] - 2 for op in inc_opp)
                and by[name]["Y"]["forfeits"] == 0):
            accepted.append(name)
    chosen = max(accepted, key=lambda name: (by[name]["Y"]["points"], by[name]["Y"]["score_diff"], name)) if accepted else incumbent
    return dict(by_policy=by, incumbent=incumbent, accepted=accepted, chosen=chosen,
                final_seed_range=[500, 507], unused_opponent="unseen-mixed-attack")


def main():
    global SPENT_BEFORE
    fixed, gen1 = seed_sources()
    rows = read_rows()
    SPENT_BEFORE = sum(r["match_seconds"] for r in rows)
    train_pool = opponents(fixed)
    baseline = fixed["v3"]
    for number, generation in ((1, gen1), (2, None)):
        if number == 2:
            generation = next_generation(fixed, gen1, summary1)
        for item in generation:
            smoke_path = HERE / f"{item['id']}-smoke.json"
            if not smoke_path.exists():
                smoke_path.write_text(json.dumps(smoke(item), ensure_ascii=False, indent=2), encoding="utf-8")
            assert json.loads(smoke_path.read_text(encoding="utf-8"))["passed"], item["id"]
        items = [baseline, fixed["cap7"]] + (gen1 if number == 1 else generation)
        rows = evaluate(items, train_pool, TRAIN_SEEDS, lambda _: ("Y",), "train", rows)
        summary = generation_summary(items, rows, "v3")
        (HERE / f"generation-{number}.json").write_text(json.dumps(dict(number=number, candidates=generation,
                 selection=summary), ensure_ascii=False, indent=2), encoding="utf-8")
        if number == 1:
            summary1 = summary
    first_best = max((x for x in gen1 if x["id"] != "independent"),
                     key=lambda item: (summary1["policies"][item["id"]]["reward"], item["id"]))
    second_best = max(generation, key=lambda item: (summary["policies"][item["id"]]["reward"], item["id"]))
    final_items = [fixed["v3"], fixed["cap7"], fixed["independent"], first_best, second_best]
    rows = evaluate(final_items, opponents(fixed, final=True), FINAL_SEEDS,
                    lambda seed: ("Y", "K") if seed < 502 else ("Y",), "final", rows)
    verdict = final_summary(final_items, rows)
    previous = HERE / "verdict.json"
    old = json.loads(previous.read_text(encoding="utf-8")) if previous.exists() else {}
    elapsed = old["elapsed_seconds"] if old.get("games") == len(rows) else round(time.monotonic()-START, 1)
    previous.write_text(json.dumps(dict(verdict=verdict, finalists=final_items, games=len(rows),
        elapsed_seconds=elapsed, match_seconds=round(sum(r["match_seconds"] for r in rows), 1)),
        ensure_ascii=False, indent=2), encoding="utf-8")
    print("VERDICT", verdict["chosen"], "games", len(rows), flush=True)


if __name__ == "__main__":
    main()
