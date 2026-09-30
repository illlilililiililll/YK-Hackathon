"""Verify the retained submission artifacts.

  python out/tools/evaluation/verify_artifacts.py

For every model folder (v1-v2-codex, v3-codex, v6-claude, v4-v5-provenance-uncertain, v0-unsubmitted/*):
  1. the folder holds its ZIP;
  2. where the folder has source/, the ZIP entries equal the source files byte for byte (the one documented variant, rebuilt-main5.zip,
     must equal source/ except that its main.py carries the two constants GUARD = 2 and ENDGAME = 15 of the received main5.zip);
  3. ZIP entries have no execute bit (the server rejects them: EXECUTABLE_FILE) - except the indep-v0 ZIP, kept as
     evidence of that defect, which must have it.
Then v1: its ZIP was deleted as a redundant copy of the v2 contents; it is rebuilt from v1-v2-codex/source/ and
v1-zip-manifest.json and must reproduce the uploaded file (compressed bytes depend on the zlib build, so a
different zlib only produces a warning after entries and modes have been checked).
Exit status 1 on any mismatch.
"""
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

OUT = Path(__file__).resolve().parents[2]
FOLDERS = ["v1-v2-codex", "v3-codex", "v6-claude", "v4-v5-provenance-uncertain", "v0-unsubmitted/cap7-codex", "v0-unsubmitted/indep-v0-claude",
           "v0-unsubmitted/v6-endgame20-opus", "v0-unsubmitted/v6-endgame20-frozen-opus"]
KNOWN_BAD_MODES = {"v0-unsubmitted/indep-v0-claude"}                     # 0o100777 entries: kept as evidence, never upload
NO_SOURCE_MATCH = {"v0-unsubmitted/indep-v0-claude"}                     # ZIP = Phase-1 build; source/ = later parametrised baseline
# main5.zip variant: source/main.py with these two lines replaced (README of v4-v5-provenance-uncertain)
VARIANT_EDITS = {"v4-v5-provenance-uncertain/rebuilt-main5.zip": {"main.py": [
    ("GUARD = 1          # 건물당 기본 수비 인원", "GUARD = 2          # 건물당 기본 수비 인원"),
    ("ENDGAME = 0        # 마지막 몇 턴 수비 강화 (테스트 결과 끄는 게 더 강함)", "ENDGAME = 15       # 마지막 몇 턴은 수비 강화")]}}


def expected(folder, zip_name, entry, data):
    """Bytes the ZIP entry must have, or None if the documented edit does not apply to source/."""
    for old, new in VARIANT_EDITS.get(f"{folder}/{zip_name}", {}).get(entry, []):
        if data.count(old.encode("utf-8")) != 1:
            return None
        data = data.replace(old.encode("utf-8"), new.encode("utf-8"))
    return data


def check_v1():
    """Rebuild the rejected v1 ZIP from the shared source + manifest; return the number of failures."""
    base = OUT / "v1-v2-codex"
    manifest = json.loads((base / "v1-zip-manifest.json").read_text(encoding="utf-8"))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for e in manifest["entries"]:
            data = (base / "source" / e["name"]).read_bytes()
            if hashlib.sha256(data).hexdigest() != e["sha256"]:
                print(f"FAIL  v1 manifest: source/{e['name']} differs from the entry that was uploaded")
                return 1
            info = zipfile.ZipInfo(e["name"], tuple(e["date_time"]))
            info.external_attr, info.create_system, info.compress_type = int(e["mode"], 8) << 16, e["create_system"], zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    rebuilt = buf.getvalue()
    modes = {e["mode"] for e in manifest["entries"]}
    if hashlib.sha256(rebuilt).hexdigest() == manifest["zip_sha256"]:
        print(f"ok    v1 ZIP rebuilt bit for bit ({len(rebuilt)} bytes), entry modes {sorted(modes)} (execute bits: the reason for the rejection)")
    else:
        print(f"WARN  v1 ZIP rebuilt with different compressed bytes; entries and modes match the manifest (zlib build dependent)")
    return 0


def main():
    bad = 0
    for folder in FOLDERS:
        base = OUT / folder
        zips = sorted(base.glob("*.zip"))
        if not zips:
            print(f"MISSING {folder}: no ZIP")
            bad += 1
        for z in zips:
            here = 0
            with zipfile.ZipFile(z) as zf:
                exec_bits = any((i.external_attr >> 16) & 0o111 for i in zf.infolist())
                if exec_bits != (folder in KNOWN_BAD_MODES):
                    print(f"FAIL  {folder}/{z.name}: execute bits {'present' if exec_bits else 'absent'}, expected {'present' if folder in KNOWN_BAD_MODES else 'absent'}")
                    here += 1
                same = "n/a"
                if (base / "source").is_dir() and folder not in NO_SOURCE_MATCH:
                    same = all((base / "source" / n).exists() and expected(folder, z.name, n, (base / "source" / n).read_bytes()) == zf.read(n) for n in zf.namelist())
                    if not same:
                        print(f"FAIL  {folder}/{z.name}: ZIP entries differ from source/")
                        here += 1
            print(f"{'ok  ' if not here else 'FAIL'}  {folder + '/' + z.name:<58} {z.stat().st_size:>6} bytes  entries==source: {same}  execute bits: {exec_bits}")
            bad += here
    bad += check_v1()
    print("RESULT:", "FAIL" if bad else "all artifact checks passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
