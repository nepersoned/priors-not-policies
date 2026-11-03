"""Blind validation sample (50 papers: 15 E2 + 35 others) for a second coder,
and a 10-paper human check sheet for E2."""
import json
import random

rows = []
for k in range(6):
    rows += [json.loads(l) for l in open(f"paper4/survey/big/coded/chunk_{k}.jsonl", encoding="utf-8") if l.strip()]
inc = [r for r in rows if r.get("include") == "yes"]
random.seed(20261001)
e2 = [r for r in inc if "E2" in (r.get("flags") or [])]
other = [r for r in inc if "E2" not in (r.get("flags") or [])]
sample = random.sample(e2, 15) + random.sample(other, 35)
random.shuffle(sample)
cands = {}
for k in range(6):
    for l in open(f"paper4/survey/big/chunks/chunk_{k}.jsonl", encoding="utf-8"):
        o = json.loads(l)
        cands[o["id"]] = o
with open("paper4/survey/big/validation_sample.jsonl", "w", encoding="utf-8") as f:
    for r in sample:
        c = cands.get(r["id"], {})
        f.write(json.dumps({"id": r["id"], "title": r.get("title") or c.get("title"),
                            "abstract": c.get("abstract")}, ensure_ascii=False) + "\n")
human = random.sample(e2, 10)
with open("paper4/survey/big/human_check_E2.md", "w", encoding="utf-8") as f:
    f.write("# Human check: 10 random E2 papers\n\n"
            "For each paper: open it, find the allocation rule, and mark whether harder inputs get MORE budget "
            "with no discount for hopeless ones (E2 = yes).\n\n"
            "| # | id | title | coder evidence | your verdict (yes/no/unclear) | note |\n|---|---|---|---|---|---|\n")
    for i, r in enumerate(human, 1):
        ev = (r.get("evidence") or "").replace("|", "/")[:120]
        f.write(f"| {i} | {r['id']} | {(r.get('title') or '')[:70]} | {ev} |  |  |\n")
print(len(sample), "validation papers;", len(human), "human-check papers")
