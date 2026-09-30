"""깃발병은 안전한 목표만, 전투병은 한 무리로 모아 이길 때만 싸운다."""
import sys
from collections import deque

from protocol import DIRS, move, priority, run, spawn

INF = 999
HUNT = 8           # 추격대가 쫓아갈 최대 거리
GUARD = 1          # 건물당 기본 수비 인원
ENDGAME = 0        # 마지막 몇 턴 수비 강화 (테스트 결과 끄는 게 더 강함)
_dist = {}          # 칸 → {칸: BFS 거리} (필요할 때 계산해 캐시)


# ------------------------------------------------------------------ 지도 도우미

def dist_from(p, init):
    """p 에서 모든 칸까지의 BFS 거리."""
    if p not in _dist:
        found = {p: 0}
        todo = deque([p])
        while todo:
            x, y = todo.popleft()
            for dx, dy in DIRS.values():
                q = (x + dx, y + dy)
                if q not in found and init.passable(*q):
                    found[q] = found[x, y] + 1
                    todo.append(q)
        _dist[p] = found
    return _dist[p]


def neighbors(p, init):
    return [(d, (p[0] + dx, p[1] + dy)) for d, (dx, dy) in DIRS.items()
            if init.passable(p[0] + dx, p[1] + dy)]


def toward(pos, goal, init):
    """goal 쪽으로 거리가 줄어드는 (방향, 칸) 후보들."""
    dist = dist_from(goal, init)
    here = dist.get(pos, INF)
    return [(d, q) for d, q in neighbors(pos, init) if dist.get(q, INF) < here]


def estimate(b, by_id):
    """공개 점수 → 대칭 짝(id 1↔2, 3↔4 …) 점수 → 기댓값(중앙 3, 진영 1.5)."""
    if b["score"] >= 0:
        return b["score"]
    if 1 <= b["id"] <= 16:
        mate = by_id.get(b["id"] + 1 if b["id"] % 2 else b["id"] - 1)
        if mate and mate["score"] >= 0:
            return mate["score"]
    return 3 if 5 <= b["x"] <= 9 else 1.5


# ------------------------------------------------------------------ 결정

def decide(view, init):
    try:
        return _decide(view, init)
    except Exception as exc:  # 예외로 죽으면 몰수패 → 이번 턴만 포기
        print(f"decide error T{view.turn}: {exc!r}", file=sys.stderr)
        return []


def _decide(view, init):
    own, opp = view.team, view.opp
    base = init.bases[own]
    enemy_base = init.bases[opp]
    buildings = {(b["x"], b["y"]): b for b in view.buildings}
    by_id = {b["id"]: b for b in view.buildings}
    targets = [b for b in view.buildings if b["owner"] != own]
    mine = [b for b in view.buildings if b["owner"] == own]
    value = {(b["x"], b["y"]): estimate(b, by_id)
             + (2 if b["type"] in ("DEPOT", "HOSPITAL", "HALL") else 0) for b in view.buildings}

    def units(team, kind):
        out = {}
        for u in view.units:
            if u["team"] == team and u["kind"] == kind:
                out[u["x"], u["y"]] = out.get((u["x"], u["y"]), 0) + u["count"]
        return out

    enemy_f, enemy_w = units(opp, "F"), units(opp, "W")
    flags, warriors = units(own, "F"), units(own, "W")

    # ---- 위협 지도: 다음 턴에 각 칸에 올 수 있는 적 전투병 수
    threat = {}

    def add_threat(p, n):
        for q in [p] + [q for _, q in neighbors(p, init)]:
            threat[q] = threat.get(q, 0) + n

    for p, n in enemy_w.items():
        add_threat(p, n)
    enemy_eng = sum(b["type"] == "ENG" and b["owner"] == opp for b in view.buildings)
    enemy_spawnable = view.opp_resource // max(2, 3 - enemy_eng)   # 생산 직후 바로 이동 가능
    for p in [enemy_base] + [(b["x"], b["y"]) for b in view.buildings
                             if b["type"] == "HOSPITAL" and b["owner"] == opp]:
        add_threat(p, enemy_spawnable)

    def near_enemy_w(p, r=2):
        d = dist_from(p, init)
        return sum(n for q, n in enemy_w.items() if d.get(q, INF) <= r)

    commands = []
    sources = [base] + [(b["x"], b["y"]) for b in mine if b["type"] == "HOSPITAL"]

    # ---- 전투병 목표: 무리 전체가 한 곳을 노린다
    total_w = sum(warriors.values())
    army = max(warriors, key=warriors.get) if warriors else base
    goals = []  # (점수, 칸)
    for b in mine:                                          # 1) 내 건물을 노리는 적 깃발병
        p = (b["x"], b["y"])
        if any(dist_from(p, init).get(q, INF) <= 2 for q in enemy_f):
            goals.append((20 + value[p], p))
    for p in enemy_f:                                       # 2) 점령 중인 적 깃발병 사냥
        b = buildings.get(p)
        if b and b["owner"] != opp:
            goals.append((10 + value[p], p))
    for b in targets:                                       # 3) 공성
        if b["owner"] == opp:
            p = (b["x"], b["y"])
            goals.append((value[p], p))
    best = None
    for score, p in goals:
        d = dist_from(p, init).get(army, INF)
        if d >= INF or total_w <= near_enemy_w(p):           # 이길 수 없는 곳은 제외
            continue
        s = score / (d + 3)
        if best is None or s > best[0]:
            best = (s, p)
    if best:
        w_goal = best[1]
    else:                                                    # 4) 전선 건물에서 대기
        front = sorted((b["x"], b["y"]) for b in mine)
        front.sort(key=lambda p: dist_from(enemy_base, init).get(p, INF))
        w_goal = front[0] if front else (7, 7)

    # ---- 생산
    income = 10 + 2 * sum(b["type"] == "HALL" for b in mine)
    capturing = sum(4 if buildings[p]["type"] == "PLAZA" else 2
                    for p in flags if p in buildings and buildings[p]["owner"] != own)
    reserve = max(0, capturing - income)          # 점령은 수입 뒤라 대부분 0
    budget = max(0, view.my_resource - reserve)

    def risky(p, mine_there=0):
        return threat.get(p, 0) > mine_there

    safe_targets = [b for b in targets if not risky((b["x"], b["y"]))]
    want_f = min(5, len(safe_targets)) - sum(flags.values())
    make_f = min(max(0, want_f), budget // 5)
    if make_f:
        ok = [s for s in sources if not risky(s)] or [base]
        source = min(ok, key=lambda s: min((dist_from((b["x"], b["y"]), init).get(s, INF)
                                            for b in safe_targets), default=0))
        commands.append(spawn("F", make_f, *source) if source != base else spawn("F", make_f))
        flags[source] = flags.get(source, 0) + make_f
        budget -= make_f * 5
    engineering = sum(b["type"] == "ENG" for b in mine)
    wc = max(2, 3 - engineering)
    make_w = budget // wc
    if make_w:
        ok = [s for s in sources if threat.get(s, 0) < make_w] or [base]
        source = min(ok, key=lambda s: dist_from(w_goal, init).get(s, INF))
        commands.append(spawn("W", make_w, *source) if source != base else spawn("W", make_w))
        warriors[source] = warriors.get(source, 0) + make_w

    # ---- 전투병 배치: 수비대 → 추격대 → 나머지(공통 목표) 순서로 인원을 나눈다.
    pool = dict(warriors)            # 칸 → 아직 배정 안 된 인원
    orders = []                      # (출발 칸, 목적지, 인원)

    def take(dest, need, max_d=INF):
        """dest 에서 가까운 칸부터 need 명까지 떼어 배정. 배정한 인원 반환."""
        dd = dist_from(dest, init)
        got = 0
        for p in sorted(pool, key=lambda p: dd.get(p, INF)):
            if got >= need or dd.get(p, INF) > max_d:
                break
            n = min(pool[p], need - got)
            orders.append((p, dest, n))
            pool[p] -= n
            got += n
            if not pool[p]:
                del pool[p]
        return got

    endgame = view.turn > 160 - ENDGAME
    # 1) 수비대: 내 건물마다 (주변 적 전투병 + 1)명, 가치 높은 건물부터
    for b in sorted(mine, key=lambda b: -value[(b["x"], b["y"])]):
        p = (b["x"], b["y"])
        need = near_enemy_w(p, 3) + GUARD
        if endgame:
            need = need * 2 + 1
        take(p, need)
    # 2) 추격대: 적 깃발병마다 (주변 적 전투병 + 1)명, 가까운 병력만
    for q in sorted(enemy_f, key=lambda q: min((dist_from(q, init).get((b["x"], b["y"]), INF)
                                                for b in mine), default=INF)):
        if not pool or endgame and not any(dist_from(q, init).get((b["x"], b["y"]), INF) <= 3
                                            for b in mine):
            continue
        take(q, near_enemy_w(q, 1) + 1 + enemy_f[q], max_d=HUNT)
    # 3) 나머지: 공통 목표(방어·공성)
    for p, n in list(pool.items()):
        orders.append((p, w_goal, n))

    w_next = {}
    wmoves = {}
    for p, dest, n in orders:
        options = sorted(toward(p, dest, init), key=lambda dq: threat.get(dq[1], 0)) if dest != p else []
        if options:
            d, q = options[0]
            wmoves[p, d] = wmoves.get((p, d), 0) + n
        else:
            q = p
        w_next[q] = w_next.get(q, 0) + n
    for (p, d), n in wmoves.items():
        commands.append(move(*p, "W", n, d))

    def danger(p):
        return threat.get(p, 0) > w_next.get(p, 0)

    # ---- 깃발병 목표 배정 (위험한 건물은 제외, 한 건물에 한 명)
    available = dict(flags)
    remaining = {(b["x"], b["y"]) for b in targets if not danger((b["x"], b["y"]))
                 and (b["x"], b["y"]) not in enemy_f}
    assignments = []
    while available and remaining:
        pairs = []
        for source in available:
            for goal in remaining:
                d = dist_from(goal, init).get(source, INF)
                if d >= INF or d > 160 - view.turn:
                    continue
                extra = 1 if buildings[goal]["owner"] == opp else 0
                pairs.append((d + extra - value[goal], d, source, goal))
        if not pairs:
            break
        _, _, source, goal = min(pairs)
        assignments.append((source, goal))
        available[source] -= 1
        if not available[source]:
            del available[source]
        remaining.remove(goal)

    # ---- 깃발병 이동: 위험 칸에는 들어가지 않는다
    moved = {}
    for source, goal in assignments:
        safe = [(d, q) for d, q in toward(source, goal, init) if not danger(q)]
        if safe:
            d = safe[0][0]
        elif not danger(source):
            continue                                   # 기다린다
        else:
            flee = [(d, q) for d, q in neighbors(source, init) if not danger(q)]
            if not flee:
                continue
            d = flee[0][0]
        moved[source, d] = moved.get((source, d), 0) + 1
    for source, n in available.items():                # 목표 없는 깃발병: 위험하면 피신
        if danger(source):
            flee = [(d, q) for d, q in neighbors(source, init) if not danger(q)]
            if flee:
                moved[source, flee[0][0]] = moved.get((source, flee[0][0]), 0) + n
    for (source, d), n in moved.items():
        commands.append(move(*source, "F", n, d))

    commands.append(priority(sorted([(b["x"], b["y"]) for b in targets],
                                    key=lambda p: -value[p])))
    return commands


if __name__ == "__main__":
    run(decide)
