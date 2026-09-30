"""Loss-mechanism diagnostics of official replays (Y side = us). Observations only; nothing about K's code.

  python "out/experiments/8-round-0929-2200(opus)/round_diag.py" [--detail] <replays...>

Facts used (rulebook): warriors cancel 1:1, so both sides lose exactly the same number of W in combat; flags die only
in combat; income = 10 + 2 per HALL owned (cap 40); ENG makes W cost 2; DEPOT +15 on first capture.
Per game:
  units/buildings/true score at T10, T20, T40; key building types (HALL, ENG, HOSPITAL, DEPOT, PLAZA) owned;
  economy T1-40 per side: hall-turns, ENG-turns, depot bonuses, stock left at the cap (waste);
  Y: W and F bought, F lost, stock spent on flags that died;
  flips of Y buildings: K W on the cell at the flip, Y W on the cell / within 2 steps one turn before, recaptured later;
  first irreversible disadvantage = first turn after which Y's true score stays below K's until the end.
"""
import argparse, glob, json, os, sys
from collections import Counter, defaultdict

KEY = ("HALL", "ENG", "HOSPITAL", "DEPOT", "PLAZA")


def cnt(units, team, kind):
    return sum(u[4] for u in units if u[0] == team and u[1] == kind)


def cellmap(units, team, kind):
    d = {}
    for u in units:
        if u[0] == team and u[1] == kind:
            d[(u[2], u[3])] = d.get((u[2], u[3]), 0) + u[4]
    return d


def true_scores(g):
    """Scores revealed to Y anywhere in the game, completed by point symmetry (pairs have equal scores)."""
    T = g["turns"]
    bl = {b["id"]: b for b in T[0]["observation"]["buildings"]}
    sc = {}
    for t in T:
        for k, v in ((t.get("revealed") or {}).get("buildingScores") or {}).items():
            sc[int(k)] = v
    pos = {(b["x"], b["y"]): i for i, b in bl.items()}
    for i, b in bl.items():
        if i not in sc:
            j = pos.get((14 - b["x"], 14 - b["y"]))
            if j in sc:
                sc[i] = sc[j]
            elif b["type"] == "PLAZA":
                sc[i] = 3
    return sc, bl


def spawns(lines, stock, wc):
    """W and F actually bought (engine order: spawn lines in order, each limited by the remaining stock)."""
    f = w = 0
    hosp = 0
    for ln in lines:
        tk = ln.split()
        if tk and tk[0] == "SPAWN" and len(tk) in (3, 5):
            k, n = tk[1], int(tk[2])
            c = 5 if k == "F" else wc if k == "W" else 2
            got = min(n, stock // c)
            stock -= got * c
            if k == "F":
                f += got
            elif k == "W":
                w += got
            if len(tk) == 5:
                hosp += got
    return f, w, hosp


def game(path, detail=False):
    g = json.load(open(path, encoding="utf-8"))
    T = g["turns"]
    obs = [t["observation"] for t in T]
    end = len(obs) - 1
    sc, bl = true_scores(g)
    unknown = [i for i in bl if i not in sc]
    r = {"file": os.path.basename(path)[:-5], "win": g["result"]["winner"] == "Y", "reason": g["result"]["reason"], "end": T[-1]["turn"],
         "unknown_scores": len(unknown)}

    def own(t, s):
        return [b for b in obs[t]["buildings"] if b["owner"] == s]

    def score(t, s):
        return sum(sc.get(b["id"], 0) for b in own(t, s))
    traj = [(score(t, "Y"), score(t, "K")) for t in range(len(obs))]
    r["traj"] = traj
    for t in (10, 20, 40):
        tt = min(t, end)
        o = obs[tt]
        r[f"T{t}"] = {
            "W": (cnt(o["units"], "Y", "W"), cnt(o["units"], "K", "W")),
            "F": (cnt(o["units"], "Y", "F"), cnt(o["units"], "K", "F")),
            "bld": (len(own(tt, "Y")), len(own(tt, "K"))),
            "score": traj[tt],
            "key": {k: (sum(1 for b in own(tt, "Y") if b["type"] == k), sum(1 for b in own(tt, "K") if b["type"] == k)) for k in KEY},
            "res": (o["resources"]["Y"], o["resources"]["K"]),
        }
    # first irreversible disadvantage (score)
    fid = None
    for t in range(1, len(traj)):
        if all(traj[u][0] < traj[u][1] for u in range(t, len(traj))):
            fid = t
            break
    r["first_irrev"] = fid
    # first turn after which Y's W stays below K's W until the end (or T40)
    wtraj = [(cnt(o["units"], "Y", "W"), cnt(o["units"], "K", "W")) for o in obs]
    r["w_behind_from"] = next((t for t in range(1, len(wtraj)) if all(wtraj[u][0] < wtraj[u][1] for u in range(t, min(len(wtraj), 60)))), None)
    # economy T1..40 (and whole game) for both sides
    eco = {s: Counter() for s in "YK"}
    fl_y = 0
    wbuy = fbuy = hosp = 0
    for t in range(1, len(obs)):
        p, o = obs[t - 1], obs[t]
        ph = "e" if t <= 40 else "l"
        for s in "YK":
            halls = sum(1 for b in p["buildings"] if b["owner"] == s and b["type"] == "HALL")
            engs = sum(1 for b in p["buildings"] if b["owner"] == s and b["type"] == "ENG")
            eco[s][ph + "hall_turns"] += halls
            eco[s][ph + "eng_turns"] += engs > 0
            eco[s][ph + "capped"] += o["resources"][s] >= 40
        for e in o["events"]:
            if e.get("kind") == "capture" and e.get("team") in "YK":
                if bl[e["buildingId"]]["type"] == "DEPOT":
                    eco[e["team"]][ph + "depot_caps"] += 1
                eco[e["team"]][ph + "captures"] += 1
            if e.get("kind") == "neutral" and e.get("team") in "YK":
                eco[e["team"]][ph + "neutralize"] += 1
        yeng = sum(1 for b in p["buildings"] if b["owner"] == "Y" and b["type"] == "ENG")
        f, w, h = spawns((T[t].get("command") or {}).get("lines", []), p["resources"]["Y"], max(2, 3 - yeng))
        fl = max(0, cnt(p["units"], "Y", "F") + f - cnt(o["units"], "Y", "F"))
        if t <= 40:
            fbuy += f; wbuy += w; hosp += h; fl_y += fl
        eco["Y"][ph + "F_lost"] += fl
        eco["Y"][ph + "F_bought"] += f
        eco["Y"][ph + "W_bought"] += w
    r["eco"] = {s: dict(v) for s, v in eco.items()}
    r["y_T40"] = {"F_bought": fbuy, "W_bought": wbuy, "F_lost": fl_y, "hosp_spawned": hosp, "stock_on_dead_F": 5 * fl_y}
    # flips of Y buildings
    flips = []
    for t in range(1, len(obs)):
        p, o = obs[t - 1], obs[t]
        pb = {b["id"]: b["owner"] for b in p["buildings"]}
        kw = cellmap(o["units"], "K", "W")
        yw_prev = cellmap(p["units"], "Y", "W")
        kw_prev = cellmap(p["units"], "K", "W")
        for b in o["buildings"]:
            if pb[b["id"]] == "Y" and b["owner"] != "Y":
                c = (b["x"], b["y"])
                ev = {e["kind"] for e in o["events"] if e.get("buildingId") == b["id"]}
                near = lambda m, r_: sum(n for q, n in m.items() if abs(q[0] - c[0]) + abs(q[1] - c[1]) <= r_)
                rec = next((u for u in range(t + 1, len(obs)) if next(bb for bb in obs[u]["buildings"] if bb["id"] == b["id"])["owner"] == "Y"), None)
                flips.append({"t": t, "type": b["type"], "score": sc.get(b["id"]), "cause": "pulled" if "pulled" in ev else "flag",
                              "kw_on": kw.get(c, 0), "kw_near_before": near(kw_prev, 2), "yw_on_before": yw_prev.get(c, 0),
                              "yw_near_before": near(yw_prev, 2), "recaptured_at": rec})
    r["flips"] = flips
    if detail:
        r["timeline"] = [(t, traj[t], wtraj[t], cnt(obs[t]["units"], "Y", "F"), cnt(obs[t]["units"], "K", "F"),
                          len(own(t, "Y")), len(own(t, "K")), obs[t]["resources"]["Y"], obs[t]["resources"]["K"]) for t in range(len(obs))]
    return r


def fmt_key(k):
    return " ".join(f"{t[:3]}{a}:{b}" for t, (a, b) in k.items())


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--detail", action="store_true")
    ap.add_argument("--json", default=None)
    ap.add_argument("replays", nargs="+")
    a = ap.parse_args()
    rs = [game(f, a.detail) for p in a.replays for f in sorted(glob.glob(p))]
    for r in rs:
        print(f"\n### {r['file']}  {'WIN' if r['win'] else 'LOSS'} {r['reason']} end T{r['end']}  first irreversible score deficit: T{r['first_irrev']}  "
              f"W behind (to T60) from: T{r['w_behind_from']}  unknown scores: {r['unknown_scores']}")
        for t in (10, 20, 40):
            s = r[f"T{t}"]
            print(f"  T{t}: score {s['score'][0]}:{s['score'][1]} bld {s['bld'][0]}:{s['bld'][1]} W {s['W'][0]}:{s['W'][1]} F {s['F'][0]}:{s['F'][1]} "
                  f"res {s['res'][0]}:{s['res'][1]} | {fmt_key(s['key'])}")
        ey, ek = r["eco"]["Y"], r["eco"]["K"]
        print(f"  T1-40 economy Y|K: hall-turns {ey.get('ehall_turns', 0)}|{ek.get('ehall_turns', 0)}  ENG-turns {ey.get('eeng_turns', 0)}|{ek.get('eeng_turns', 0)}  "
              f"depot caps {ey.get('edepot_caps', 0)}|{ek.get('edepot_caps', 0)}  captures {ey.get('ecaptures', 0)}|{ek.get('ecaptures', 0)}  "
              f"neutralize {ey.get('eneutralize', 0)}|{ek.get('eneutralize', 0)}  capped {ey.get('ecapped', 0)}|{ek.get('ecapped', 0)}")
        y = r["y_T40"]
        print(f"  Y T1-40 bought F {y['F_bought']} W {y['W_bought']} (hospital {y['hosp_spawned']}), F lost {y['F_lost']} = {y['stock_on_dead_F']} stock; "
              f"whole game F lost {ey.get('eF_lost', 0) + ey.get('lF_lost', 0)}")
        fl = r["flips"]
        if fl:
            early = [f for f in fl if f["t"] <= 60]
            print(f"  Y buildings lost: {len(fl)} ({len(early)} by T60); escorted (K W on cell) {sum(f['kw_on'] > 0 for f in fl)}; "
                  f"Y garrison before 0/1/2+: {sum(f['yw_on_before'] == 0 for f in fl)}/{sum(f['yw_on_before'] == 1 for f in fl)}/{sum(f['yw_on_before'] >= 2 for f in fl)}; "
                  f"recaptured {sum(f['recaptured_at'] is not None for f in fl)}")
            ty = Counter(f["type"] for f in early)
            print(f"  lost by T60 by type: {dict(ty)}; first 6: " + ", ".join(f"T{f['t']} {f['type'][:4]}{f['score']} kw{f['kw_on']} yw{f['yw_on_before']}/{f['yw_near_before']} kn{f['kw_near_before']} rec{f['recaptured_at']}" for f in fl[:6]))
    # pooled
    for lab, sel in (("LOSSES", [r for r in rs if not r["win"]]), ("WINS", [r for r in rs if r["win"]])):
        if not sel:
            continue
        n = len(sel)
        m = lambda f: sum(f(r) for r in sel) / n
        print(f"\n== {lab} n={n}")
        for t in (10, 20, 40):
            print(f"  T{t}: W {m(lambda r: r[f'T{t}']['W'][0]):.1f}:{m(lambda r: r[f'T{t}']['W'][1]):.1f}  F {m(lambda r: r[f'T{t}']['F'][0]):.1f}:{m(lambda r: r[f'T{t}']['F'][1]):.1f}  "
                  f"bld {m(lambda r: r[f'T{t}']['bld'][0]):.1f}:{m(lambda r: r[f'T{t}']['bld'][1]):.1f}  score {m(lambda r: r[f'T{t}']['score'][0]):.1f}:{m(lambda r: r[f'T{t}']['score'][1]):.1f}  "
                  + " ".join(f"{k[:3]} {m(lambda r: r[f'T{t}']['key'][k][0]):.1f}:{m(lambda r: r[f'T{t}']['key'][k][1]):.1f}" for k in KEY))
        for k in ("ehall_turns", "eeng_turns", "edepot_caps", "ecaptures", "eneutralize"):
            print(f"  T1-40 {k[1:]:<12} Y {m(lambda r: r['eco']['Y'].get(k, 0)):.1f}  K {m(lambda r: r['eco']['K'].get(k, 0)):.1f}")
        print(f"  Y T1-40 F bought {m(lambda r: r['y_T40']['F_bought']):.1f}, F lost {m(lambda r: r['y_T40']['F_lost']):.1f}, W bought {m(lambda r: r['y_T40']['W_bought']):.1f}")
        fl = [f for r in sel for f in r["flips"] if f["t"] <= 60]
        if fl:
            print(f"  flips by T60: {len(fl) / n:.1f}/game; escorted {sum(f['kw_on'] > 0 for f in fl) / len(fl):.0%} (mean K W on cell {sum(f['kw_on'] for f in fl) / len(fl):.1f}); "
                  f"Y W on cell before 0/1/2+: {sum(f['yw_on_before'] == 0 for f in fl)}/{sum(f['yw_on_before'] == 1 for f in fl)}/{sum(f['yw_on_before'] >= 2 for f in fl)}; "
                  f"Y W within 2 before mean {sum(f['yw_near_before'] for f in fl) / len(fl):.1f} vs K W within 2 before {sum(f['kw_near_before'] for f in fl) / len(fl):.1f}; "
                  f"recaptured {sum(f['recaptured_at'] is not None for f in fl) / len(fl):.0%}; by type {dict(Counter(f['type'] for f in fl))}")
        print(f"  first irreversible score deficit: {[r['first_irrev'] for r in sel]}")
        print(f"  W behind from: {[r['w_behind_from'] for r in sel]}")
    if a.json:
        json.dump(rs, open(a.json, "w", encoding="utf-8"), ensure_ascii=False)


if __name__ == "__main__":
    main()
