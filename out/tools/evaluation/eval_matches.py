"""Batch local matches through the official runner (SubprocessBot + run_match). Run under WSL/Linux.

  python3 out/tools/evaluation/eval_matches.py --tag t1 \
      --cand indep="python3 out/v0-unsubmitted/indep-v0-claude/source/main.py" \
      --opp lv1="python3 bots/dist/starter/python/example_lv1.py" \
      --seeds 0-9 --sides Y,K --jobs 6

--sides picks which team the candidate plays (Y = official practice side, K = symmetry diagnostic).
Results: out/experiments/local-runs/<tag>/results.jsonl (+ replays/*.json.gz for non-wins or --save-replays all).
"""
import argparse, gzip, json, os, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

CHECK_TURNS = (10, 20, 40, 80, 120, 160)


def _parse_seeds(s):
    out = []
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += range(int(a), int(b) + 1)
        else:
            out.append(int(part))
    return out


def _kv(s):
    k, v = s.split("=", 1)
    return k, v


def _metrics(replay):
    """Score / occupation / unit value / early-game timeline straight from the replay snapshots."""
    bs = {b["id"]: b for b in replay["map"]["buildings"]}
    vals = replay["config"]["tiebreak_values"]
    total = sum(b["score"] for b in bs.values())
    tl = {}
    last = None
    for t in replay["turns"]:
        st = t["state"]
        last = (t["turn"], st)
        if t["turn"] in CHECK_TURNS:
            tl[t["turn"]] = _snap(st, bs, vals)
    if last is None:            # forfeit before any turn was processed
        return {"total": total, "timeline": {}, "ignored_lines": {"Y": 0, "K": 0},
                "final": {"score": {"Y": 0, "K": 0}, "nb": {"Y": 0, "K": 0}, "turn": 0,
                          "units": {t: {"F": 0, "W": 0, "S": 0} for t in "YK"},
                          "uv": {"Y": 0, "K": 0}, "res": {"Y": 10, "K": 10}, "occ": {"Y": 0, "K": 0}}}
    turn, st = last
    final = _snap(st, bs, vals)
    final["turn"] = turn
    final["occ"] = dict(st["occupation"])
    ignored = {"Y": 0, "K": 0}
    for t in replay["turns"]:
        for team in ("Y", "K"):
            ignored[team] += len(t["commands"][team]) - len(t["applied"][team])
    return {"total": total, "timeline": tl, "final": final, "ignored_lines": ignored}


def _snap(st, bs, vals):
    sc = {"Y": 0, "K": 0}
    nb = {"Y": 0, "K": 0}
    for b in st["buildings"]:
        if b["owner"] in sc:
            sc[b["owner"]] += bs[b["id"]]["score"]
            nb[b["owner"]] += 1
    cnt = {"Y": {"F": 0, "W": 0, "S": 0}, "K": {"F": 0, "W": 0, "S": 0}}
    for team, kind, x, y, c in st["units"]:
        cnt[team][kind] += c
    uv = {t: sum(vals[k] * n for k, n in cnt[t].items()) for t in cnt}
    return {"score": sc, "nb": nb, "units": cnt, "uv": uv, "res": dict(st["resources"])}


def run_one(job):
    from engine.config import load_config
    from runner import SubprocessBot, run_match

    class TimedBot(SubprocessBot):
        """max_turn_ms over turns >= 2 (turn 1 = process start + init, budget 3 s, tracked apart)."""
        n = 0
        first_ms = 0.0

        def collect_turn(self):
            r = super().collect_turn()
            self.n += 1
            if self.n == 1:
                self.first_ms, self.max_turn_ms = self.max_turn_ms, 0.0
            return r

    cfg = load_config()
    cand_side = job["side"]
    cmds = {cand_side: job["cand_cmd"], ("K" if cand_side == "Y" else "Y"): job["opp_cmd"]}
    by, bk = TimedBot(cmds["Y"], name=cmds["Y"]), TimedBot(cmds["K"], name=cmds["K"])
    t0 = time.time()
    try:
        replay, res = run_match(job["seed"], cfg, by, bk, turn_timeout_ms=300)
    finally:
        by.close(); bk.close()
    m = _metrics(replay)
    from midgame_metrics import metrics as mid_metrics      # same folder; midgame building control per team
    m["mid"] = mid_metrics(replay)
    other = "K" if cand_side == "Y" else "Y"
    w = res["winner"]
    outcome = "D" if w == "DRAW" else ("W" if w == cand_side else "L")
    row = {
        "tag": job["tag"], "cand": job["cand"], "opp": job["opp"], "seed": job["seed"], "side": cand_side,
        "outcome": outcome, "winner": w, "reason": res["reason"], "turns": res["turns"],
        "score": res["score"], "forfeit": res.get("forfeit"),
        "max_ms": {"Y": round(by.max_turn_ms, 1), "K": round(bk.max_turn_ms, 1)},
        "first_ms": {"Y": round(by.first_ms, 1), "K": round(bk.first_ms, 1)},
        "wall_s": round(time.time() - t0, 1), **m,
    }
    row["cand_max_ms"] = row["max_ms"][cand_side]
    row["margin"] = res["score"][cand_side] - res["score"][other]
    save = job["save"] == "all" or (job["save"] == "lost" and outcome != "W")
    if save:
        d = Path(job["out"]) / "replays"
        d.mkdir(parents=True, exist_ok=True)
        name = f"{job['cand']}-{cand_side}-vs-{job['opp']}-s{job['seed']}.json.gz"
        with gzip.open(d / name, "wt", encoding="utf-8") as f:
            json.dump(replay, f, ensure_ascii=False)
    return row


def summarize(rows, out=sys.stdout):
    from collections import defaultdict
    g = defaultdict(list)
    for r in rows:
        g[(r["cand"], r["opp"], r["side"])].append(r)
    hdr = f"{'cand':<14}{'opp':<12}{'side':<5}{'n':>3} {'W-D-L':>9} {'margin':>7} {'occ(c-o)':>9} {'uv(c-o)':>8} {'ff':>3} {'maxms':>6} {'inst%':>6}"
    print(hdr, file=out)
    for (c, o, s), rs in sorted(g.items()):
        o_ = "K" if s == "Y" else "Y"
        w = sum(r["outcome"] == "W" for r in rs); d = sum(r["outcome"] == "D" for r in rs); l = len(rs) - w - d
        mar = sum(r["margin"] for r in rs) / len(rs)
        occ = sum(r["final"]["occ"][s] - r["final"]["occ"][o_] for r in rs) / len(rs)
        uv = sum(r["final"]["uv"][s] - r["final"]["uv"][o_] for r in rs) / len(rs)
        ff = sum(1 for r in rs if r["forfeit"])
        mx = max(r["cand_max_ms"] for r in rs)
        inst = 100 * sum(r["reason"] == "instant" for r in rs) / len(rs)
        print(f"{c:<14}{o:<12}{s:<5}{len(rs):>3} {f'{w}-{d}-{l}':>9} {mar:>7.1f} {occ:>9.0f} {uv:>8.0f} {ff:>3} {mx:>6.0f} {inst:>6.0f}", file=out)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tag", required=True)
    p.add_argument("--cand", action="append", required=True, type=_kv)
    p.add_argument("--opp", action="append", required=True, type=_kv)
    p.add_argument("--seeds", default="0-9")
    p.add_argument("--sides", default="Y")
    p.add_argument("--jobs", type=int, default=6)
    p.add_argument("--save-replays", choices=["none", "lost", "all"], default="lost")
    p.add_argument("--outdir", default="out/experiments/local-runs")
    p.add_argument("--resume", action="store_true", help="append to an existing results.jsonl and skip finished games")
    p.add_argument("--unordered", action="store_true", help="skip self-pairs and the reverse of an already scheduled pair")
    p.add_argument("--errlog", default=None,
                   help="file the candidate cmd appends stderr to (cmd ... 2>>FILE); tracebacks in it are counted")
    a = p.parse_args()
    out = Path(a.outdir) / a.tag
    out.mkdir(parents=True, exist_ok=True)
    if a.errlog and os.path.exists(a.errlog):
        os.remove(a.errlog)
    pairs, seen = [], set()
    for c, cc in a.cand:
        for o, oc in a.opp:
            if a.unordered and (c == o or (o, c) in seen):     # round-robin: each unordered pair once, no self-play
                continue
            seen.add((c, o))
            pairs.append((c, cc, o, oc))
    jobs = [dict(tag=a.tag, cand=c, cand_cmd=cc, opp=o, opp_cmd=oc, seed=s, side=side, save=a.save_replays, out=str(out))
            for c, cc, o, oc in pairs for side in a.sides.split(",") for s in _parse_seeds(a.seeds)]
    rows = []
    res_path = out / "results.jsonl"
    if a.resume and res_path.exists():                      # keep finished games, run only the missing ones
        rows = [json.loads(l) for l in open(res_path, encoding="utf-8") if l.strip()]
        done = {(r["cand"], r["opp"], r["seed"], r["side"]) for r in rows}
        jobs = [j for j in jobs if (j["cand"], j["opp"], j["seed"], j["side"]) not in done]
        print(f"resume: {len(rows)} games already done, {len(jobs)} to run", flush=True)
    with ProcessPoolExecutor(a.jobs) as ex, open(res_path, "a" if a.resume else "w", encoding="utf-8") as f:
        for r in ex.map(run_one, jobs):
            rows.append(r)
            f.write(json.dumps(r, ensure_ascii=False) + "\n"); f.flush()
    with open(out / "summary.txt", "w", encoding="utf-8") as f:
        summarize(rows, f)
    summarize(rows)
    if a.errlog:
        n = open(a.errlog, encoding="utf-8", errors="replace").read().count("Traceback") if os.path.exists(a.errlog) else 0
        print(f"stderr tracebacks in {a.errlog}: {n}" + ("   <-- FIX BEFORE TRUSTING RESULTS" if n else ""))
    print(f"-> {out}/results.jsonl ({len(rows)} games)")


if __name__ == "__main__":
    main()
