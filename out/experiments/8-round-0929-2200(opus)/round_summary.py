"""Integrity and per-match summary of official replay originals (read only; the files are never modified).

  python "out/experiments/8-round-0929-2200(opus)/round_summary.py" out/official-replays/4[89]_*.json out/official-replays/5?_*.json

Per file: JSON validity, gameId (and whether it repeats an earlier file), side, result/reason, turns, evaluation
slot time (UUIDv7 in evaluationId, KST; a slot time, not a submission time), command statuses, max response ms,
buildings and W:F at T10/T20/end, Y peak flags in turns 1-15 (a version fingerprint: v2 12, v3 6).
"""
import datetime as dt, glob, json, os, sys
from collections import Counter


def uuid7_kst(u):
    ms = int(u.replace("-", "")[:12], 16)
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone(dt.timedelta(hours=9))).strftime("%m-%d %H:%M")


def cnt(units, team, kind):
    return sum(u[4] for u in units if u[0] == team and u[1] == kind)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    files = sorted(f for p in sys.argv[1:] for f in glob.glob(p))
    seen = {}
    for f in sorted(glob.glob(os.path.join(os.path.dirname(files[0]), "[0-9][0-9]_*.json"))):
        if f not in files:
            try:
                seen[json.load(open(f, encoding="utf-8"))["gameId"]] = os.path.basename(f)
            except Exception:  # noqa: BLE001
                pass
    ids = Counter()
    for f in files:
        name = os.path.basename(f)
        try:
            g = json.load(open(f, encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"{name}: INVALID JSON {e}")
            continue
        T = g["turns"]
        obs = [t["observation"] for t in T]
        ids[g["gameId"]] += 1
        st = Counter((t.get("command") or {}).get("status", "-") for t in T[1:])
        resp = [o.get("myResponseMs") for o in obs[1:] if o.get("myResponseMs") is not None]
        end = len(obs) - 1

        def snap(t):
            t = min(t, end)
            o = obs[t]
            nb = {s: sum(1 for b in o["buildings"] if b["owner"] == s) for s in "YK"}
            return f"{nb['Y']}:{nb['K']} W{cnt(o['units'], 'Y', 'W')}:{cnt(o['units'], 'K', 'W')} F{cnt(o['units'], 'Y', 'F')}:{cnt(o['units'], 'K', 'F')}"
        fpeak = max(cnt(o["units"], "Y", "F") for o in obs[:16])
        dup = seen.get(g["gameId"])
        print(f"{name:<22} id {g['gameId'].split('-')[-1][:8]} side {g['side']} {g['result']['winner']}/{g['result']['reason']:<8} "
              f"end T{T[-1]['turn']:>3} slot {uuid7_kst(g['evaluationId'])} cmds {dict(st)} maxms {max(resp) if resp else '-'} "
              f"(first {resp[0] if resp else '-'}, later max {max(resp[1:]) if len(resp) > 1 else '-'}) "
              f"T10 {snap(10)} T20 {snap(20)} end {snap(end)} Fpeak15 {fpeak}" + (f"  DUPLICATE of {dup}" if dup else ""))
    print(f"\nfiles {len(files)}, unique gameIds {len(ids)}, repeated within set {[k for k, v in ids.items() if v > 1]}")


if __name__ == "__main__":
    main()
