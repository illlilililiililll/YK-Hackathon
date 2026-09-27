"""Run reproducible local seed sets with the official engine and runner."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.config import load_config
from runner import SubprocessBot, run_match


def main():
    p = argparse.ArgumentParser()
    p.add_argument("candidate")
    p.add_argument("opponent")
    p.add_argument("--side", choices=("Y", "K"), default="Y")
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--name", default="trial")
    args = p.parse_args()
    folder = ROOT / "out" / args.name
    folder.mkdir(parents=True, exist_ok=True)
    cfg = load_config()
    cfg["first_turn_timeout_ms"] = 3000
    results = []
    for seed in range(args.seeds):
        a = SubprocessBot(f"{sys.executable} {args.candidate}", "candidate")
        b = SubprocessBot(f"{sys.executable} {args.opponent}", "opponent")
        y, k = (a, b) if args.side == "Y" else (b, a)
        replay, result = run_match(seed, cfg, y, k, turn_timeout_ms=300)
        result["candidate_max_turn_ms"] = round(a.max_turn_ms, 2)
        results.append(result)
        (folder / f"seed-{seed}.json").write_text(json.dumps(replay, ensure_ascii=False), encoding="utf-8")
        print(seed, result, flush=True)
    summary = {key: sum(r["winner"] == value for r in results)
               for key, value in (("win", args.side), ("draw", "DRAW"),
                                  ("loss", "K" if args.side == "Y" else "Y"))}
    summary["forfeit"] = sum(r["reason"] == "forfeit" and r["forfeit"]["team"] == args.side for r in results)
    summary["max_turn_ms"] = max(r["candidate_max_turn_ms"] for r in results)
    (folder / "summary.json").write_text(json.dumps({"args": vars(args), "summary": summary, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("SUMMARY", summary)


if __name__ == "__main__":
    main()
