"""Independent grouped-defense policy for the generational search."""
from protocol import move, priority, run, spawn
from search import bfs


def decide(view, init):
    own, opp = view.team, view.opp
    base = init.bases[own]
    targets = [b for b in view.buildings if b["owner"] != own]
    owned = [b for b in view.buildings if b["owner"] == own]
    flags = {(u["x"], u["y"]): u["count"] for u in view.my_units("F")}
    warriors = {(u["x"], u["y"]): u["count"] for u in view.my_units("W")}
    foes = {(u["x"], u["y"]) for u in view.units if u["team"] == opp and u["kind"] == "F"}
    foe_w = {(u["x"], u["y"]) for u in view.units if u["team"] == opp and u["kind"] == "W"}
    hospitals = [(b["x"], b["y"]) for b in owned if b["type"] == "HOSPITAL"]
    sources = [base] + hospitals
    plaza_owned = any(b["type"] == "PLAZA" and b["owner"] == own for b in view.buildings)
    money = max(0, view.my_resource - (1 if plaza_owned else 3))
    commands = []

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def make(kind, count, goal):
        if not count:
            return
        source = min(sources, key=lambda p: dist(p, goal))
        commands.append(spawn(kind, count, *source) if source != base else spawn(kind, count))
        groups = flags if kind == "F" else warriors
        groups[source] = groups.get(source, 0) + count

    target_pos = {(b["x"], b["y"]) for b in targets}
    nearest_target = min(target_pos, key=lambda p: dist(base, p)) if target_pos else (7, 7)
    make_f = min(max(0, min(6, len(targets) + 1) - sum(flags.values())), money // 5)
    make("F", make_f, nearest_target)
    money -= make_f * 5
    eng = sum(b["type"] == "ENG" for b in owned)
    cost_w = max(2, 3 - eng)

    # A common target concentrates warriors around threats to owned buildings.
    if foes and owned:
        warrior_goal = min(foes, key=lambda p: min(dist(p, (b["x"], b["y"])) for b in owned))
    elif foes:
        warrior_goal = min(foes, key=lambda p: dist(p, (7, 7)))
    else:
        central = {p for p in target_pos if 5 <= p[0] <= 9}
        warrior_goal = min(central, key=lambda p: dist(p, (7, 7))) if central else (7, 7)
    make("W", money // cost_w, warrior_goal)

    free = flags.copy()
    remaining = target_pos.copy()
    while free and remaining:
        pairs = []
        for start in free:
            for goal in remaining:
                building = next(b for b in targets if (b["x"], b["y"]) == goal)
                value = building["score"] if building["score"] >= 0 else (3 if 5 <= goal[0] <= 9 else 1.5)
                threat = 5 if any(dist(goal, p) <= 1 for p in foe_w) else 0
                pairs.append((dist(start, goal) - value - (2 if building["type"] in ("DEPOT", "HOSPITAL", "HALL") else 0) + threat, start, goal))
        _, start, goal = min(pairs)
        direction = bfs(start, {goal}, init)
        if direction:
            commands.append(move(*start, "F", 1, direction))
        free[start] -= 1
        if not free[start]:
            del free[start]
        remaining.remove(goal)

    direction_cache = {}
    for start, count in warriors.items():
        direction = direction_cache.setdefault(start, bfs(start, {warrior_goal}, init))
        if direction:
            commands.append(move(*start, "W", count, direction))
    commands.append(priority(sorted(target_pos, key=lambda p: -next(
        b["score"] if b["score"] >= 0 else 3 for b in targets if (b["x"], b["y"]) == p))))
    return commands


if __name__ == "__main__":
    run(decide)
