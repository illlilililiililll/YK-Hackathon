"""Midgame building-control metrics, the same for local replays (engine format) and official replays (site format).

  python out/tools/evaluation/midgame_metrics.py <replay.json[.gz] ...>      # one line per game, side = Y / the side named in the file

Window T11-140 (after the opening, before the 20-turn endgame of v6-endgame20). For each side s:
  flips          turns on which a building s owned the turn before is no longer s's
  flips_bare     ... with no s warrior on that building the turn before
  flips_val      ... of a HALL or ENG (production buildings) or a building worth >= 3 points
  sup1/sup3      ... where s had more warriors than the enemy within 1 / 3 steps of the building, 1 / 3 turns before
  lost_st        score-turns lost to flips: points x turns until s owns the building again (or the window / game ends)
  score_turns    sum over window turns of the points s owns (control of valuable buildings)
  hall_t/eng_t   turns s owned a HALL / ENG (summed over buildings)
decisive = first turn after which s's true score stays below the enemy's until the end (None = never behind at the end).
"""
import gzip, json, sys
from collections import deque

LO, HI = 11, 140


def _bfs(rows, s):
    d = {s: 0}
    q = deque([s])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if 0 <= p[0] < 15 and 0 <= p[1] < 15 and rows[p[1]][p[0]] != "#" and p not in d:
                d[p] = d[(x, y)] + 1
                q.append(p)
    return d


def frames(g):
    """-> rows, {id: (x, y, type, score)}, [(turn, units, {id: owner})] for local or official replays."""
    if "map" in g and "terrain" in g["map"]:                       # local engine replay (true scores in the map)
        rows = ["".join(r) if not isinstance(r, str) else r for r in g["map"]["terrain"]]
        bl = {b["id"]: (b["x"], b["y"], b["type"], b["score"]) for b in g["map"]["buildings"]}
        fr = [(t["turn"], t["state"]["units"], {b["id"]: b["owner"] for b in t["state"]["buildings"]}) for t in g["turns"]]
        return rows, bl, fr
    T = g["turns"]                                                 # official: revealed scores + point symmetry
    obs0 = T[0]["observation"]
    sc = {}
    for t in T:
        for b in t["observation"]["buildings"]:
            if b.get("score", -1) >= 0:
                sc[b["id"]] = b["score"]
        for k, v in ((t.get("revealed") or {}).get("buildingScores") or {}).items():
            sc[int(k)] = v
    pos = {(b["x"], b["y"]): b["id"] for b in obs0["buildings"]}
    bl = {}
    for b in obs0["buildings"]:
        s = sc.get(b["id"], sc.get(pos.get((14 - b["x"], 14 - b["y"])), 3 if b["type"] == "PLAZA" else 2))
        bl[b["id"]] = (b["x"], b["y"], b["type"], s)
    fr = [(t["turn"], t["observation"]["units"], {b["id"]: b["owner"] for b in t["observation"]["buildings"]}) for t in T]
    return obs0["map"], bl, fr


def metrics(g):
    rows, bl, fr = frames(g)
    dist = {}
    out = {}
    wcell = []
    for _, units, _ in fr:
        m = {"Y": {}, "K": {}}
        for tm, k, x, y, n in units:
            if k == "W":
                m[tm][(x, y)] = m[tm].get((x, y), 0) + n
        wcell.append(m)
    idx = {t: i for i, (t, _, _) in enumerate(fr)}
    for s, e in (("Y", "K"), ("K", "Y")):
        r = dict(flips=0, flips_bare=0, flips_val=0, sup1=0, sup3=0, lost_st=0, score_turns=0, hall_t=0, eng_t=0)
        for i in range(1, len(fr)):
            t, _, own = fr[i]
            if not LO <= t <= HI:
                continue
            prev = fr[i - 1][2]
            for bid, (x, y, typ, pts) in bl.items():
                if own[bid] == s:
                    r["score_turns"] += pts
                    r["hall_t"] += typ == "HALL"
                    r["eng_t"] += typ == "ENG"
                if prev[bid] == s and own[bid] != s:
                    r["flips"] += 1
                    r["flips_bare"] += wcell[i - 1][s].get((x, y), 0) == 0
                    r["flips_val"] += typ in ("HALL", "ENG") or pts >= 3
                    if (x, y) not in dist:
                        dist[(x, y)] = _bfs(rows, (x, y))
                    D = dist[(x, y)]
                    for k, key in ((1, "sup1"), (3, "sup3")):
                        j = max(0, i - k)
                        mine = sum(n for c, n in wcell[j][s].items() if D.get(c, 99) <= k)
                        theirs = sum(n for c, n in wcell[j][e].items() if D.get(c, 99) <= k)
                        r[key] += mine > theirs
                    back = next((fr[j][0] for j in range(i + 1, len(fr)) if fr[j][2][bid] == s), None)
                    end = min(HI, fr[-1][0]) + 1
                    r["lost_st"] += pts * (min(back if back is not None else end, end) - t)
        tot = {tm: [sum(bl[b][3] for b, o in own.items() if o == tm) for _, _, own in fr] for tm in "YK"}
        dec = None
        for i in range(len(fr) - 1, -1, -1):
            if tot[s][i] >= tot[e][i]:
                break
            dec = fr[i][0]
        r["decisive"] = dec
        out[s] = r
    return out


def load(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for p in sys.argv[1:]:
        g = load(p)
        side = g.get("side") or ("K" if "-K-vs-" in p else "Y")
        print(p.replace("\\", "/").split("/")[-1][:44], side, metrics(g)[side])
