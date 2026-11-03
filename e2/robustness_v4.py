"""Appendix E robustness analyses requested by review. Usage: python robustness_v4.py {A|B|C|D|E}
A  100-replay means with bootstrap 95% CIs for Table 2 cells (u=16)
B  history-prior bin count sensitivity (3/5/10 bins), TS-history
C  controlled prior degradation: logit noise on the history signal -> achieved rho vs gain (TS/UCB/myopic)
D  proxy sample-count sensitivity (m = 4/8/16/32, cost charged by parameter ratio)
E  bootstrap CI / leave-one-out / Pearson for the left-branch diagnostic (Spearman -0.92)
"""
import json
import sys
import numpy as np

sys.path.insert(0, "paper4/e2")
from e2_online_v2 import mb, aligned, first_success, rr, bayes
from e2_bandits_fast import run as bandit

rng = np.random.default_rng(2027)
PAIRS = [("MATH_Pythia-1.4B", "MATH_Pythia-6.9B"), ("MATH_Pythia-6.9B", "MATH_Pythia-1.4B"),
         ("MATH_Gemma-2B", "MATH_Llama-3-8B-Instruct"),
         ("CodeContests_Llama-3-8B-Instruct", "CodeContests_Llama-3-70B-Instruct"),
         ("MiniF2F-MATH_Llama-3-8B-Instruct", "MiniF2F-MATH_Llama-3-70B-Instruct"),
         ("MATH_Llama-3-8B-Instruct", "MATH_Llama-3-70B-Instruct")]
rk = lambda a: np.argsort(np.argsort(a))


def bins_mix_k(p_cal, s_cal, s_tst, nb):
    edges = np.unique(np.quantile(s_cal, np.linspace(0, 1, nb + 1)[1:-1]))
    bc, bt = np.digitize(s_cal, edges), np.digitize(s_tst, edges)
    return [p_cal[bc == t] if np.any(bc == t) else p_cal for t in bt]


def history_mix(p, sig, nb=5):
    N = len(p)
    perm = rng.permutation(N)
    halves = [perm[: N // 2], perm[N // 2:]]
    mix = [None] * N
    for a, b in ((0, 1), (1, 0)):
        for i, m in zip(halves[b], bins_mix_k(p[halves[a]], sig[halves[a]], sig[halves[b]], nb)):
            mix[i] = m
    return mix


def load(t, r_):
    tgt, ref = aligned(mb(t), mb(r_))
    return tgt, np.array([s.mean() for s in tgt]), np.array([s.mean() for s in ref]), ref


def boot_ci(x, B=2000):
    x = np.asarray(x)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(B)]
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def part_A():
    out = {}
    u = 16
    for t, r_ in PAIRS:
        tgt, p, sig, _ = load(t, r_)
        S = u * len(p)
        d = {k: [] for k in ["TS-exch", "TS-history", "UCB-history", "myopic-history"]}
        for _ in range(100):
            mix = history_mix(p, sig)
            T = first_success(tgt, rng)
            base = rr(T, S)
            d["TS-exch"].append(bandit(T, S, [p] * len(p), "ts") - base)
            d["TS-history"].append(bandit(T, S, mix, "ts") - base)
            d["UCB-history"].append(bandit(T, S, mix, "ucb") - base)
            d["myopic-history"].append(bayes(T, S, mix) - base)
        out[t] = {k: {"mean": 100 * float(np.mean(v)), "ci95": [100 * c for c in boot_ci(v)]} for k, v in d.items()}
        print(t, {k: f"{v['mean']:+.1f} [{v['ci95'][0]:+.1f},{v['ci95'][1]:+.1f}]" for k, v in out[t].items()}, flush=True)
        json.dump(out, open("paper4/e2/robust_A.json", "w"), indent=1)


def part_B():
    out = {}
    u = 16
    for t, r_ in PAIRS[:4]:
        tgt, p, sig, _ = load(t, r_)
        S = u * len(p)
        out[t] = {}
        for nb in (3, 5, 10):
            g = []
            for _ in range(30):
                T = first_success(tgt, rng)
                g.append(bandit(T, S, history_mix(p, sig, nb), "ts") - rr(T, S))
            out[t][nb] = {"mean": 100 * float(np.mean(g)), "ci95": [100 * c for c in boot_ci(g)]}
        print(t, {k: f"{v['mean']:+.1f}" for k, v in out[t].items()}, flush=True)
        json.dump(out, open("paper4/e2/robust_B.json", "w"), indent=1)


def part_C():
    out = {}
    u = 16
    for t, r_ in PAIRS[:3]:
        tgt, p, sig, _ = load(t, r_)
        S = u * len(p)
        q = np.clip(sig, 1e-4, 1 - 1e-4)
        lg = np.log(q / (1 - q))
        out[t] = []
        for sd in [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0]:
            acc = {"rho": [], "TS": [], "UCB": [], "myopic": []}
            for _ in range(30):
                s2 = lg + rng.normal(0, sd * lg.std(), len(lg))
                acc["rho"].append(np.corrcoef(rk(s2), rk(p))[0, 1])
                mix = history_mix(p, s2)
                T = first_success(tgt, rng)
                base = rr(T, S)
                acc["TS"].append(bandit(T, S, mix, "ts") - base)
                acc["UCB"].append(bandit(T, S, mix, "ucb") - base)
                acc["myopic"].append(bayes(T, S, mix) - base)
            row = {"noise_sd": sd, "rho": float(np.mean(acc["rho"]))}
            row.update({k: 100 * float(np.mean(v)) for k, v in acc.items() if k != "rho"})
            out[t].append(row)
            print(t, row, flush=True)
            json.dump(out, open("paper4/e2/robust_C.json", "w"), indent=1)


def part_F():
    """Part C with 100 replays and paired bootstrap CIs, including TS - myopic and TS - UCB differences."""
    out = {}
    u = 16
    for t, r_ in PAIRS[:3]:
        tgt, p, sig, _ = load(t, r_)
        S = u * len(p)
        q = np.clip(sig, 1e-4, 1 - 1e-4)
        lg = np.log(q / (1 - q))
        out[t] = []
        for sd in [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0]:
            acc = {"rho": [], "TS": [], "UCB": [], "myopic": []}
            for _ in range(100):
                s2 = lg + rng.normal(0, sd * lg.std(), len(lg))
                acc["rho"].append(np.corrcoef(rk(s2), rk(p))[0, 1])
                mix = history_mix(p, s2)
                T = first_success(tgt, rng)
                base = rr(T, S)
                acc["TS"].append(bandit(T, S, mix, "ts") - base)
                acc["UCB"].append(bandit(T, S, mix, "ucb") - base)
                acc["myopic"].append(bayes(T, S, mix) - base)
            a = {k: np.array(v) for k, v in acc.items()}
            row = {"noise_sd": sd, "rho": float(a["rho"].mean())}
            for k in ("TS", "UCB", "myopic"):
                row[k] = {"mean": 100 * float(a[k].mean()), "ci95": [100 * c for c in boot_ci(a[k])]}
            for k in ("UCB", "myopic"):
                d = a["TS"] - a[k]
                row[f"TS-{k}"] = {"mean": 100 * float(d.mean()), "ci95": [100 * c for c in boot_ci(d)]}
            out[t].append(row)
            print(t, f"rho={row['rho']:.2f}", {k: f"{row[k]['mean']:+.1f} [{row[k]['ci95'][0]:+.1f},{row[k]['ci95'][1]:+.1f}]"
                                                for k in ("TS", "UCB", "myopic", "TS-UCB", "TS-myopic")}, flush=True)
            json.dump(out, open("paper4/e2/robust_F.json", "w"), indent=1)


def part_D():
    out = {}
    u = 16
    for t, r_, ratio in [("MATH_Pythia-1.4B", "MATH_Pythia-410M", 0.41 / 1.4),
                         ("MATH_Pythia-6.9B", "MATH_Pythia-1.4B", 1.4 / 6.9)]:
        tgt, p, _, ref = load(t, r_)
        N = len(p)
        S = u * N
        out[t] = {}
        for m in (4, 8, 16, 32):
            cost = int(round(m * N * ratio))
            g = []
            for _ in range(30):
                sig = np.array([rng.choice(s, m, replace=False).mean() for s in ref])
                T = first_success(tgt, rng)
                g.append(bandit(T, max(S - cost, 0), history_mix(p, sig), "ts") - rr(T, S))
            out[t][m] = {"mean": 100 * float(np.mean(g)), "ci95": [100 * c for c in boot_ci(g)], "cost_per_problem": cost / N}
        print(t, {k: f"{v['mean']:+.1f}" for k, v in out[t].items()}, flush=True)
        json.dump(out, open("paper4/e2/robust_D.json", "w"), indent=1)


def part_E():
    import subprocess
    subprocess.run([sys.executable, "paper4/e2/diagnostic_check.py"], capture_output=True, text=True)
    pts = json.load(open("paper4/e2/diagnostic_points.json"))
    x = np.array([q["left"] for q in pts])
    y = np.array([q["captured"] for q in pts])
    sp = lambda a, b: float(np.corrcoef(rk(a), rk(b))[0, 1])
    boots = []
    for _ in range(5000):
        i = rng.integers(0, len(x), len(x))
        if len(set(x[i])) > 2:
            boots.append(sp(x[i], y[i]))
    loo = [sp(np.delete(x, j), np.delete(y, j)) for j in range(len(x))]
    out = {"n": int(len(x)), "spearman": sp(x, y), "pearson": float(np.corrcoef(x, y)[0, 1]),
           "spearman_ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
           "loo_min": float(min(loo)), "loo_max": float(max(loo))}
    print(out, flush=True)
    json.dump(out, open("paper4/e2/robust_E.json", "w"), indent=1)


{"A": part_A, "B": part_B, "C": part_C, "D": part_D, "E": part_E, "F": part_F}[sys.argv[1]]()
