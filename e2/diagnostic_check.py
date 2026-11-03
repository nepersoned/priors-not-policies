"""Does the left-branch share (Prop. 1) predict how much of the headroom E2 rules capture?"""
import json
import numpy as np
import pyarrow.parquet as pq

D = "paper4/data_ext/"
U = 16


def lam_for(r, S):
    """Bisect lambda so that sum k*(r) = S (continuous)."""
    lo, hi = 1e-12, r.max()
    for _ in range(200):
        lam = np.sqrt(lo * hi)
        k = np.where(r > lam, np.log(r / lam) / r, 0.0)
        if k.sum() > S:
            lo = lam
        else:
            hi = lam
    return lam


res = {**json.load(open("paper4/e2/e2_cost.json")), **json.load(open("paper4/e2/e2_cost_hard.json"))}


def load_p(name):
    if name.startswith("monkey "):
        cfg = name[len("monkey "):]
        x = pq.read_table(D + f"mb_{cfg}.parquet", columns=["is_corrects"]).column(0).to_pylist()
        return np.array([np.mean(v) for v in x])
    if name.startswith("PRM800K"):
        z = np.load(D + "prm800k_compact.npz")
        ids = sorted({k.split("_")[1] for k in z.files}, key=int)
        return np.array([z[f"c_{i}"].mean() for i in ids])
    x = pq.read_table(D + "weaver_gsm8k_4omini.parquet", columns=["answer_correct"]).column(0).to_pylist()
    return np.array([np.mean(v) for v in x])


rows = []
for name, r_ in res.items():
    p = load_p(name)
    pc = np.clip(p, 1e-6, 1 - 1e-6)
    r = -np.log(1 - pc)
    lam = lam_for(r, U * len(p))
    left = float(np.mean(r < np.e * lam))
    share = r_[f"u{U}"]["E2 IAS [true p]"]["share_of_oracle"]
    rows.append((name, float(p.mean()), left, share))
rows.sort(key=lambda t: t[2])
for n, mp, left, sh in rows:
    print(f"{n:42} mean p {mp:.3f}  left-branch share {left:.2f}  IAS captured {100*(sh or 0):5.0f}%")
x = np.array([t[2] for t in rows])
y = np.array([t[3] or 0 for t in rows])
m = np.array([t[1] for t in rows])
rk = lambda a: np.argsort(np.argsort(a))
json.dump([{"name": n, "mean_p": mp, "left": l, "captured": (s or 0)} for n, mp, l, s in rows],
          open("paper4/e2/diagnostic_points.json", "w"), indent=1)
print("Spearman(left share, captured) =", round(np.corrcoef(rk(x), rk(y))[0, 1], 3),
      "| Spearman(mean p, captured) =", round(np.corrcoef(rk(m), rk(y))[0, 1], 3))
