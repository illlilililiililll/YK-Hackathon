"""Build three standalone decision policies from the unchanged cap7 baseline."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1] / "v0-unsubmitted/cap7-codex/source/main.py"


def replace_once(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new)


def adaptive(source):
    source = replace_once(source, "from search import bfs", "from search import bfs, capture_reserve")
    source = replace_once(source, "_dist = None", "_dist = None\n_prev_flags = (0, 0, 0)")
    source = replace_once(source, "def decide(view, init):\n    maps = distances(init)",
                          "def decide(view, init):\n    global _prev_flags\n    maps = distances(init)")
    old = '''    reserve = RESERVE if buildings[7, 7]["owner"] != own else PLAZA_RESERVE
    budget = max(0, view.my_resource - reserve)
    make_f = min(max(0, min(CAP, len(targets) + 2) - sum(flags.values())), budget // 5)
'''
    new = '''    live_f = sum(flags.values())
    lost_f = max(0, _prev_flags[1] + _prev_flags[2] - live_f) if _prev_flags[0] == view.turn - 1 else 0
    own_w, opposing_w = sum(warriors.values()), sum(enemy_w.values())
    threatened = any(abs(p[0] - q[0]) + abs(p[1] - q[1]) <= 2
                     for p in flags.keys() | {(b["x"], b["y"]) for b in view.buildings if b["owner"] == own}
                     for q in enemy_w)
    pressure = view.turn >= 9 and (opposing_w >= own_w + 8 or lost_f >= 2
                                    or (threatened and opposing_w > own_w and lost_f > 0))
    reserve = RESERVE if buildings[7, 7]["owner"] != own else PLAZA_RESERVE
    if pressure:
        reserve = max(reserve, capture_reserve(view))
    budget = max(0, view.my_resource - reserve)
    engineering = sum(b["type"] == "ENG" and b["owner"] == own for b in view.buildings)
    wc = max(2, 3 - engineering)
    make_f = min(max(0, min(CAP, len(targets) + 2) - live_f), budget // 5)
    if pressure:
        make_f = min(make_f, 1)
        if live_f and opposing_w > own_w and budget - 5 * make_f < 2 * wc:
            make_f = 0
'''
    source = replace_once(source, old, new)
    source = replace_once(source, '''    engineering = sum(b["type"] == "ENG" and b["owner"] == own for b in view.buildings)
    wc = max(2, 3 - engineering)
    make_w = budget // wc''', '''    make_w = budget // wc''')
    source = replace_once(source, "    return commands\n", "    _prev_flags = (view.turn, live_f, make_f)\n    return commands\n")
    return source


def defense(source):
    old = '''    for source, count in warriors.items():
        goals = enemy_flags or {(b["x"], b["y"]) for b in targets if 5 <= b["x"] <= 9}
        direction = bfs(source, goals, init) if goals else None
        if direction:
            commands.append(move(*source, "W", count, direction))
'''
    new = '''    # Assign a local guard before pursuing enemy flags. Avoid entering a larger enemy stack.
    threats = {}
    guarded_sites = flags.keys() | {(b["x"], b["y"]) for b in view.buildings if b["owner"] == own}
    for site in guarded_sites:
        nearby = sum(n for p, n in enemy_w.items()
                     if abs(site[0] - p[0]) + abs(site[1] - p[1]) <= 2)
        if nearby:
            threats[site] = nearby
    chase = enemy_flags or {(b["x"], b["y"]) for b in targets if 5 <= b["x"] <= 9}
    for source, count in warriors.items():
        local = [p for p in threats if abs(source[0] - p[0]) + abs(source[1] - p[1]) <= 4]
        guard = min(local, key=lambda p: (abs(source[0] - p[0]) + abs(source[1] - p[1]), -threats[p], p)) if local else None
        keep = min(count, threats[guard] + 1) if guard else 0
        if guard and guard != source:
            direction = bfs(source, {guard}, init)
            if direction:
                dx, dy = DIRS[direction]
                if enemy_w.get((source[0] + dx, source[1] + dy), 0) < keep:
                    commands.append(move(*source, "W", keep, direction))
        roaming = count - keep
        direction = bfs(source, chase, init) if roaming and chase else None
        if direction:
            dx, dy = DIRS[direction]
            if enemy_w.get((source[0] + dx, source[1] + dy), 0) < roaming:
                commands.append(move(*source, "W", roaming, direction))
'''
    return replace_once(source, old, new)


def local_superiority(source):
    old = '''        if direction:
            commands.append(move(*source, "W", count, direction))
'''
    new = '''        if direction:
            dx, dy = DIRS[direction]
            nxt = (source[0] + dx, source[1] + dy)
            local_enemy = sum(n for p, n in enemy_w.items()
                              if abs(p[0] - nxt[0]) + abs(p[1] - nxt[1]) <= 1)
            local_ally = sum(n for p, n in warriors.items()
                             if abs(p[0] - nxt[0]) + abs(p[1] - nxt[1]) <= 1)
            if local_ally > local_enemy:
                commands.append(move(*source, "W", count, direction))
'''
    return replace_once(source, old, new)


def main():
    baseline = BASE.read_text(encoding="utf-8")
    candidates = {"defense": defense(baseline), "adaptive": adaptive(baseline),
                  "combined": defense(adaptive(baseline)),
                  "defense-near2": replace_once(defense(baseline), "<= 4]", "<= 2]"),
                  "adaptive-margin4": replace_once(adaptive(baseline), "own_w + 8", "own_w + 4"),
                  "local-superiority": local_superiority(baseline)}
    for name, source in candidates.items():
        path = HERE / f"{name}.py"
        if path.exists():
            assert path.read_text(encoding="utf-8") == source, path
        else:
            path.write_text(source, encoding="utf-8")
        compile(source, str(path), "exec")
        print(path)


if __name__ == "__main__":
    main()
