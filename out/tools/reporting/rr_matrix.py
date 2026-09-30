"""Round-robin matrix from eval_matches results (Y-side games; each cell = row agent's win% vs column agent).

  python out/tools/reporting/rr_matrix.py out/experiments/7-independent-agent(v6)/phase3-selection/p3-select2-rr/results.jsonl
A game is (cand as Y) vs (opp as K). Because deterministic agents mirror across sides, cand-vs-opp also gives opp-vs-cand
(win% of opp = 100 - cand win% - draw%). Prints the matrix with W-D-L counts and each agent's mean win% and worst matchup.
"""
import json, sys
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding="utf-8")
rows = []
for f in sys.argv[1:]:
    rows += [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
rows = [r for r in rows if r["side"] == "Y"]
cell = defaultdict(Counter)
for r in rows:
    cell[(r["cand"], r["opp"])][r["outcome"]] += 1
agents = sorted({r["cand"] for r in rows} | {r["opp"] for r in rows})


def get(a, b):
    """(W, D, L) of agent a against b, from whichever ordering was run."""
    if (a, b) in cell:
        c = cell[(a, b)]
        return c["W"], c["D"], c["L"]
    if (b, a) in cell:
        c = cell[(b, a)]
        return c["L"], c["D"], c["W"]
    return None


order = sorted(agents, key=lambda a: -sum((get(a, b) or (0, 0, 0))[0] - (get(a, b) or (0, 0, 0))[2] for b in agents if b != a))
w = 12
print(f"{'row beats col':<{w}}" + "".join(f"{b:>{w}}" for b in order) + f"{'mean%':>8}{'worst%':>8}")
for a in order:
    line, pct = f"{a:<{w}}", []
    for b in order:
        g = get(a, b) if a != b else None
        if g is None:
            line += f"{'-':>{w}}"
            continue
        n = sum(g)
        line += f"{f'{g[0]}-{g[1]}-{g[2]}':>{w}}"
        pct.append(100 * g[0] / n)
    print(line + f"{sum(pct)/len(pct):>8.1f}{min(pct):>8.1f}")
