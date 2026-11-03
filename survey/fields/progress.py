"""Progress of the multi-field survey: coded papers and flags per field, prior-work files present."""
import glob
import json
import os
from collections import Counter

base = "paper4/survey/fields/"
for path in sorted(glob.glob(base + "coded_*.jsonl")):
    field = os.path.basename(path)[6:-6]
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    inc = [r for r in rows if r.get("include") in ("yes", True)]
    fl = Counter(f for r in inc for f in (r.get("flags") or []))
    reg = Counter(r.get("regime") for r in inc)
    prior = "yes" if os.path.exists(base + f"prior_{field}.md") else "no"
    print(f"{field:10} screened {len(rows):3d} included {len(inc):3d} regime {dict(reg)} flags {dict(fl)} prior-work {prior}")
