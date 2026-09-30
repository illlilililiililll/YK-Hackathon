"""Summarize the public, Y-side official match replays (table for out/OFFICIAL_MATCH_ANALYSIS.md).

  python out/tools/reporting/official_table.py
"""
import json
from pathlib import Path


def state(turn):
    obs = turn["observation"]
    buildings = obs["buildings"]
    units = obs["units"]
    return {
        "score": obs["scores"]["Y"],
        "resources": obs["resources"],
        "buildings": {team: sum(b["owner"] == team for b in buildings) for team in "YK"},
        "warriors": {team: sum(u[4] for u in units if u[:2] == [team, "W"]) for team in "YK"},
        "flags": {team: sum(u[4] for u in units if u[:2] == [team, "F"]) for team in "YK"},
        "center": {team: sum(b["owner"] == team and 5 <= b["x"] <= 9 for b in buildings) for team in "YK"},
        "plaza": next(b["owner"] for b in buildings if b["type"] == "PLAZA"),
    }


def main():
    files = sorted((Path(__file__).resolve().parents[2] / "official-replays").glob("[0-9][0-9]_*.json"))
    ids = [json.loads(f.read_text(encoding="utf-8"))["gameId"] for f in files]
    assert len(set(ids)) == len(files) == 71, f"Expected 71 distinct official replays, found {len(files)} files / {len(set(ids))} ids"
    print("| 경기 | 결과 | 사유 | 턴 | 10턴 건물 Y:K / W Y:K | 20턴 건물 Y:K / W Y:K | 종료 건물 Y:K |")
    print("| --- | --- | --- | ---: | --- | --- | --- |")
    for file in files:
        game = json.loads(file.read_text(encoding="utf-8"))
        turns = game["turns"]
        end = turns[-1]["turn"]
        states = {n: state(turns[min(n, len(turns) - 1)]) for n in (10, 20, end)}
        def brief(n):
            s = states[n]
            return f"{s['buildings']['Y']}:{s['buildings']['K']} / {s['warriors']['Y']}:{s['warriors']['K']}"
        print(f"| {file.stem} | {game['result']['winner']} | {game['result']['reason']} | {end} | {brief(10)} | {brief(20)} | {states[end]['buildings']['Y']}:{states[end]['buildings']['K']} |")
    print("\n대표 경기 상세: 점수는 상대 측 미공개 점수를 추정하지 않음")
    for prefix in ("02_", "03_", "06_", "08_", "16_"):
        file = next(p for p in files if p.name.startswith(prefix))
        game = json.loads(file.read_text(encoding="utf-8"))
        turns = game["turns"]
        print("\n", file.stem, game["result"])
        for n in sorted({10, 20, len(turns) // 2, len(turns) - 1}):
            s = state(turns[min(n, len(turns) - 1)])
            print(n, s)


if __name__ == "__main__":
    main()
