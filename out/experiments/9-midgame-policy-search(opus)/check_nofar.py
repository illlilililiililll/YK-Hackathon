"""Runnable check of the adopted rule (no far hunting, hunt_r=1) against the frozen baseline (hunt_r=6).

  python "out/experiments/9-midgame-policy-search(opus)/check_nofar.py"

Open map, 5 of my W at (5,7), one enemy flag at (9,7) heading for a far building: no rule but far hunting sends W east.
Midgame (T50): the baseline sends W one step toward the flag (R), the shipped source does not.
Endgame (T150): both keep far hunting off (the v6-endgame20 endgame branch is unchanged).
"""
import importlib.util, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "v0-unsubmitted")


def brain(folder):
    spec = importlib.util.spec_from_file_location(f"brain_{folder}", os.path.join(ROOT, folder, "source", "brain.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.Brain


def east_moves(B, turn):
    terrain = ["." * 15] * 15
    blds = [(14, 0, "HALL"), (0, 14, "ENG")]
    b = B(terrain, blds, (0, 7), (14, 7))
    units = [("M", "W", 5, 7, 5), ("E", "F", 9, 7, 1)]
    state = [(14, 0, "HALL", "N", 0, -1), (0, 14, "ENG", "N", 0, -1)]
    cmds = b.act(turn, 0, 0, units, state)
    return [c for c in cmds if c[0] == "move" and c[1:4] == (5, 7, "W") and c[5] == "R"]


if __name__ == "__main__":
    base, ship = brain("v6-endgame20-frozen-opus"), brain("v6-endgame20-opus")
    assert east_moves(base, 50), "baseline should chase the flag 4 steps away (hunt_r=6)"
    assert not east_moves(ship, 50), "shipped source must not chase far flags in the midgame"
    assert not east_moves(base, 150) and not east_moves(ship, 150), "endgame: far hunting off in both"
    print("ok: midgame far hunt only in the baseline; endgame identical")
