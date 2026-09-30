"""Check that Markdown links and repo paths mentioned in the project's own docs still resolve.

  python out/tools/reporting/check_links.py            # all .md files outside the official kit (bots/, docs/)

Checks (1) [text](relative/target) links, (2) `out/...`-style repo paths inside code spans / fenced commands, and
(3) that every `python[3] <script>` / `bash <script>` in the docs names an existing script.
Conventions (so intentional mentions are not reported):
  * fenced blocks tagged `text` are verbatim quotations (e.g. the prompts in PROMPT_RECORD.md) and are skipped;
  * lines that describe a move or a historical name ("Old names", "->", "→", "was `", "옛", ...) are skipped;
  * paths ending in a glob (*), containing a placeholder (<tag>), or below out/experiments/local-runs/ (command output) are skipped.
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
SKIP_TOP = {"bots", "docs", ".git", ".claude", "node_modules"}
PREFIX = r"(?:out|bots|docs|engine|runner|mapgen|config)/"
LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)\)")
SPAN = re.compile(r"`([^`\n]+)`")
PATH = re.compile(r"(?<![\w./-])(" + PREFIX + r"(?:[^\s`'\"<>*{}\[\]|;,()]|\([\w-]+\))+)")   # allows the "(v3)" in experiment folder names
HISTORICAL = re.compile(r"Old names|old name|old path|formerly|previously|was `|->|→|옛 |이전 이름|historical|removed")
CMD = re.compile(r"(?:python3?|bash)\s+(?:-\S+\s+)*\"?((?:out|bots|engine|runner|mapgen|config)/(?:[\w./-]|\([\w-]+\))+\.(?:py|sh))")   # optional quote, "(v3)" folder segments
GENERATED = ("out/_scratch", "out/experiments/local-runs", "out/submission-python.zip", "out/local-replay.json", "out/replay.json", "out/result.json")


def md_files():
    for p in sorted(ROOT.rglob("*.md")):
        rel = p.relative_to(ROOT)
        if rel.parts[0] not in SKIP_TOP:
            yield p


def main():
    bad = []
    for md in md_files():
        text = md.read_text(encoding="utf-8", errors="replace")
        name = md.relative_to(ROOT).as_posix()
        for m in LINK.finditer(text):
            target = m.group(1).split("#")[0]
            if not target or re.match(r"[a-z]+:", target):
                continue
            if not (md.parent / unquote(target)).exists():
                bad.append((name, "link", target))
        if name == "out/PATH_MAP.md":     # a list of old paths by design; only its links are checked
            continue
        fence = None                      # None, or the info string of the open fenced block
        for line in text.splitlines():
            if line.lstrip().startswith("```"):
                fence = None if fence is not None else line.lstrip().strip("`").strip()
                continue
            if fence == "text" or HISTORICAL.search(line):
                continue
            for m in CMD.finditer(line):          # documented commands must name an existing script
                if not (ROOT / m.group(1)).exists() and not m.group(1).startswith(GENERATED):
                    bad.append((name, "command script", m.group(1)))
            for chunk in ([line] if fence is not None else SPAN.findall(line)):
                for m in PATH.finditer(chunk):
                    target = m.group(1).rstrip(".:")
                    if chunk[m.end():m.end() + 1] in ("*", "<") or target.startswith(GENERATED):
                        continue
                    if not (ROOT / target).exists():
                        bad.append((name, "path", target))
    for row in bad:
        print("BROKEN %s: %s -> %s" % row)
    print(f"{len(bad)} broken reference(s) in {sum(1 for _ in md_files())} Markdown files")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
