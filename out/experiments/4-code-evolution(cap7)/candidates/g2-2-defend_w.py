"""Allocate flags across buildings and send warriors after opposing flags."""
from collections import deque

from protocol import DIRS, move, priority, run, spawn
from search import bfs


_dist = None


def distances(init):
    global _dist
    if _dist is None:
        _dist = {}
        for b in init.buildings:
            goal = (b["x"], b["y"])
            found = {goal: 0}
            todo = deque([goal])
            while todo:
                x, y = todo.popleft()
                for dx, dy in DIRS.values():
                    p = (x + dx, y + dy)
                    if p not in found and init.passable(*p):
                        found[p] = found[x, y] + 1
                        todo.append(p)
            _dist[goal] = found
    return _dist


def step(pos, goal, maps, danger=()):
    dist = maps[goal]
    current = dist.get(pos, 999)
    options = []
    for direction, (dx, dy) in DIRS.items():
        nxt = (pos[0] + dx, pos[1] + dy)
        if dist.get(nxt, 999) < current:
            options.append((nxt in danger, dist[nxt], direction))
    return min(options)[2] if options else None


CAP=7
RESERVE=1
PLAZA_RESERVE=0
SCORE_WEIGHT=1
BONUS=2
DANGER=4

def decide(view, init):
    maps = distances(init)
    own, opp = view.team, view.opp
    base = init.bases[own]
    buildings = {(b["x"], b["y"]): b for b in view.buildings}
    targets = [b for b in view.buildings if b["owner"] != own]
    enemy_flags = {(u["x"], u["y"]) for u in view.units if u["team"] == opp and u["kind"] == "F"}
    enemy_w = {(u["x"], u["y"]): u["count"] for u in view.units if u["team"] == opp and u["kind"] == "W"}
    danger = set(enemy_w)
    for x, y in enemy_w:
        danger.update((x + dx, y + dy) for dx, dy in DIRS.values())
    flags = {(u["x"], u["y"]): u["count"] for u in view.my_units("F")}
    warriors = {(u["x"], u["y"]): u["count"] for u in view.my_units("W")}
    commands = []

    # New units move on their spawn turn. Prefer a hospital nearer the front.
    sources = [base] + [(b["x"], b["y"]) for b in view.buildings
                        if b["type"] == "HOSPITAL" and b["owner"] == own]
    reserve = RESERVE if buildings[7, 7]["owner"] != own else PLAZA_RESERVE
    budget = max(0, view.my_resource - reserve)
    make_f = min(max(0, min(CAP, len(targets) + 2) - sum(flags.values())), budget // 5)
    if make_f:
        source = min(sources, key=lambda p: min((maps[b["x"], b["y"]].get(p, 999)
                                                 for b in targets), default=0))
        commands.append(spawn("F", make_f, *source) if source != base else spawn("F", make_f))
        flags[source] = flags.get(source, 0) + make_f
        budget -= make_f * 5
    engineering = sum(b["type"] == "ENG" and b["owner"] == own for b in view.buildings)
    wc = max(2, 3 - engineering)
    make_w = budget // wc
    if make_w:
        source = min(sources, key=lambda p: min((abs(q[0] - p[0]) + abs(q[1] - p[1])
                                                 for q in enemy_flags), default=maps[7, 7].get(p, 999)))
        commands.append(spawn("W", make_w, *source) if source != base else spawn("W", make_w))
        warriors[source] = warriors.get(source, 0) + make_w

    # One flag per building prevents the example bot's large single-file convoy.
    available = flags.copy()
    remaining = {(b["x"], b["y"]) for b in targets}
    assignments = {}
    while available and remaining:
        pairs = []
        for source in available:
            for goal in remaining:
                b = buildings[goal]
                d = maps[goal].get(source, 999)
                if d >= 999:
                    continue
                score = b["score"] if b["score"] >= 0 else (3 if 5 <= b["x"] <= 9 else 1.5)
                bonus = BONUS if b["type"] in ("DEPOT", "HOSPITAL", "HALL") else 0
                pairs.append((d - SCORE_WEIGHT * score - bonus + (DANGER if any(abs(goal[0]-x)+abs(goal[1]-y) <= 1 for x,y in enemy_w) else 0), d, source, goal))
        if not pairs:
            break
        _, _, source, goal = min(pairs)
        assignments.setdefault(source, []).append(goal)
        available[source] -= 1
        if not available[source]:
            del available[source]
        remaining.remove(goal)
    for source, goals in assignments.items():
        for goal in goals:
            direction = step(source, goal, maps, danger)
            if direction:
                commands.append(move(*source, "F", 1, direction))

    for source, count in warriors.items():
        threats = {p for p in enemy_flags if any(abs(p[0]-b["x"])+abs(p[1]-b["y"]) <= 2 for b in view.buildings if b["owner"] == own)}
        goals = threats or enemy_flags or {(b["x"], b["y"]) for b in targets if 5 <= b["x"] <= 9}
        direction = bfs(source, goals, init) if goals else None
        if direction:
            commands.append(move(*source, "W", count, direction))
    commands.append(priority(sorted([(b["x"], b["y"]) for b in targets],
                                    key=lambda p: -(buildings[p]["score"] if buildings[p]["score"] >= 0 else 3))))
    return commands


if __name__ == "__main__":
    run(decide)
