"""Independent Y agent entry point. Policy lives in brain.py; protocol I/O is the official helper."""
import json
import os
import sys
import traceback

from campus_bot import run
from protocol import move, priority, spawn
from brain import Brain

FLIP_DIR = {"U": "D", "D": "U", "L": "R", "R": "L"}
_errors = 0


def _parse_params(s):
    """Tuning overrides for experiments only: INDEP_PARAMS='garrison=1,hunt_r=6' (or a JSON object). Unset in submissions."""
    s = s.strip()
    if not s:
        return {}
    if s.startswith("{"):
        return json.loads(s)
    return {k: float(v) if "." in v else int(v) for k, v in (kv.split("=") for kv in s.split(","))}


def _make_decide():
    st = {}

    def decide(view, init):
        global _errors
        try:
            flip = init.bases[init.team][0] * 2 > init.width - 1     # K side: rotate 180 degrees
            c = (lambda x, y: (14 - x, 14 - y)) if flip else (lambda x, y: (x, y))
            if "brain" not in st:
                terrain = [[init.terrain[y][x] for x in range(15)] for y in range(15)]
                if flip:
                    terrain = [row[::-1] for row in terrain[::-1]]
                blds = [(*c(b["x"], b["y"]), b["type"]) for b in init.buildings]
                params = _parse_params(os.environ.get("INDEP_PARAMS", ""))
                st["brain"] = Brain(terrain, blds, c(*init.bases[init.team]),
                                    c(*init.bases[init.opp]), params)
            who = {view.team: "M", view.opp: "E", "N": "N"}
            units = [(who[u["team"]], u["kind"], *c(u["x"], u["y"]), u["count"]) for u in view.units]
            blds = [(*c(b["x"], b["y"]), b["type"], who[b["owner"]], b["stage"], b["score"])
                    for b in view.buildings]
            out = []
            for cmd in st["brain"].act(view.turn, view.my_resource, view.opp_resource, units, blds):
                if cmd[0] == "spawn":
                    out.append(spawn(cmd[1], cmd[2]) if len(cmd) == 3 else spawn(cmd[1], cmd[2], *c(cmd[3], cmd[4])))
                elif cmd[0] == "move":
                    _, x, y, kind, n, d = cmd
                    x, y = c(x, y)
                    out.append(move(x, y, kind, n, FLIP_DIR[d] if flip else d))
                else:
                    out.append(priority([c(x, y) for x, y in cmd[1]]))
            return out
        except Exception:                      # never crash: a missing END forfeits the game
            _errors += 1
            if _errors <= 3:
                sys.stderr.write(traceback.format_exc()[-1500:] + "\n")
            return [spawn("W", 99)]           # degraded mode: still buy W with everything affordable

    return decide


if __name__ == "__main__":
    run(_make_decide())
