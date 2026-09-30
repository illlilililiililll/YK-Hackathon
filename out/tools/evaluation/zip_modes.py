"""Print unix modes of every ZIP entry and fail if any has an execute bit (server rejects EXECUTABLE_FILE).

  python out/tools/evaluation/zip_modes.py out/v0-unsubmitted/indep-v0-claude/indep-v0.zip [...]
"""
import stat, sys, zipfile

bad = 0
for path in sys.argv[1:]:
    z = zipfile.ZipFile(path)
    print(path)
    for i in z.infolist():
        mode = i.external_attr >> 16
        x = bool(mode & 0o111)
        bad += x
        print(f"  {i.filename:<18} {oct(mode)}  create_system={i.create_system}  {'EXECUTABLE' if x else 'ok'}")
print("RESULT:", "FAIL (execute bit present)" if bad else "ok (no execute bits)")
sys.exit(1 if bad else 0)
