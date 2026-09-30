"""Print the Markdown rows of the section 2 table of OFFICIAL_MATCH_ANALYSIS.md for games 48-59.

  python "out/experiments/8-round-0929-2200(opus)/doc_rows.py"
"""
import glob, json, os, sys, urllib.parse

sys.stdout.reconfigure(encoding="utf-8")
REASON = {"instant": "즉시", "score": "점수"}


def st(o):
    b = {s: sum(1 for x in o["buildings"] if x["owner"] == s) for s in "YK"}
    w = {s: sum(u[4] for u in o["units"] if u[0] == s and u[1] == "W") for s in "YK"}
    return b, w


for f in sorted(f for f in glob.glob("out/official-replays/[0-9][0-9]_*.json") if int(os.path.basename(f)[:2]) >= 48):
    name = os.path.basename(f)
    team = name[3:-5].rsplit("_", 1)[0]
    g = json.load(open(f, encoding="utf-8"))
    T = g["turns"]
    b10, w10 = st(T[10]["observation"])
    b20, w20 = st(T[20]["observation"])
    be, _ = st(T[-1]["observation"])
    res = ("승" if g["result"]["winner"] == "Y" else "패") + "·" + REASON.get(g["result"]["reason"], g["result"]["reason"])
    print(f"| {name[:2]} | {team} | v6 코드 | 9/29 22:00 | {res} | {T[-1]['turn']} | {b10['Y']}:{b10['K']} · {w10['Y']}:{w10['K']} | "
          f"{b20['Y']}:{b20['K']} · {w20['Y']}:{w20['K']} | {be['Y']}:{be['K']} | [JSON](official-replays/{urllib.parse.quote(name)}) |")
