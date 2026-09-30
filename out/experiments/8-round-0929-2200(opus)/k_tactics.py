"""Observable K-side tactics in the official replays (public observations only; no claim about K's code).

  python "out/experiments/8-round-0929-2200(opus)/k_tactics.py" out/official-replays/[0-9][0-9]_*.json

Per game (and pooled by outcome) for the opponent K:
- W / F / S counts at T5, T10, T20; W spawned per turn T1-10 (base cell growth), turn of first K W;
- escort: share of K flag-cells that have >= 1 K W on the same cell / within 1 step, and mean escort size;
- capture events by K on buildings Y owned the turn before (flips): K W on the cell at that moment;
- W dispersion: number of K W stacks and largest stack share at T20;
- forward production: K W appearing on an owned HOSPITAL; TELE-like jumps (unit on a STATION far from last turn).
"""
import glob, json, sys
from collections import defaultdict


def cnt(units, team, kind):
    return sum(u[4] for u in units if u[0] == team and u[1] == kind)


def cells(units, team, kind):
    return {(u[2], u[3]): u[4] for u in units if u[0] == team and u[1] == kind}


def game(path):
    g = json.load(open(path, encoding="utf-8"))
    T = g["turns"]
    obs = [t["observation"] for t in T]
    r = {"file": path.split("\\")[-1].split("/")[-1][:30], "win": g["result"]["winner"] == "Y", "end": T[-1]["turn"]}
    rows = obs[0]["map"]
    hs = sorted((x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch == "H")
    kb = hs[1] if hs[0][0] <= 4 else hs[0]
    for t in (5, 10, 20):
        if t < len(obs):
            r[f"K{t}"] = (cnt(obs[t]["units"], "K", "W"), cnt(obs[t]["units"], "K", "F"), cnt(obs[t]["units"], "K", "S"))
            r[f"Y{t}"] = (cnt(obs[t]["units"], "Y", "W"), cnt(obs[t]["units"], "Y", "F"))
    r["firstKW"] = next((t for t in range(1, len(obs)) if cnt(obs[t]["units"], "K", "W") > 0), None)
    # escort of K flags, turns 1..min(end,60)
    same = near = tot = 0
    esc = []
    for t in range(1, min(len(obs), 61)):
        kw = cells(obs[t]["units"], "K", "W")
        for (x, y), n in cells(obs[t]["units"], "K", "F").items():
            if (x, y) == kb:
                continue
            tot += 1
            w0 = kw.get((x, y), 0)
            w1 = w0 + sum(kw.get((x + dx, y + dy), 0) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            same += w0 > 0
            near += w1 > 0
            esc.append(w1)
    r["esc_same"] = same / tot if tot else None
    r["esc_near"] = near / tot if tot else None
    r["esc_mean"] = sum(esc) / len(esc) if esc else None
    # flips of Y buildings: K W on the building cell in the flip turn
    flips = []
    for t in range(1, len(obs)):
        pb = {b["id"]: b["owner"] for b in obs[t - 1]["buildings"]}
        kw = cells(obs[t]["units"], "K", "W")
        for b in obs[t]["buildings"]:
            if pb[b["id"]] == "Y" and b["owner"] != "Y":
                flips.append((t, kw.get((b["x"], b["y"]), 0)))
    r["flips"] = len(flips)
    r["flips_escorted"] = sum(1 for _, w in flips if w > 0)
    r["flip_w_mean"] = sum(w for _, w in flips) / len(flips) if flips else None
    r["first_flip"] = flips[0][0] if flips else None
    if len(obs) > 20:
        st = sorted(cells(obs[20]["units"], "K", "W").values(), reverse=True)
        r["stacks20"] = len(st)
        r["top20"] = st[0] / sum(st) if st else 0
    hosp = {(b["x"], b["y"]) for b in obs[0]["buildings"] if b["type"] == "HOSPITAL"}
    fw = 0
    for t in range(1, len(obs)):
        prev = cells(obs[t - 1]["units"], "K", "W")
        for (x, y), n in cells(obs[t]["units"], "K", "W").items():
            if (x, y) in hosp and n > prev.get((x, y), 0) + sum(prev.get((x + dx, y + dy), 0) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                fw += 1
    r["hosp_spawn_turns"] = fw
    return r


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else float("nan")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rs = [game(f) for p in sys.argv[1:] for f in sorted(glob.glob(p))]
    for r in rs:
        print(f"{r['file']:<30} {'W' if r['win'] else 'L'} end{r['end']:>4} K10 W/F/S {r.get('K10')} K20 {r.get('K20')} firstKW T{r['firstKW']} "
              f"esc same/near {r['esc_same'] or 0:.2f}/{r['esc_near'] or 0:.2f} mean {r['esc_mean'] or 0:.1f} "
              f"flips {r['flips']} escorted {r['flips_escorted']} W@flip {r['flip_w_mean'] or 0:.1f} first T{r['first_flip']} "
              f"stacks20 {r.get('stacks20')} hosp {r['hosp_spawn_turns']}")
    for lab, sel in (("Y lost", [r for r in rs if not r["win"]]), ("Y won", [r for r in rs if r["win"]])):
        print(f"\n== {lab} (n={len(sel)})")
        for k in ("esc_same", "esc_near", "esc_mean", "flip_w_mean", "first_flip", "stacks20", "top20", "hosp_spawn_turns", "firstKW"):
            print(f"  {k:<18} {mean([r.get(k) for r in sel]):.2f}")
        for t in (5, 10, 20):
            print(f"  K W/F at T{t}: {mean([r[f'K{t}'][0] for r in sel if f'K{t}' in r]):.1f} / {mean([r[f'K{t}'][1] for r in sel if f'K{t}' in r]):.1f}"
                  f"   Y W/F: {mean([r[f'Y{t}'][0] for r in sel if f'Y{t}' in r]):.1f} / {mean([r[f'Y{t}'][1] for r in sel if f'Y{t}' in r]):.1f}")
        print(f"  flips escorted share: {sum(r['flips_escorted'] for r in sel)}/{sum(r['flips'] for r in sel)}")


if __name__ == "__main__":
    main()
