"""For each flip of a Y building in official replays: k turns before the flip (k = 1..5), the distance of the
nearest enemy flag to the building (BFS on the map), and the Y and K warriors within k steps of the building
(= what could arrive in time). Answers: when was the threat visible, and could Y have out-numbered K at the cell?

  python "out/experiments/8-round-0929-2200(opus)/flip_lead.py" <replays...>
"""
import glob, json, os, sys
from collections import deque, defaultdict


def bfs(rows, s):
    H, W = len(rows), len(rows[0])
    d = {s: 0}
    q = deque([s])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if 0 <= p[0] < W and 0 <= p[1] < H and rows[p[1]][p[0]] != "#" and p not in d:
                d[p] = d[(x, y)] + 1
                q.append(p)
    return d


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    agg = defaultdict(lambda: [0, 0, 0, 0])   # k -> [n, flag visible within 2k, Y>=K+1 within k, sum]
    rows_out = []
    for f in sorted(x for p in sys.argv[1:] for x in glob.glob(p)):
        g = json.load(open(f, encoding="utf-8"))
        T = g["turns"]
        obs = [t["observation"] for t in T]
        rows = obs[0]["map"]
        dist = {}
        for t in range(6, len(obs)):
            pb = {b["id"]: b["owner"] for b in obs[t - 1]["buildings"]}
            for b in obs[t]["buildings"]:
                if not (pb[b["id"]] == "Y" and b["owner"] != "Y") or t > 80:
                    continue
                c = (b["x"], b["y"])
                if c not in dist:
                    dist[c] = bfs(rows, c)
                D = dist[c]
                line = []
                for k in range(1, 6):
                    o = obs[t - k]
                    fd = min((D.get((u[2], u[3]), 99) for u in o["units"] if u[0] == "K" and u[1] == "F"), default=99)
                    yw = sum(u[4] for u in o["units"] if u[0] == "Y" and u[1] == "W" and D.get((u[2], u[3]), 99) <= k)
                    kw = sum(u[4] for u in o["units"] if u[0] == "K" and u[1] == "W" and D.get((u[2], u[3]), 99) <= k)
                    a = agg[k]
                    a[0] += 1
                    a[1] += fd <= k
                    a[2] += yw > kw
                    line.append(f"k{k}: F@{fd} Y{yw}/K{kw}")
                rows_out.append(f"{os.path.basename(f)[:10]} T{t} {b['type'][:4]} " + "  ".join(line))
    for r in rows_out[:40]:
        print(r)
    print(f"... {len(rows_out)} flips (T<=80)")
    for k in range(1, 6):
        n, vis, sup, _ = agg[k]
        print(f"k={k} turns before: enemy flag within k steps {vis / n:.0%}; Y W within k steps > K W within k steps {sup / n:.0%}")


if __name__ == "__main__":
    main()
