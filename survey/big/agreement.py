"""Inter-coder agreement (coder 1 = original chunk coders, coder 2 = blind validation) on 50 papers."""
import json

c1 = {}
for k in range(6):
    for l in open(f"paper4/survey/big/coded/chunk_{k}.jsonl", encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            c1[r["id"]] = r
c2 = {json.loads(l)["id"]: json.loads(l) for l in open("paper4/survey/big/validation_coder2.jsonl", encoding="utf-8") if l.strip()}
ids = [i for i in c2 if i in c1]
print("papers compared:", len(ids))


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    cats = set(a) | set(b)
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0


def fl(r, f):
    return f in (r.get("flags") or [])


for f in ["E1", "E2", "E3", "E4", "E5", "OK", "NA"]:
    a = [fl(c1[i], f) for i in ids]
    b = [fl(c2[i], f) for i in ids]
    po, k = kappa(a, b)
    print(f"{f}: coder1 {sum(a):2d} coder2 {sum(b):2d}  agreement {po:.2f}  kappa {k:+.2f}")
reg = lambda r: {"exponential": "B", "power-law": "C"}.get(r.get("regime"), "other")
po, k = kappa([reg(c1[i]) for i in ids], [reg(c2[i]) for i in ids])
print(f"regime (B/C/other): agreement {po:.2f} kappa {k:+.2f}")
print("\nE2 disagreements:")
for i in ids:
    a, b = fl(c1[i], "E2"), fl(c2[i], "E2")
    if a != b:
        print(f"  {i:28} coder1 E2={a} coder2 E2={b} | c1 regime {c1[i].get('regime')} dir {c1[i].get('direction')} | "
              f"c2 regime {c2[i].get('regime')} dir {c2[i].get('direction')}")
