"""What did our warriors do while a building was about to flip? Official replays played by v6 code, replayed through the
v6 brain with every warrior move tagged by the rule that issued it (the brain reproduces every recorded turn, so the tags
are what happened, not a counterfactual).

  python "out/experiments/9-midgame-policy-search(opus)/w_orders.py" [--src out/v6-claude/source] out/official-replays/<48-59>_*.json

For each flip of a Y building in T11-140 (owner Y after turn t-1, not Y after turn t), at the three decisions before it
(turns t-2, t-1, t; each sees the state of the previous turn):
  in reach = Y W within 3 steps of the building; per issuing rule: how many, and whether they stepped closer / stayed / left.
At onset (state after turn t-3): nearest K flag, Y and K W within 3 steps, where all Y W stood, and the first radius k
at which Y's W within k outnumber K's (the time Y would need to gather a local majority).
"""
import argparse, glob, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools", "evaluation"))
import replay_commands as rc  # noqa: E402
from midgame_metrics import _bfs, frames, load  # noqa: E402

RULES = ("hunt", "hunt_far", "garrison", "rally", "escort", "defend")


def instrument(B):
    def tagged(name, fn):
        def w(self, *a, **k):
            prev = self._tag
            self._tag = name
            try:
                return fn(self, *a, **k)
            finally:
                self._tag = prev
        return w
    for n in (r for r in RULES if hasattr(B, r)):
        setattr(B, n, tagged(n, getattr(B, n)))
    mv, act = B.move, B.act

    def move(self, c, kind, n, j):
        if kind == "W" and n > 0:
            self._log.append((c, j, n, self._tag))
        return mv(self, c, kind, n, j)

    def act_(self, turn, *a):
        self._log, self._tag = [], "flag-phase"
        r = act(self, turn, *a)
        B.LOG[turn] = self._log
        return r
    B.move, B.act, B.LOG = move, act_, {}


def run_game(src, path):
    decide, cb = rc.load_decide(src)
    B = sys.modules["brain"].Brain
    instrument(B)
    g = load(path)
    T = g["turns"]
    init = cb.parse_init(rc.init_block(T[0]["observation"], "Y"))
    same = 0
    for i in range(1, len(T)):
        rec = (T[i].get("command") or {}).get("lines")
        view = cb.parse_turn(rc.turn_block(T[i]["turn"], T[i - 1]["observation"], T[i - 1].get("revealed"), "Y"), init)
        same += list(decide(view, init)) == rec
    return g, B.LOG, same, len(T) - 1


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="out/v6-claude/source")
    ap.add_argument("replays", nargs="+")
    a = ap.parse_args()
    files = sorted(x for p in a.replays for x in glob.glob(p))
    tags = defaultdict(Counter)          # rule -> {closer, stay, away}
    onset = Counter()
    where = Counter()
    gap = []                            # (k needed for Y majority) - (K flag distance)
    per_type = Counter()
    nflip = 0
    for f in files:
        g, LOG, same, n = run_game(a.src, f)
        if same != n:
            print(f"WARNING {os.path.basename(f)}: brain reproduces {same}/{n} turns; tags are not what happened")
        rows, bl, fr = frames(g)
        idx = {t: i for i, (t, _, _) in enumerate(fr)}
        dist = {}
        for i in range(4, len(fr)):
            t, _, own = fr[i]
            if not 11 <= t <= 140:
                continue
            for bid, (x, y, typ, pts) in bl.items():
                if not (fr[i - 1][2][bid] == "Y" and own[bid] != "Y"):
                    continue
                nflip += 1
                per_type[typ] += 1
                if (x, y) not in dist:
                    dist[(x, y)] = _bfs(rows, (x, y))
                D = dist[(x, y)]
                u0 = fr[i - 3][1]
                yw = [(D.get((u[2], u[3]), 99), u[4]) for u in u0 if u[0] == "Y" and u[1] == "W"]
                kw = [(D.get((u[2], u[3]), 99), u[4]) for u in u0 if u[0] == "K" and u[1] == "W"]
                fd = min((D.get((u[2], u[3]), 99) for u in u0 if u[0] == "K" and u[1] == "F"), default=99)
                onset["K flag within 3"] += fd <= 3
                onset["Y W on building"] += sum(n for d, n in yw if d == 0) > 0
                ys3, ks3 = sum(n for d, n in yw if d <= 3), sum(n for d, n in kw if d <= 3)
                onset["Y W<=3 > K W<=3"] += ys3 > ks3
                tot = sum(n for _, n in yw) or 1
                for lo, hi, name in ((0, 3, "<=3"), (4, 6, "4-6"), (7, 10, "7-10"), (11, 99, ">10")):
                    where[name] += sum(n for d, n in yw if lo <= d <= hi) / tot
                k_need = next((k for k in range(0, 30) if sum(n for d, n in yw if d <= k) > sum(n for d, n in kw if d <= k)), 30)
                gap.append((k_need, fd))
                for tt in (t - 2, t - 1, t):
                    for c, j, n, tag in LOG.get(tt, []):
                        cx, cy, jx, jy = c % 15, c // 15, j % 15, j // 15
                        d0, d1 = D.get((cx, cy), 99), D.get((jx, jy), 99)
                        if d0 > 3:
                            continue
                        tags[tag]["closer" if d1 < d0 else "stay" if d1 == d0 else "away"] += n
    print(f"games {len(files)}, flips of Y buildings T11-140: {nflip}  by type {dict(per_type.most_common())}")
    print("at onset (3 turns before):", ", ".join(f"{k} {v / nflip:.0%}" for k, v in onset.items()))
    print("where all Y W stood at onset (mean share by steps to the building):", ", ".join(f"{k} {v / nflip:.0%}" for k, v in where.items()))
    late = sum(1 for k, fd in gap if k > fd)
    print(f"Y majority radius vs K flag distance at onset: majority radius > flag distance in {late / len(gap):.0%} "
          f"(median radius {sorted(k for k, _ in gap)[len(gap) // 2]}, median flag distance {sorted(fd for _, fd in gap)[len(gap) // 2]})")
    allw = sum(sum(c.values()) for c in tags.values()) or 1
    print("orders given to the Y W within 3 steps, over the 3 decisions before each flip (W-moves):")
    for tag, c in sorted(tags.items(), key=lambda kv: -sum(kv[1].values())):
        s = sum(c.values())
        print(f"  {tag:<11} {s:>6} ({s / allw:4.0%})  closer {c['closer'] / s:4.0%}  stay {c['stay'] / s:4.0%}  away {c['away'] / s:4.0%}")


if __name__ == "__main__":
    main()
