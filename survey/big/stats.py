"""Survey statistics for the draft: domain x flag tables, E2 examples."""
import json
from collections import Counter, defaultdict

rows = []
for k in range(6):
    rows += [json.loads(l) for l in open(f"paper4/survey/big/coded/chunk_{k}.jsonl", encoding="utf-8") if l.strip()]
inc = [r for r in rows if r.get("include") == "yes"]
print("screened", len(rows), "included", len(inc))
dom = Counter(r.get("domain") for r in inc)
print("domains", dict(dom.most_common()))
reg = Counter(r.get("regime") for r in inc)
print("regime", dict(reg))
sig = Counter(s for r in inc for s in (r.get("signal") or []))
print("signal", dict(sig))
fl = Counter(f for r in inc for f in (r.get("flags") or []))
print("flags", dict(fl))
level = [r for r in inc if "LEVEL" in (r.get("signal") or [])]
print("LEVEL papers", len(level), "direction", dict(Counter(r.get("direction") for r in level)))
binlev = [r for r in level if r.get("regime") == "exponential"]
print("LEVEL in exponential regime", len(binlev), "direction", dict(Counter(r.get("direction") for r in binlev)))
by = defaultdict(Counter)
for r in inc:
    for f in (r.get("flags") or []):
        by[r.get("domain")][f] += 1
for d, c in by.items():
    print(f"  {d}: {dict(c)}")
print("fulltext checked", sum(1 for r in inc if r.get("fulltext_checked")), "/", len(inc))
print("E2 ids:", [r["id"] for r in inc if "E2" in (r.get("flags") or [])])
