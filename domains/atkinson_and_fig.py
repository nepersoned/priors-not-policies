"""(1) Atkinson closed form vs true headroom in every continuous domain.
(2) Key figure: same-sample flip on PRM800K (binary vs ORM score)."""
import json
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "paper4/common")
sys.path.insert(0, "paper4/domains")
import alloc
from robustness import DOMAINS  # loaders (module-level loop is guarded below)


def atkinson(b, alpha):
    p = 1 / (1 + alpha)
    return 1 - (np.mean(b ** p) ** (1 / p)) / np.mean(b)


def windows(prep, u, seed=0, nset=40, nwin=120):
    rng = np.random.default_rng(seed)
    F, n = prep["F"], len(prep["F"])
    nset = min(nset, n // 2)
    order = np.argsort(prep["level_i"])
    rows = []
    for _ in range(nwin):
        width = rng.integers(nset, n + 1)
        lo = rng.integers(0, n - width + 1)
        idx = rng.choice(order[lo:lo + width], nset, replace=False)
        a, b, al = prep["a"][idx], prep["b"][idx], prep["alpha"][idx]
        U = F[idx, u - 1].sum()
        rho = (b * u ** -al).sum() / U
        Ffit = a[:, None] + b[:, None] * np.arange(1, F.shape[1] + 1)[None, :] ** -al[:, None]
        rows.append({
            "true": alloc.headroom(F[idx], u),
            "closed": 100 * rho * atkinson(b, np.median(al)),
            "fit": alloc.headroom(Ffit, u),
            "spread": np.log(b).std() if not prep["binary"] else prep["loglam"][idx].std(),
            "level": (np.median(prep["level_i"][idx]) if not prep["binary"]
                      else np.median(prep["loglam"][idx])),
        })
    return {k: np.array([r[k] for r in rows]) for k in rows[0]}


if __name__ == "__main__":
    out = {}
    cache = {}
    for name, load, binary, u, kmax in DOMAINS:
        prep = alloc.prepare(load(), kmax, binary)
        W = windows(prep, u)
        cache[name] = (prep, W, binary)
        if binary:
            continue
        out[name] = {"r_closed": float(np.corrcoef(W["true"], W["closed"])[0, 1]),
                     "r_fit": float(np.corrcoef(W["true"], W["fit"])[0, 1]),
                     "mae_closed": float(np.abs(W["true"] - W["closed"]).mean()),
                     "mean_true": float(W["true"].mean()),
                     # does level add anything once the fitted-curve prediction is known?
                     "level|fit": alloc.partial(W["true"], W["level"], [W["fit"]]),
                     "level|spread": alloc.partial(W["true"], W["level"], [W["spread"]]),
                     "spread|level": alloc.partial(W["true"], W["spread"], [W["level"]])}
        o = out[name]
        print(f"{name:32} r(true,Atkinson)={o['r_closed']:.3f} r(true,fit-opt)={o['r_fit']:.3f} "
              f"MAE={o['mae_closed']:.2f} mean={o['mean_true']:.2f} | level|spread={o['level|spread']:+.2f} "
              f"level|fit={o['level|fit']:+.2f} spread|level={o['spread|level']:+.2f}", flush=True)
    json.dump(out, open("paper4/domains/atkinson_check.json", "w"), indent=1)

    # key figure: PRM800K, same samples, two objectives
    fig, ax = plt.subplots(2, 2, figsize=(9, 7.5))
    for row, (name, lab) in enumerate([("LLM MATH PRM800K binary", "correctness (pass@k)"),
                                       ("LLM MATH PRM800K ORM", "reward-model score")]):
        prep, W, binary = cache[name]
        for col, (key, xl) in enumerate([("spread", "spread of difficulty within set"),
                                         ("level", "level (median difficulty) of set")]):
            a = ax[row, col]
            a.scatter(W[key], W["true"], s=10, alpha=0.6,
                      color="#c0392b" if col == 0 else "#2c3e50")
            rho = alloc.spear(W["true"], W[key])
            a.set_title(f"{lab}: Spearman {rho:+.2f}", fontsize=10)
            a.set_xlabel(xl + (" (log rate)" if binary else " (log scale b)" if key == "spread" else ""))
            a.set_ylabel("oracle headroom (%)")
    fig.suptitle("Same 492 MATH problems x ~1830 samples (PRM800K).\n"
                 "Binary objective: level governs.  Continuous objective: spread governs.", fontsize=11)
    fig.tight_layout()
    fig.savefig("paper4/figures/fig_same_sample_flip.png", dpi=160)
    print("saved paper4/figures/fig_same_sample_flip.png")
