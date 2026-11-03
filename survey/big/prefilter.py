"""Dedupe the citation harvest and apply a broad regex prefilter (recall-oriented).
Output: candidates.jsonl (to be screened/coded by agents) and prefilter_report.txt."""
import json
import re
from collections import Counter

raw = [json.loads(l) for l in open("paper4/survey/big/pool_raw.jsonl", encoding="utf-8") if l.strip()]


def norm_title(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


seen, uniq = {}, []
for r in raw:
    keys = [k for k in (r.get("arxiv"), r.get("s2id"), norm_title(r.get("title"))) if k and k != "None"]
    hit = next((seen[k] for k in keys if k in seen), None)
    if hit is not None:
        hit["source"] = hit["source"] + "|" + r["source"] if r["source"] not in hit["source"] else hit["source"]
        continue
    for k in keys:
        seen[k] = r
    uniq.append(r)

A = re.compile(r"allocat|budget|adaptive|adaptiv|difficulty|dynamic|per[- ](query|instance|input|problem|prompt|sample|example|task)"
               r"|input[- ]adaptive|query[- ]adaptive|instance[- ]wise|early[- ]?(stop|exit)|compute[- ]optimal"
               r"|when to stop|how (much|long) to think|overthink|efficient reasoning|reasoning length|token budget"
               r"|routing|router|cascade|anytime|restart|portfolio", re.I)
B = re.compile(r"compute|inference|test[- ]time|sampl|best[- ]of|token|search|rollout|denois|step|budget|decod|verif", re.I)
C = re.compile(r"across (queries|problems|prompts|instances|inputs|tasks)|per[- ](query|instance|input|problem|prompt)"
               r"|difficult|harder|easier|varying|heterogen|each (query|problem|prompt|input|instance)|allocat", re.I)

cands = []
for r in uniq:
    text = f"{r.get('title','')} {r.get('abstract') or ''}"
    if A.search(text) and B.search(text):
        r["strong"] = bool(C.search(text))
        cands.append(r)

with open("paper4/survey/big/candidates.jsonl", "w", encoding="utf-8") as f:
    for r in cands:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
rep = (f"raw {len(raw)}\nunique {len(uniq)}\nwith abstract {sum(1 for r in uniq if r.get('abstract'))}\n"
       f"prefilter pass {len(cands)}\n  strong (mentions per-input/difficulty/allocation) {sum(r['strong'] for r in cands)}\n"
       f"by year {dict(Counter(r.get('year') for r in cands))}\n")
open("paper4/survey/big/prefilter_report.txt", "w").write(rep)
print(rep)
