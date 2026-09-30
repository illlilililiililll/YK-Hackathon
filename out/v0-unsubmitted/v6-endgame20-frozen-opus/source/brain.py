"""Independent Y agent policy. Works in a canonical frame (my base on the left, x <= 4);
main.py rotates K's view 180 degrees so both sides run exactly the same code (mirror = draw).

Owners are 'M' (me) / 'E' (enemy) / 'N'. Cells are indices y*15+x. All iteration is over sorted
lists / index ranges (no set or dict-order dependence).
"""
from collections import defaultdict, deque

W = H = 15
N = W * H
INF = 99
T_TOTAL = 160
DIRS = (("U", 0, -1), ("D", 0, 1), ("L", -1, 0), ("R", 1, 0))
# score-equivalent bonus for what a building does when I own it
FUNC = {"HALL": 3.5, "ENG": 3.0, "DEPOT": 1.5, "HOSPITAL": 1.0, "STATION": 0.6,
        "LIBRARY": 0.6, "WATCH": 0.3, "PLAZA": 0.5}

# tunables (Phase 3 sweeps these)
P = dict(fcap_early=10, fcap_late=8, early_turns=12, escort_margin=0, pool_radius=3,
         slack_w=1, top_cands=8,
         garrison=1,          # W kept on every owned building (0 = off, v0 behaviour)
         garrison_alert=0,    # extra garrison W when enemy F within 6 / enemy W within 4 of the building
         garrison_radius=8,   # only W within this many steps are pulled in as garrison
         hunt_r=6,            # chase enemy F with W from up to this many steps away (1 = v0 behaviour)
         hospital_spawn=1,    # spawn at the owned hospital nearest to the goal instead of always at the base
         defend=0,            # 1: threat-proportional defence of owned buildings BEFORE hunting (0 = v6 behaviour)
         defend_eta=2,        # an enemy flag within this many steps makes a building "threatened"
         endgame=20)           # last N turns: targets count if the flag arrives by T160; no far hunting


class Brain:
    def __init__(self, terrain, blds, my_base, op_base, params=None):
        self.p = dict(P, **(params or {}))
        self.pas = [terrain[i // W][i % W] != "#" for i in range(N)]
        self.nb = [[] for _ in range(N)]
        for i in range(N):
            if not self.pas[i]:
                continue
            x, y = i % W, i // W
            for d, dx, dy in DIRS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and self.pas[ny * W + nx]:
                    self.nb[i].append((ny * W + nx, d))
        self.near = [[i] + [j for j, _ in self.nb[i]] for i in range(N)]
        self.D = [self._bfs(i) for i in range(N)]
        self.btype = {y * W + x: t for x, y, t in blds}
        self.bcells = sorted(self.btype)
        self.base = my_base[1] * W + my_base[0]
        self.obase = op_base[1] * W + op_base[0]
        self.depot_mine = set()

    def _bfs(self, s):
        d = [INF] * N
        d[s] = 0
        q = deque([s])
        while q:
            i = q.popleft()
            for j, _ in self.nb[i]:
                if d[j] == INF:
                    d[j] = d[i] + 1
                    q.append(j)
        return d

    # ------------------------------------------------------------------ helpers
    def dir_to(self, c, j):
        for k, d in self.nb[c]:
            if k == j:
                return d
        return None

    def sc(self, i):
        if self.known[i] >= 0:
            return self.known[i]
        j = N - 1 - i  # point-symmetric partner has the same score
        if j in self.btype and self.known[j] >= 0:
            return self.known[j]
        if self.btype[i] == "PLAZA":
            return 3
        return 3.0 if 5 <= i % W <= 9 else 1.5

    def bval(self, i):
        t = self.btype[i]
        f = FUNC[t]
        if (t == "ENG" and self.eng_owned) or (t == "LIBRARY" and self.lib_owned) or \
                (t == "DEPOT" and i in self.depot_mine):
            f = 0.2 if t == "ENG" else 0.0
        f *= min(1.0, (T_TOTAL - self.turn) / 60.0)
        s = self.sc(i)
        return 2 * s + f if self.own[i] == "E" else s + f

    def step_toward(self, c, t):
        """Neighbour of c one step closer to t (ties: least enemy-W exposure, then direction order)."""
        if c == t:
            return c
        dc = self.D[c][t]
        best = None
        for j, _ in self.nb[c]:
            if self.D[j][t] == dc - 1:
                k = (self.eW1[j], 0)
                if best is None or k < best[0]:
                    best = (k, j)
        return best[1] if best else c

    def ew_r(self, i, r):
        return sum(n for k, n in self.ecellsW if self.D[k][i] <= r)

    def myw_r(self, i, r):
        return sum(self.remW[k] for k in self.wcells if self.D[k][i] <= r)

    def capw(self, n):
        return sum(self.remW[j] for j in self.near[n])

    # ------------------------------------------------------------------ move bookkeeping
    def move(self, c, kind, n, j):
        if n <= 0:
            return
        (self.remW if kind == "W" else self.remF)[c] -= n
        if kind == "W" and j != c:
            self.arrW[j] += n
        if kind == "W" and j == c:
            self.arrW[c] += n
        if j != c:
            self.moves[(c, kind, j)] += n

    def escort(self, dest, need, pref):
        got = 0
        for j in [pref] + [k for k in self.near[dest] if k != pref]:
            if got >= need:
                break
            if self.remW[j] > 0 and (j == dest or self.D[j][dest] <= 1):
                take = min(self.remW[j], need - got)
                self.move(j, "W", take, dest)
                got += take
        return got

    # ------------------------------------------------------------------ main entry
    def act(self, turn, res, ores, units, blds):
        self.turn = turn
        self.mF, self.mW = [0] * N, [0] * N
        eF = [0] * N
        eW = [0] * N
        for team, kind, x, y, c in units:
            i = y * W + x
            if team == "M":
                if kind == "F":
                    self.mF[i] += c
                elif kind == "W":
                    self.mW[i] += c
            else:
                if kind == "F":
                    eF[i] += c
                elif kind == "W":
                    eW[i] += c
        self.own, self.stage, self.known = ["N"] * N, [0] * N, [-1] * N
        halls = eng = lib = 0
        for x, y, t, owner, stage, score in blds:
            i = y * W + x
            self.own[i], self.stage[i], self.known[i] = owner, stage, score
            if owner == "M" and stage == 2:
                halls += t == "HALL"
                eng += t == "ENG"
                lib += t == "LIBRARY"
                if t == "DEPOT":
                    self.depot_mine.add(i)
        self.eng_owned, self.lib_owned = eng > 0, lib > 0
        self.eF = eF
        self.ecellsW = [(i, eW[i]) for i in range(N) if eW[i]]
        self.eW1 = [0] * N
        for k, n in self.ecellsW:
            for j in self.near[k]:
                self.eW1[j] += n

        # ---- spawn
        wc = max(2, 3 - eng)
        nF, nW = sum(self.mF), sum(self.mW)
        inc = 10 + 2 * halls
        budget = res
        cmds = []
        f_new = 0
        if turn < T_TOTAL:
            k_cap = 0
            for i in self.bcells:
                if not (self.own[i] == "M" and self.stage[i] == 2):
                    k_cap += sum(self.mF[j] for j in self.near[i])
            budget -= max(0, 2 * k_cap - inc)
            if turn <= T_TOTAL - 8:
                open_t = sum(1 for i in self.bcells if not (self.own[i] == "M" and self.stage[i] == 2))
                fcap = self.p["fcap_early"] if turn <= self.p["early_turns"] else self.p["fcap_late"]
                if nW >= nF or turn <= self.p["early_turns"]:
                    f_new = max(0, min(min(open_t, fcap) - nF, budget // 5))
        else:
            budget = res
        budget = max(0, budget)
        w_new = max(0, (budget - 5 * f_new) // wc)
        site_f = site_w = self.base
        if self.p["hospital_spawn"]:
            hosp = [i for i in self.bcells if self.btype[i] == "HOSPITAL" and self.own[i] == "M" and self.stage[i] == 2]
            if hosp:
                tgt = self.best_target(self.base, 10 ** 6)
                efs = [i for i in range(N) if self.eF[i]]
                gw = min(efs, key=lambda i: (self.D[self.base][i], i)) if efs else tgt
                pick = lambda goal: self.base if goal is None else min([self.base] + hosp, key=lambda s: (self.D[s][goal], s != self.base, s))
                site_f, site_w = pick(tgt), pick(gw)
        for kind, n, site in (("F", f_new, site_f), ("W", w_new, site_w)):
            if n:
                cmds.append(("spawn", kind, n) if site == self.base else ("spawn", kind, n, site % W, site // W))
        self.mF[site_f] += f_new
        self.mW[site_w] += w_new
        self.remF, self.remW = self.mF[:], self.mW[:]
        self.wcells = [i for i in range(N) if self.remW[i]]
        self.moves = defaultdict(int)
        self.arrW = [0] * N
        self.plan_moves()
        for (c, kind, j), n in sorted(self.moves.items()):
            cmds.append(("move", c % W, c // W, kind, n, self.dir_to(c, j)))
        pr = []
        for (c, kind, j), n in sorted(self.moves.items()):
            if kind == "F" and j in self.btype and j not in pr:
                pr.append(j)
        for c in range(N):
            if self.mF[c] and c in self.btype and c not in pr and self.remF[c] >= 0:
                pr.append(c)
        pr.sort(key=lambda i: (-self.bval(i), i))
        if len(pr) >= 2:
            cmds.append(("prio", [(i % W, i // W) for i in pr]))
        return cmds

    # ------------------------------------------------------------------ movement planning
    def capturable(self, i):
        return i in self.btype and not (self.own[i] == "M" and self.stage[i] == 2)

    def plan_moves(self):
        claimed = set()
        # 1) F already standing on a building I still have to take: stay, keep it escorted
        for c in range(N):
            if self.remF[c] and self.capturable(c):
                claimed.add(c)
                need = self.eW1[c]
                if self.eF[c] and need == 0:
                    need = 1
                if need > self.capw(c):
                    # cannot be held: flee to the safest neighbour instead of feeding the enemy
                    j = self.safest(c)
                    if j != c:
                        claimed.discard(c)
                        self.move(c, "F", self.remF[c], j)
                        continue
                self.escort(c, need, c)
                self.remF[c] = 0
        # 2) remaining F: global greedy (value / eta) over feasible targets
        cands = []
        for c in range(N):
            if not self.remF[c]:
                continue
            for i in self.bcells:
                if not self.capturable(i):
                    continue
                eta = self.D[c][i]
                if eta >= INF or self.too_late(eta):
                    continue
                cands.append((-self.bval(i) / (eta + 1.5), c, i))
        cands.sort()
        for _, c, i in cands:
            if not self.remF[c] or i in claimed:
                continue
            eta = self.D[c][i]
            r = min(eta, self.p["pool_radius"])
            thr = self.ew_r(i, r)
            pool = self.myw_r(c, self.p["pool_radius"])
            if thr > pool - self.p["escort_margin"] and thr > 0:
                continue
            nxt = self.step_toward(c, i)
            need = self.eW1[nxt]
            if self.eF[nxt] and need == 0:
                need = 1
            if need > self.capw(nxt) - self.p["escort_margin"] and need > 0:
                continue
            if need == 0 and self.ew_r(nxt, 2) > 0 and self.capw(nxt) > 0:
                need = 1
            claimed.add(i)
            self.escort(nxt, need, c)
            self.move(c, "F", 1, nxt)
        # 3) F that found nothing safe: hold or retreat
        for c in range(N):
            if self.remF[c]:
                j = self.safest(c)
                need = self.eW1[j]
                self.escort(j, need, c)
                self.move(c, "F", self.remF[c], j)
        # 4) W: defend threatened buildings (optional, before hunting), then kill / intercept enemy F
        if self.p["defend"]:
            self.defend()
        self.hunt()
        if not self.in_endgame():
            self.hunt_far()
        # 5) garrison owned buildings, then leftover W: convoy with F, otherwise head for the best target
        self.garrison()
        self.rally(claimed)

    def in_endgame(self):
        return self.p["endgame"] > 0 and self.turn > T_TOTAL - self.p["endgame"]

    def too_late(self, eta):
        """A flag eta steps away captures (or neutralizes) on turn + eta - 1; v6 kept a 2-turn margin."""
        if self.in_endgame():
            return self.turn + eta - 1 > T_TOTAL
        return self.turn + eta + 1 > T_TOTAL

    def defend(self):
        """Threat-proportional defence, before hunting.

        A building I own is threatened when an enemy flag can stand on it within defend_eta turns. The flag
        arrives with whatever enemy W can reach the building by then; I need one more W than that ON the building
        (W cancel 1:1, a surviving W wipes the flags). Only W that can arrive in time are used, most valuable
        buildings first (HALL income / ENG discount count via bval). If the defence cannot be made, nothing is
        sent: a trickle would only be killed; the building is retaken later (it becomes a capture target).
        """
        R = self.p["defend_eta"]
        efc = [i for i in range(N) if self.eF[i]]
        if not efc:
            return
        cells = [i for i in self.bcells if self.own[i] == "M" and self.stage[i] == 2]
        threats = []
        for i in cells:
            eta = min((self.D[k][i] for k in efc), default=INF)
            if eta > R:
                continue
            threats.append((-self.bval(i), eta, i))
        threats.sort()
        for _, eta, i in threats:
            # enemy W that can be on i when the flag arrives (they move one step per turn, like the flag)
            need = self.ew_r(i, max(1, eta)) + 1
            have = self.remW[i]
            srcs = sorted((j for j in range(N) if j != i and self.remW[j] and self.D[j][i] <= max(1, eta)),
                          key=lambda j: (self.D[j][i], j))
            if have + sum(self.remW[j] for j in srcs) < need:
                continue
            stay = min(have, need)
            self.move(i, "W", stay, i)
            left = need - stay
            for j in srcs:
                if left <= 0:
                    break
                take = min(self.remW[j], left)
                self.move(j, "W", take, self.step_toward(j, i))
                left -= take

    def safest(self, c):
        """Stay or step to the neighbour with the smallest uncovered enemy-W exposure."""
        best = None
        for j in self.near[c]:
            k = (max(0, self.eW1[j] - self.capw(j)), 0 if j == c else 1,
                 self.D[j][self.base])
            if best is None or k < best[0]:
                best = (k, j)
        return best[1]

    def predict(self, h):
        """Where an enemy F group at h will most likely be next turn, and its destination."""
        if h in self.btype and not (self.own[h] == "E" and self.stage[h] == 2):
            return h, h
        best = None
        for i in self.bcells:
            if self.own[i] == "E" and self.stage[i] == 2:
                continue
            d = self.D[h][i]
            if d < INF and (best is None or (d, -self.bval(i), i) < best[0]):
                best = ((d, -self.bval(i), i), i)
        if best is None:
            return h, h
        return self.step_toward_plain(h, best[1]), best[1]

    def step_toward_plain(self, c, t):
        for j, _ in self.nb[c]:
            if self.D[j][t] == self.D[c][t] - 1:
                return j
        return c

    def hunt(self):
        groups = []
        for h in range(N):
            if self.eF[h]:
                p, t = self.predict(h)
                mine = self.own[t] != "E" if t in self.btype else False
                val = 5 * self.eF[h] + (self.sc(t) * 2 if mine else 0)
                groups.append((-val, h, p, t))
        groups.sort()
        for _, h, p, t in groups:
            esc_e = self.ew_r(h, 2)
            need = self.eW1[p] + 1 if self.eW1[p] else 1
            need = max(need, esc_e + 1) if esc_e else need
            for pt, d_e in ((p, 1), (t, self.D[h][t])):
                if pt == t and t == p:
                    d_e = 1
                supply = sum(self.remW[j] for j in range(N)
                             if self.remW[j] and self.D[j][pt] <= d_e)
                if supply < need:
                    continue
                left = need + self.p["slack_w"]
                srcs = sorted((j for j in range(N) if self.remW[j] and self.D[j][pt] <= d_e),
                              key=lambda j: (self.D[j][pt], j))
                for j in srcs:
                    if left <= 0:
                        break
                    take = min(self.remW[j], left)
                    nxt = self.step_toward(j, pt)
                    self.move(j, "W", take, nxt)
                    left -= take
                break

    def hunt_far(self):
        """Chase enemy F that are up to hunt_r steps away when the W in reach beat their escort."""
        R = self.p["hunt_r"]
        if R <= 1:
            return
        groups = []
        for h in range(N):
            if self.eF[h]:
                p, t = self.predict(h)
                val = 5 * self.eF[h] + (self.sc(t) * 2 if t in self.btype and self.own[t] != "E" else 0)
                groups.append((-val, h))
        groups.sort()
        for _, h in groups:
            need = self.ew_r(h, 2) + 1
            srcs = sorted((j for j in range(N) if self.remW[j] and self.D[j][h] <= R),
                          key=lambda j: (self.D[j][h], j))
            if sum(self.remW[j] for j in srcs) < need:
                continue
            left = need + self.p["slack_w"]
            for j in srcs:
                if left <= 0:
                    break
                take = min(self.remW[j], left)
                self.move(j, "W", take, self.step_toward(j, h))
                left -= take

    def garrison(self):
        """Keep g W standing on each owned building (g+alert when enemy F/W are close): a lone raiding F dies on arrival."""
        g0 = self.p["garrison"]
        if g0 <= 0:
            return
        cells = [i for i in self.bcells if self.own[i] == "M" and self.stage[i] == 2]
        efc = [i for i in range(N) if self.eF[i]]
        order = sorted(cells, key=lambda i: (-self.bval(i), i))
        for i in order:
            want = g0
            if self.p["garrison_alert"] and (any(self.D[k][i] <= 6 for k in efc) or self.ew_r(i, 4) > 0):
                want += self.p["garrison_alert"]
            stay = min(self.remW[i], want)
            self.move(i, "W", stay, i)
            deficit = want - stay
            if deficit <= 0:
                continue
            for j in sorted((j for j in range(N) if self.remW[j] and self.D[j][i] <= self.p["garrison_radius"]),
                            key=lambda j: (self.D[j][i], j)):
                if deficit <= 0:
                    break
                take = min(self.remW[j], deficit)
                self.move(j, "W", take, self.step_toward(j, i))
                deficit -= take

    def best_target(self, c, pool):
        best = None
        for i in self.bcells:
            if not self.capturable(i):
                continue
            eta = self.D[c][i]
            if eta >= INF or eta == 0 or self.too_late(eta):
                continue
            if self.ew_r(i, min(eta, self.p["pool_radius"])) > pool:
                continue
            v = self.bval(i) / (eta + 1.5)
            if best is None or (-v, i) < best[0]:
                best = ((-v, i), i)
        return best[1] if best else None

    def rally(self, claimed):
        # convoy: W left on a cell where F just moved out follow the highest-value F move
        fdest = {}
        for (c, kind, j), n in sorted(self.moves.items()):
            if kind != "F":
                continue
            cur = fdest.get(c)
            if j in self.btype and (cur not in self.btype or self.bval(j) > self.bval(cur)):
                fdest[c] = j
            elif cur is None:
                fdest[c] = j
        for c in range(N):
            w = self.remW[c]
            if not w:
                continue
            dest = None
            if c in fdest and self.eW1[fdest[c]] <= w + self.arrW[fdest[c]]:
                dest = fdest[c]
            else:
                pool = self.myw_r(c, self.p["pool_radius"]) + 0
                tgt = self.best_target(c, pool)
                if tgt is not None:
                    dest = self.step_toward(c, tgt)
                    if self.eW1[dest] > w + self.arrW[dest]:
                        dest = None
            if dest is None or dest == c:
                self.move(c, "W", w, c)
            else:
                self.move(c, "W", w, dest)
