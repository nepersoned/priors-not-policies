"""Progress of the 6 parallel coders: screened / included / flags so far."""
import glob
import json
from collections import Counter

tot, inc, flags = 0, 0, Counter()
for k in range(6):
    try:
        rows = [json.loads(l) for l in open(f"paper4/survey/big/coded/chunk_{k}.jsonl", encoding="utf-8") if l.strip()]
    except FileNotFoundError:
        rows = []
    n_inc = sum(1 for r in rows if r.get("include") == "yes")
    print(f"chunk {k}: screened {len(rows):4d}/212  included {n_inc}")
    tot += len(rows)
    inc += n_inc
    for r in rows:
        if r.get("include") == "yes":
            flags.update(r.get("flags") or [])
print(f"TOTAL screened {tot}/1269  included {inc}  flags {dict(flags)}")
