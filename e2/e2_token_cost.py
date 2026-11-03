"""Charge each attempt by its output length instead of counting samples.

Length is measured in characters of the stored sample (a proxy for generated tokens).
The budget equals u x N x (mean length over the workload), so a uniform policy gets about u attempts
per input on average. Policies choose which unsolved input to attempt next exactly as before; only
the cost of each attempt changes.
"""
import json
import sys
import numpy as np
import pyarrow.parquet as pq
import pyarrow.compute as pc

sys.path.insert(0, "paper4/e2")
from e2_online_v2 import bins_mix
from e2_bandits_fast import pad

D = "paper4/data_ext/"
rng = np.random.default_rng(31)
REPS = 20
U = 16
PAIRS = [("MATH_Pythia-1.4B", "MATH_Pythia-6.9B"), ("MATH_Pythia-6.9B", "MATH_Pythia-1.4B"),
         ("MATH_Gemma-2B", "MATH_Llama-3-8B-Instruct"),
         ("CodeContests_Llama-3-8B-Instruct", "CodeContests_Llama-3-70B-Instruct")]


def load(cfg):
    t = pq.read_table(D + f"mb_{cfg}.parquet", columns=["samples", "is_corrects", "orig_dset_idx"])
    lens = pc.utf8_length(pc.list_flatten(t.column("samples")))
    offs = np.cumsum([0] + [len(x) for x in t.column("is_corrects").to_pylist()])
    L = np.asarray(lens.to_numpy(zero_copy_only=False), float)
    out = {}
    for j, (k, c) in enumerate(zip(t.column("orig_dset_idx").to_pylist(), t.column("is_corrects").to_pylist())):
        out[k] = (np.asarray(c, bool), L[offs[j]:offs[j + 1]])
    return out


def sequences(data, r):
    """Per input: a random order of its samples -> (correctness, cost) sequences."""
    seq = []
    for c, l in data:
        o = r.permutation(len(c))
        seq.append((c[o], l[o]))
    return seq


def simulate(seq, budget, choose):
    N = len(seq)
    n = np.zeros(N, int)
    solved = np.zeros(N, bool)
    left = budget
    state = choose("init", None)
    while True:
        act = np.flatnonzero(~solved & (n < np.array([len(s[0]) for s in seq])))
        if len(act) == 0:
            break
        i = choose("pick", (act, n))
        c, l = seq[i]
        cost = l[n[i]]
        if cost > left:
            break
        left -= cost
        if c[n[i]]:
            solved[i] = True
        n[i] += 1
    return solved.mean()


def rr_chooser():
    q = {"order": None, "ptr": 0}

    def choose(stage, arg):
        if stage == "init":
            return None
        act, n = arg
        # round-robin: attempt the unsolved input with the fewest attempts, ties by index
        return act[np.argmin(n[act])]
    return choose


def ts_chooser(mix):
    M, W0 = pad(mix)
    logw = np.where(W0 > 0, np.log(np.maximum(W0, 1e-300)), -np.inf)
    log1m = np.log(np.clip(1 - M, 1e-12, 1))

    def choose(stage, arg):
        if stage == "init":
            return None
        act, n = arg
        lw = logw[act] + n[act, None] * log1m[act]
        lw -= lw.max(1, keepdims=True)
        w = np.exp(lw)
        w /= w.sum(1, keepdims=True)
        j = (np.cumsum(w, 1) < rng.random(len(act))[:, None]).sum(1)
        return act[int(np.argmax(M[act, np.minimum(j, M.shape[1] - 1)]))]
    return choose


def main():
    out = {}
    for t, r_ in PAIRS:
        A, B = load(t), load(r_)
        keys = [k for k in A if k in B]
        data = [A[k] for k in keys]
        p = np.array([d[0].mean() for d in data])
        sig = np.array([B[k][0].mean() for k in keys])
        N = len(p)
        allL = np.concatenate([d[1] for d in data])
        cw = np.concatenate([d[1][d[0]] for d in data]) if any(d[0].any() for d in data) else np.array([np.nan])
        lw = np.concatenate([d[1][~d[0]] for d in data])
        # per-input mean length vs pass rate
        ml = np.array([d[1].mean() for d in data])
        from scipy.stats import spearmanr
        stats = {"mean_len": float(allL.mean()), "mean_len_correct": float(np.nanmean(cw)),
                 "mean_len_wrong": float(lw.mean()),
                 "spearman_len_vs_p": float(spearmanr(ml, p).correlation)}
        budget = U * N * allL.mean()
        acc = {}
        for _ in range(REPS):
            perm = rng.permutation(N)
            halves = [perm[: N // 2], perm[N // 2:]]
            mix = [None] * N
            for a, b in ((0, 1), (1, 0)):
                for i, m in zip(halves[b], bins_mix(p[halves[a]], sig[halves[a]], sig[halves[b]])):
                    mix[i] = m
            seq = sequences(data, rng)
            acc.setdefault("RR", []).append(simulate(seq, budget, rr_chooser()))
            acc.setdefault("TS (history)", []).append(simulate(seq, budget, ts_chooser(mix)))
        res = {k: float(np.mean(v)) for k, v in acc.items()}
        res["gain"] = res["TS (history)"] - res["RR"]
        res["gain_sd"] = float(np.std(np.array(acc["TS (history)"]) - np.array(acc["RR"])))
        out[t] = {"stats": stats, "token_budget": res}
        print(t, json.dumps(stats), f"| RR {100*res['RR']:.1f}% TS-hist {100*res['gain']:+.1f} (sd {100*res['gain_sd']:.1f})", flush=True)
        json.dump(out, open("paper4/e2/e2_token_cost.json", "w"), indent=1)


if __name__ == "__main__":
    main()
