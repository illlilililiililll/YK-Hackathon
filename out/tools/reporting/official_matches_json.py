"""Rebuild per-match JSON summaries (full gameId, snapshots, commands, events, response times) for a numbered range of
official replays.

  python out/tools/reporting/official_matches_json.py --first 20 --last 35   # -> out/official-replays/summary_20-35.json
"""
import argparse
import collections
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2]


def snapshot(turn):
    obs = turn["observation"]
    return {
        "turn": turn["turn"], "score": obs["scores"], "resources": obs["resources"],
        "buildings": {side: sum(b["owner"] == side for b in obs["buildings"]) for side in "YK"},
        "center": {side: sum(b["owner"] == side and 5 <= b["x"] <= 9 for b in obs["buildings"]) for side in "YK"},
        "units": {side: {kind: sum(u[4] for u in obs["units"] if u[:2] == [side, kind]) for kind in "FWS"} for side in "YK"},
        "unit_value": {side: sum(u[4] * {"F": 5, "W": 3, "S": 2}[u[1]] for u in obs["units"] if u[0] == side) for side in "YK"},
        "plaza": next(b["owner"] for b in obs["buildings"] if b["type"] == "PLAZA"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--first", type=int, default=20)
    parser.add_argument("--last", type=int, default=35)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    args.output = args.output or OUT / "official-replays" / f"summary_{args.first}-{args.last}.json"
    files = sorted(path for path in (OUT / "official-replays").glob("[0-9][0-9]_*.json")
                   if args.first <= int(path.name[:2]) <= args.last)
    assert len(files) == args.last - args.first + 1, len(files)
    result = []
    for path in files:
        game = json.loads(path.read_text(encoding="utf-8"))
        turns = game["turns"]
        end = turns[-1]["turn"]
        assert game["side"] == "Y" and end == len(turns) - 1
        commands = collections.Counter()
        spawned = collections.Counter()
        events = collections.Counter()
        statuses = set()
        for turn in turns:
            command = turn.get("command") or {}
            if command:
                statuses.add(command["status"])
            for line in command.get("lines", []):
                words = line.split()
                commands[" ".join(words[:2]) if words[0] == "SPAWN" else words[0]] += 1
                if words[0] == "SPAWN":
                    spawned[words[1]] += int(words[2])
            events.update(e["kind"] for e in turn["observation"]["events"])
        times = [(turn["turn"], turn["observation"].get("myResponseMs") or 0) for turn in turns]
        result.append({"file": path.name, "gameId": game["gameId"], "result": game["result"],
                       "end_turn": end, "snapshots": {str(n): snapshot(turns[n]) for n in (10, 20, max(20, end // 2), end)},
                       "commands": dict(commands), "spawned": dict(spawned), "events": dict(events), "command_statuses": sorted(statuses),
                       "max_response": max(times, key=lambda x: x[1]),
                       "max_response_after_first": max(times[2:], key=lambda x: x[1]) if len(times) > 2 else None})
    assert len({r["gameId"] for r in result}) == len(files)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("games", len(result), "Y wins", sum(r["result"]["winner"] == "Y" for r in result),
          "non-ok", sum(r["command_statuses"] != ["ok"] for r in result),
          "max ordinary response ms", max(r["max_response_after_first"][1] for r in result))


if __name__ == "__main__":
    main()
