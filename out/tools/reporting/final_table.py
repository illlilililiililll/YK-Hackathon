"""Markdown comparison table: candidates x opponents on identical seeds/side (from eval_matches results).

  python out/tools/reporting/final_table.py --files a.jsonl b.jsonl --cands indep1,base,cap7,v3,v2 \
      --opps lv1,lv2,rush,turtle,raider,pack,v2,v3,cap7,base --side Y --seeds 1000-1099 --md out.md

A cell is W-D-L of the candidate (candidate never plays itself). Summary columns are over each candidate's own
opponent list: win%, mean score margin, mean end buildings diff, mean occupation diff, mean unit-value diff,
forfeits, max turn ms (serial timing gate is checked separately), instant-win share.
"""
import argparse, json, sys
from collections import defaultdict


def rng(s):
    a, b = s.split("-")
    return range(int(a), int(b) + 1)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--cands", required=True); ap.add_argument("--opps", required=True)
    ap.add_argument("--side", default="Y"); ap.add_argument("--seeds", default=None)
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    rows = []
    for f in a.files:
        rows += [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    seeds = set(rng(a.seeds)) if a.seeds else None
    rows = [r for r in rows if r["side"] == a.side and (seeds is None or r["seed"] in seeds)]
    cell = defaultdict(list)
    for r in rows:
        cell[(r["cand"], r["opp"])].append(r)
    cands, opps = a.cands.split(","), a.opps.split(",")
    o_ = "K" if a.side == "Y" else "Y"
    out = []
    out.append(f"Side {a.side}, seeds {a.seeds or 'all'}; cell = candidate W-D-L (n)")
    out.append("")
    out.append("| candidate | " + " | ".join(opps) + " |")
    out.append("|---|" + "---|" * len(opps))
    for c in cands:
        cs = []
        for o in opps:
            rs = cell.get((c, o))
            if not rs or c == o:
                cs.append("-")
                continue
            w = sum(r["outcome"] == "W" for r in rs); d = sum(r["outcome"] == "D" for r in rs)
            cs.append(f"{w}-{d}-{len(rs)-w-d} ({len(rs)})")
        out.append(f"| **{c}** | " + " | ".join(cs) + " |")
    out.append("")
    out.append("| candidate | games | win% | W-D-L | margin | end bld diff | occupation diff | unit value diff | forfeits | max ms | instant% |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for c in cands:
        rs = [r for o in opps if o != c for r in cell.get((c, o), [])]
        if not rs:
            continue
        n = len(rs)
        w = sum(r["outcome"] == "W" for r in rs); d = sum(r["outcome"] == "D" for r in rs)
        m = lambda f: sum(f(r) for r in rs) / n
        out.append(f"| **{c}** | {n} | {100*w/n:.1f} | {w}-{d}-{n-w-d} | {m(lambda r: r['margin']):.1f} | "
                   f"{m(lambda r: r['final']['nb'][a.side]-r['final']['nb'][o_]):.1f} | "
                   f"{m(lambda r: r['final']['occ'][a.side]-r['final']['occ'][o_]):.0f} | "
                   f"{m(lambda r: r['final']['uv'][a.side]-r['final']['uv'][o_]):.0f} | "
                   f"{sum(1 for r in rs if r['forfeit'])} | {max(r['cand_max_ms'] for r in rs):.0f} | "
                   f"{100*sum(r['reason']=='instant' for r in rs)/n:.0f} |")
    text = "\n".join(out)
    print(text)
    if a.md:
        open(a.md, "w", encoding="utf-8").write(text + "\n")


if __name__ == "__main__":
    main()
