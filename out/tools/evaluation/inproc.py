"""In-process match (no subprocess; works on Windows). Shows exceptions and per-turn decide() time.

  python out/tools/evaluation/inproc.py --y indep --k lv2 --seed 3
specs: lv1 | lv2 | indep (indep-v0 baseline) | v6 | file:<path/to/main.py> (module must expose decide or _make_decide)
"""
import argparse, importlib.util, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
STARTER = ROOT / "bots/dist/starter/python"


def load(spec):
    if spec in ("lv1", "lv2"):
        path = STARTER / f"example_{spec}.py"
    elif spec == "indep":
        path = ROOT / "out/v0-unsubmitted/indep-v0-claude/source/main.py"
    elif spec == "v6":
        path = ROOT / "out/v6-claude/source/main.py"
    elif spec.startswith("file:"):
        path = Path(spec[5:]).resolve()
    else:
        raise SystemExit(f"bad spec {spec}")
    # each agent must import ITS OWN helper modules: without this, the second agent reuses the first agent's cached
    # `brain` (two indep-family agents then silently play the same policy against each other)
    for m in ("brain", "campus_bot", "protocol", "_generated", "search"):
        sys.modules.pop(m, None)
    sys.path.insert(0, str(path.parent))
    sys.path.insert(1, str(STARTER))
    mod_spec = importlib.util.spec_from_file_location(f"bot_{abs(hash(str(path)))}", path)
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    sys.path.remove(str(path.parent))
    return mod._make_decide() if hasattr(mod, "_make_decide") else mod.decide


class Timed:
    def __init__(self, fn):
        self.fn, self.t = fn, []

    def __call__(self, view, init):
        t0 = time.perf_counter()
        r = self.fn(view, init)
        self.t.append((time.perf_counter() - t0) * 1000)
        return r


def main():
    from engine.config import load_config
    from runner import InProcessBot, run_match
    p = argparse.ArgumentParser()
    p.add_argument("--y", default="indep"); p.add_argument("--k", default="lv2")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--replay", default=None)
    a = p.parse_args()
    ty, tk = Timed(load(a.y)), Timed(load(a.k))
    replay, res = run_match(a.seed, load_config(), InProcessBot(ty, a.y), InProcessBot(tk, a.k))
    print({k: res[k] for k in ("winner", "reason", "score", "turns")})
    for name, t in (("Y", ty.t), ("K", tk.t)):
        if t:
            s = sorted(t)
            print(f"{name} decide ms: first={t[0]:.1f} mean={sum(t)/len(t):.2f} p95={s[int(len(s)*.95)]:.2f} max={s[-1]:.2f}")
    if a.replay:
        import json
        Path(a.replay).parent.mkdir(parents=True, exist_ok=True)
        Path(a.replay).write_text(json.dumps(replay), encoding="utf-8")


if __name__ == "__main__":
    main()
