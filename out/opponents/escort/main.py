"""Fixed local opponent 'escort'. Built only from OBSERVABLE statistics of the K bots that beat us in the 47
public replays (out/experiments/8-round-0929-2200(opus)/k_tactics_47.txt): first warrior at turn ~2-3, about 7 flags
kept all game, everything else warriors (~28 W at T10, ~70 at T20), flags that advance with a warrior escort
(60% have a W adjacent, ~10 W on the cell when they flip one of our buildings), warriors spread over many stacks.
It is NOT a model of any team's private code.

Rules of this bot: keep <= FCAP flags; each flag claims the best reachable building not owned by us; once the
opening is over a flag only steps forward when enough warriors step with it (escort = enemy W near the next cell + MARGIN);
remaining warriors, in stacks of at most CHUNK: kill enemy flags they outnumber, relieve our threatened buildings,
otherwise advance on the nearest enemy owned building.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "bots", "dist", "starter", "python"))
from collections import deque
from protocol import spawn, move, run, priority

FCAP = 7
OPEN_TURNS = 8        # before this turn flags move without escort (all early flags are unescorted in the replays)
MARGIN = 2
CHUNK = 5             # ~70 W in ~19 stacks at T20 in the replays
HUNT_R = 8
VALUE = {"HALL": 4, "ENG": 4, "DEPOT": 3, "PLAZA": 3, "HOSPITAL": 2, "STATION": 1, "LIBRARY": 1, "WATCH": 1}
DIRS = (("U", 0, -1), ("D", 0, 1), ("L", -1, 0), ("R", 1, 0))
_dist = {}


def dist_from(init, goal):
    if goal not in _dist:
        d = {goal: 0}
        q = deque([goal])
        while q:
            x, y = q.popleft()
            for _, dx, dy in DIRS:
                p = (x + dx, y + dy)
                if p not in d and init.passable(*p):
                    d[p] = d[(x, y)] + 1
                    q.append(p)
        _dist[goal] = d
    return _dist[goal]


def step(init, pos, goal):
    """(direction, next cell) one step closer to goal, or (None, pos)."""
    d = dist_from(init, goal)
    cur = d.get(pos, 999)
    for name, dx, dy in DIRS:
        p = (pos[0] + dx, pos[1] + dy)
        if d.get(p, 999) < cur:
            return name, p
    return None, pos


def decide(view, init):
    me, op, t = view.team, view.opp, view.turn
    F = {}
    W = {}
    eW, eF = {}, {}
    for u in view.units:
        p = (u["x"], u["y"])
        if u["team"] == me:
            if u["kind"] in "FW":
                dct = F if u["kind"] == "F" else W
                dct[p] = dct.get(p, 0) + u["count"]
        elif u["kind"] == "W":
            eW[p] = eW.get(p, 0) + u["count"]
        elif u["kind"] == "F":
            eF[p] = eF.get(p, 0) + u["count"]
    blds = {(b["x"], b["y"]): b for b in view.buildings}
    base = init.bases[me]
    eng = sum(1 for b in view.buildings if b["type"] == "ENG" and b["owner"] == me)
    wc = max(2, 3 - eng)

    def ew_near(p, r):
        return sum(n for q, n in eW.items() if abs(q[0] - p[0]) + abs(q[1] - p[1]) <= r)

    cmds = []
    res = view.my_resource
    nf = sum(F.values())
    mf = 1 if nf < FCAP and res >= 5 and t < 150 else 0
    if mf:
        cmds.append(spawn("F", 1))
        F[base] = F.get(base, 0) + 1
        res -= 5
    mw = res // wc
    if mw:
        cmds.append(spawn("W", mw))
        W[base] = W.get(base, 0) + mw
    left = dict(W)            # warriors not yet ordered
    moves = []

    def send(src, n, goal):
        n = min(n, left.get(src, 0))
        if n <= 0:
            return 0
        d, nxt = step(init, src, goal)
        left[src] -= n
        # local superiority: never step next to more enemy warriors than we bring (hold and let stacks merge)
        if d and (nxt == goal and goal in eF or ew_near(nxt, 1) < n):
            moves.append(move(src[0], src[1], "W", n, d))
        return n

    # --- flags: one per target building
    targets = [p for p, b in blds.items() if b["owner"] != me]
    claimed = set()
    free = []                                          # flag instances not busy capturing
    for pos in sorted(F):
        n = F[pos]
        here = blds.get(pos)
        if here and here["owner"] != me:
            claimed.add(pos)                           # one flag captures here, keeping its escort
            n -= 1
            need = ew_near(pos, 1) + (MARGIN if t >= OPEN_TURNS else 0)
            left[pos] = left.get(pos, 0) - min(left.get(pos, 0), need)
        free += [pos] * n
    pairs = []
    for k, pos in enumerate(free):
        dm = dist_from(init, pos)
        for q in targets:
            if q in claimed or q in eF or dm.get(q, 999) >= 999:
                continue
            c = dm[q] - VALUE.get(blds[q]["type"], 1) * (1 if t < 30 else 0) - (2 if blds[q]["owner"] == op else 0)
            pairs.append((c, k, q))
    pairs.sort()
    assign = {}
    for c, k, q in pairs:                              # global greedy matching: stable from turn to turn
        if k not in assign and q not in claimed:
            assign[k] = q
            claimed.add(q)
    for k, pos in enumerate(free):
        goal = assign.get(k)
        if goal is None:
            continue
        d, nxt = step(init, pos, goal)
        if not d:
            continue
        threat = ew_near(nxt, 1)
        need = threat + MARGIN if t >= OPEN_TURNS or threat else 0
        have = left.get(pos, 0)
        if have < need:
            # wait here and call warriors in (nearest stacks first)
            for src in sorted(left, key=lambda s: (abs(s[0] - pos[0]) + abs(s[1] - pos[1]), s)):
                if need - have <= 0:
                    break
                if src != pos and left[src] > 0 and abs(src[0] - pos[0]) + abs(src[1] - pos[1]) <= 6:
                    have += send(src, need - have, pos)
            continue
        moves.append(move(pos[0], pos[1], "F", 1, d))
        if need:
            left[pos] -= need
            moves.append(move(pos[0], pos[1], "W", need, d))

    # --- hunters: one sufficient stack per enemy flag within HUNT_R steps (nearest stacks first)
    for q in sorted(eF, key=lambda q: (min(dist_from(init, q).get(s, 99) for s in left) if left else 99, q)):
        need = ew_near(q, 1) + 1
        dq = dist_from(init, q)
        srcs = sorted((s for s in left if left[s] > 0 and dq.get(s, 99) <= HUNT_R), key=lambda s: (dq.get(s, 99), s))
        if sum(left[s] for s in srcs) < need:
            continue
        for s in srcs:
            if need <= 0:
                break
            need -= send(s, min(left[s], need + 1), q)

    # --- remaining warriors, in chunks
    mine = [p for p, b in blds.items() if b["owner"] == me]
    for src in sorted(left):
        while left.get(src, 0) > 0:
            n = min(left[src], CHUNK)
            goal = None
            ds = dist_from(init, src)
            # 2) our building with enemy flags / warriors close by
            thr = [q for q in mine if any(abs(e[0] - q[0]) + abs(e[1] - q[1]) <= 3 for e in list(eF) + list(eW))]
            thr = [q for q in thr if ds.get(q, 99) <= 8]
            if thr:
                goal = min(thr, key=lambda q: (ds.get(q, 99), q))
            else:
                enemy = [q for q, b in blds.items() if b["owner"] == op]
                pool = enemy or [q for q in targets]
                if pool:
                    goal = min(pool, key=lambda q: (ds.get(q, 999), q))
            if goal is None or goal == src:
                break
            send(src, n, goal)
    cmds += moves
    order = sorted(targets, key=lambda q: -VALUE.get(blds[q]["type"], 1))
    if order:
        cmds.append(priority(order))
    return cmds


if __name__ == "__main__":
    run(decide)
