"""Independent re-analysis of the official Y-side replays (raw JSON only; does not use earlier reports).

  python out/tools/reporting/official_macro_analysis.py out/official-replays [--out out/experiments/7-independent-agent(v6)/phase2-analysis/official]

Version attribution: by Y's peak F count in turns 1-15 (v2 caps F at 12, v3 at 6). evaluationId is a
UUIDv7 but its time is the evaluation-slot time, NOT the submit time (games 20-35 are stamped 08:00 KST
28 Sep, before v3 was submitted at 11:24), so it is printed only as a caution and never used to pick a version.
"""
import argparse, datetime as dt, glob, json, os, re, sys
from collections import Counter, defaultdict

V3_SUBMIT_UTC = dt.datetime(2026, 9, 28, 2, 24, tzinfo=dt.timezone.utc)
W_COST, F_COST = 3, 5


def uuid7_time(u):
    ms = int(u.replace("-", "")[:12], 16)
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc)


def counts(units, team):
    c = {"F": 0, "W": 0, "S": 0}
    for t, k, x, y, n in units:
        if t == team:
            c[k] += n
    return c


def stacks(units, team, kind="W"):
    cells = sorted((n for t, k, x, y, n in units if t == team and k == kind), reverse=True)
    tot = sum(cells)
    return {"total": tot, "cells": len(cells), "top1": cells[0] / tot if tot else 0,
            "top3": sum(cells[:3]) / tot if tot else 0}


def analyze(path):
    g = json.load(open(path, encoding="utf-8"))
    T = g["turns"]
    name = os.path.basename(path)
    idx = int(name[:2])
    opp = re.sub(r"^\d+_|_[0-9a-f]{8}\.json$", "", name)
    ts = uuid7_time(g["evaluationId"])
    obs = [t["observation"] for t in T]
    bt = {b["id"]: b for b in obs[0]["buildings"]}
    fpeak = max(counts(o["units"], "Y")["F"] for o in obs[:16])
    res = {"idx": idx, "opp": opp, "file": name, "game": g["gameId"][-12:], "eval_utc": ts.isoformat(timespec="minutes"),
           "ver": "v2" if fpeak >= 8 else "v3", "side": g["side"], "winner": g["result"]["winner"],
           "reason": g["result"]["reason"], "end": T[-1]["turn"], "win": g["result"]["winner"] == g["side"]}
    res["maxF15"] = fpeak
    snaps = {}
    lost = []                                     # Y buildings that stopped being Y's
    f_dead = w_dead = f_spawn = w_spawn = 0
    ev_by_phase = defaultdict(Counter)
    first_cap, first_cap_k = {}, {}
    y_first_w_lead = k_first_w_lead = None
    capped = 0
    ownhist = {}
    for t in range(1, len(T)):
        o, p = obs[t], obs[t - 1]
        cmds = (T[t].get("command") or {}).get("lines", [])
        yeng = sum(1 for b in p["buildings"] if b["type"] == "ENG" and b["owner"] == "Y" and b["stage"] == 2)
        wc = max(2, W_COST - yeng)
        stock = p["resources"]["Y"]
        sf = sw = 0
        for ln in cmds:                            # replay Y's SPAWN commands against Y's stock
            tk = ln.split()
            if tk and tk[0] == "SPAWN" and len(tk) in (3, 5):
                k, n = tk[1], int(tk[2])
                cst = F_COST if k == "F" else (wc if k == "W" else 2)
                got = min(n, stock // cst)
                stock -= got * cst
                if k == "F": sf += got
                if k == "W": sw += got
        f_spawn += sf; w_spawn += sw
        cp, cn = counts(p["units"], "Y"), counts(o["units"], "Y")
        f_dead += max(0, cp["F"] + sf - cn["F"]); w_dead += max(0, cp["W"] + sw - cn["W"])
        pb = {b["id"]: b for b in p["buildings"]}
        for b in o["buildings"]:
            was = pb[b["id"]]["owner"]
            if was == "Y" and b["owner"] != "Y":
                kinds = [e["kind"] for e in o["events"] if e.get("buildingId") == b["id"]]
                lost.append({"turn": t, "type": b["type"], "id": b["id"], "to": b["owner"], "ev": kinds})
            if b["owner"] == "Y" and was != "Y":
                first_cap.setdefault(b["type"], t)
            if b["owner"] == "K" and was != "K":
                first_cap_k.setdefault(b["type"], t)
        for e in o["events"]:
            ph = "1-10" if t <= 10 else "11-20" if t <= 20 else "21-40" if t <= 40 else "41+"
            ev_by_phase[ph][e["kind"] + ("_" + e["team"] if "team" in e else "")] += 1
        cy, ck = counts(o["units"], "Y"), counts(o["units"], "K")
        if y_first_w_lead is None and cy["W"] > ck["W"] and t > 3: y_first_w_lead = t
        if k_first_w_lead is None and ck["W"] > cy["W"] and t > 3: k_first_w_lead = t
        if o["resources"]["Y"] >= 38: capped += 1
        if t in (5, 10, 15, 20, 30, 40, 60, 80, 120, 160) or t == T[-1]["turn"]:
            def own(team): return sum(1 for b in o["buildings"] if b["owner"] == team)
            def typ(team, tp): return sum(1 for b in o["buildings"] if b["owner"] == team and b["type"] == tp)
            snaps[t] = {"bY": own("Y"), "bK": own("K"), "scoreY": o["scores"]["Y"], "scoreK": o["scores"]["K"],
                        "Y": cy, "K": ck, "resY": o["resources"]["Y"], "resK": o["resources"]["K"],
                        "center": {"Y": sum(1 for b in o["buildings"] if b["owner"] == "Y" and 5 <= b["x"] <= 9),
                                   "K": sum(1 for b in o["buildings"] if b["owner"] == "K" and 5 <= b["x"] <= 9)},
                        "plaza": next(b["owner"] for b in o["buildings"] if b["type"] == "PLAZA"),
                        "hallY": typ("Y", "HALL"), "hallK": typ("K", "HALL"), "engY": typ("Y", "ENG"), "engK": typ("K", "ENG"),
                        "wstackY": stacks(o["units"], "Y"), "wstackK": stacks(o["units"], "K")}
    res.update(snaps=snaps, lost=lost, f_spawn=f_spawn, w_spawn=w_spawn, f_dead=f_dead, w_dead=w_dead,
               first_capture_Y=first_cap, first_capture_K=first_cap_k, ev_by_phase={k: dict(v) for k, v in ev_by_phase.items()},
               y_first_w_lead=y_first_w_lead, k_first_w_lead=k_first_w_lead, turns_res_cap=capped,
               max_resp_ms=max(o.get("myResponseMs", 0) for o in obs))
    return res


def w20(r, team="Y"):
    s = r["snaps"].get(20)
    return None if not s else s[team]["W"]


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


def deep(rows):
    print("\n# ---- outcome vs early W lead (all 47 games; lead = Y_W - K_W) ----")
    for T in (10, 20):
        tab = defaultdict(lambda: [0, 0])
        for r in rows:
            s = r["snaps"].get(T)
            if s:
                lead = s["Y"]["W"] - s["K"]["W"]
                key = "Y ahead" if lead > 0 else "K ahead"
                tab[key][0 if r["win"] else 1] += 1
        print(f"T{T}: " + "; ".join(f"{k}: {w}W-{l}L" for k, (w, l) in sorted(tab.items())))
    for ver in ("v2", "v3"):
        rs = [r for r in rows if r["ver"] == ver]
        for label, sel in (("wins", [r for r in rs if r["win"]]), ("losses", [r for r in rs if not r["win"]])):
            if not sel:
                continue
            g = lambda f: mean([f(r) for r in sel])
            s = lambda r, T, tm, k: r["snaps"][T][tm][k] if T in r["snaps"] else None
            print(f"\n## {ver} {label} (n={len(sel)})")
            for T in (5, 10, 20, 40):
                print(f" T{T:>2}: bld Y/K {g(lambda r: r['snaps'].get(T, {}).get('bY')):.1f}/{g(lambda r: r['snaps'].get(T, {}).get('bK')):.1f}"
                      f"  W Y/K {g(lambda r: s(r,T,'Y','W')):.1f}/{g(lambda r: s(r,T,'K','W')):.1f}"
                      f"  F Y/K {g(lambda r: s(r,T,'Y','F')):.1f}/{g(lambda r: s(r,T,'K','F')):.1f}"
                      f"  res Y/K {g(lambda r: r['snaps'].get(T,{}).get('resY')):.1f}/{g(lambda r: r['snaps'].get(T,{}).get('resK')):.1f}"
                      f"  Wtop1 Y/K {g(lambda r: r['snaps'].get(T,{}).get('wstackY',{}).get('top1')):.2f}/{g(lambda r: r['snaps'].get(T,{}).get('wstackK',{}).get('top1')):.2f}"
                      f"  Wtop3 Y/K {g(lambda r: r['snaps'].get(T,{}).get('wstackY',{}).get('top3')):.2f}/{g(lambda r: r['snaps'].get(T,{}).get('wstackK',{}).get('top3')):.2f}")
            print(" first capture turn (mean over games that captured), Y | K:")
            for tp in ("HALL", "ENG", "DEPOT", "PLAZA", "LIBRARY", "HOSPITAL", "STATION", "WATCH"):
                yv = [r["first_capture_Y"].get(tp) for r in sel]; kv = [r["first_capture_K"].get(tp) for r in sel]
                print(f"   {tp:<9} Y {mean(yv):5.1f} ({sum(v is not None for v in yv)}/{len(sel)})   K {mean(kv):5.1f} ({sum(v is not None for v in kv)}/{len(sel)})")
            lo = Counter()
            for r in sel:
                for l in r["lost"]:
                    ph = "<=10" if l["turn"] <= 10 else "11-20" if l["turn"] <= 20 else "21-40" if l["turn"] <= 40 else "41+"
                    lo[(ph, "pulled" if "pulled" in l["ev"] else "neutralized-by-K" if "neutral" in l["ev"] else "other")] += 1
            print(" Y buildings lost per game by phase/cause:", {f"{k[0]}/{k[1]}": round(v / len(sel), 2) for k, v in sorted(lo.items())})
            print(f" F spawned/dead per game: {g(lambda r: r['f_spawn']):.1f}/{g(lambda r: r['f_dead']):.1f}   "
                  f"W spawned/dead: {g(lambda r: r['w_spawn']):.0f}/{g(lambda r: r['w_dead']):.0f}   turns with Y res>=38: {g(lambda r: r['turns_res_cap']):.1f}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--out", default="out/experiments/7-independent-agent(v6)/phase2-analysis/official")
    a = ap.parse_args()
    # games 01-47 only (v2/v3): its peak-flag version rule would call v6 games (peak 10) "v2"; 48+ are analysed in experiment 8
    files = sorted(f for f in glob.glob(os.path.join(a.dir, "[0-9][0-9]_*.json")) if int(os.path.basename(f)[:2]) <= 47)
    rows = [analyze(f) for f in files]
    os.makedirs(a.out, exist_ok=True)
    json.dump(rows, open(os.path.join(a.out, "official_analysis.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def grp(name, sel):
        rs = [r for r in rows if sel(r)]
        wins = sum(r["win"] for r in rs)
        print(f"\n## {name}: n={len(rs)} wins={wins} losses={len(rs)-wins} (ff/cmd-errors: see status)")
        L = [r for r in rs if not r["win"]]
        defi = [r for r in L if w20(r) is not None and w20(r, "K") is not None and w20(r, "K") > w20(r)]
        alive20 = [r for r in L if w20(r) is not None]
        print(f"losses with K_W > Y_W at T20: {len(defi)}/{len(alive20)} (games with a T20 snapshot); "
              f"losses ending before T20: {len(L)-len(alive20)}")
        for r in rs:
            s10, s20 = r["snaps"].get(10), r["snaps"].get(20)
            f = lambda s: "-" if not s else f"{s['bY']}:{s['bK']} W{s['Y']['W']}:{s['K']['W']} F{s['Y']['F']}:{s['K']['F']}"
            print(f"{r['idx']:02d} {r['ver']} {r['opp'][:14]:<14} {'W' if r['win'] else 'L'} {r['reason'][:5]:<5} end={r['end']:>3} "
                  f"maxF15={r['maxF15']:>2} T10[{f(s10)}] T20[{f(s20)}] {r['eval_utc']}")
    grp("v2 games (eval time < v3 submit)", lambda r: r["ver"] == "v2")
    grp("v3 games 20-35 (heartbeat 28 Sep 22:00 round)", lambda r: r["ver"] == "v3" and r["idx"] <= 35)
    grp("v3 games 36-47 (29 Sep 10:00 round)", lambda r: r["ver"] == "v3" and r["idx"] >= 36)
    deep(rows)
    print("\nversion vs peak F (first 15 turns):",
          {v: sorted(r["maxF15"] for r in rows if r["ver"] == v) for v in ("v2", "v3")})
    print("sides:", Counter(r["side"] for r in rows), " max response ms:", max(r["max_resp_ms"] for r in rows))


if __name__ == "__main__":
    main()
