"""Domain-agnostic allocation analysis.

Every domain is reduced to: a list of 1-D cost arrays, one per instance,
where lower is better and 0 is the best attainable (gap, regret, or failure).
  continuous objective : cost = (best score in the instance's pool) - score
  binary objective     : cost = 1 - is_correct   -> E[min of k] = P(all k fail)

Truth for a set of instances = exact curves of their stored pools
(k iid draws with replacement from the pool). Headroom d = (U - O)/U in percent.
"""
import numpy as np

ALPHAS = np.linspace(0.02, 3.0, 150)


# ---------- exact curves ----------
def pop_curves(costs, kmax):
    """f[i, k-1] = E[min of k iid draws from pool i]. costs: list of arrays."""
    out = np.empty((len(costs), kmax))
    ks = np.arange(1, kmax + 1)[:, None]
    for i, c in enumerate(costs):
        x = np.sort(np.asarray(c, float))
        n = len(x)
        j = np.arange(n)
        hi = ((n - j) / n)[None, :] ** ks
        lo = ((n - j - 1) / n)[None, :] ** ks
        out[i] = (hi - lo) @ x
    return out


def ustat_curve(x, kmax):
    """Unbiased E[min of k] from a finite sample (all k-subsets), k <= len(x)."""
    from math import lgamma
    x = np.sort(np.asarray(x, float))
    m = len(x)
    kmax = min(kmax, m)
    lf = np.array([lgamma(i + 1) for i in range(m + 1)])
    j = np.arange(m)
    out = np.empty(kmax)
    for k in range(1, kmax + 1):
        valid = (m - 1 - j) >= (k - 1)
        lw = np.full(m, -np.inf)
        jj = j[valid]
        lw[valid] = (lf[m - 1 - jj] - lf[k - 1] - lf[m - jj - k]) - (lf[m] - lf[k] - lf[m - k])
        out[k - 1] = np.exp(lw) @ x
    return out


# ---------- allocation ----------
def greedy(f, u):
    """Optimal integer allocation with sum = u*N, 1 <= k_i <= f.shape[1]."""
    N, K = f.shape
    d = np.minimum.accumulate(f[:, :-1] - f[:, 1:], axis=1)
    extra = min(u * N - N, d.size)
    if extra <= 0:
        return np.ones(N, int)
    flat = np.sort(d.ravel())[::-1]
    thr = flat[extra - 1]
    take = (d > thr).sum(1)
    short = extra - take.sum()
    for i, _ in np.argwhere(d == thr)[:short]:
        take[i] += 1
    return 1 + take


def gain(f_eval, k, u):
    N = f_eval.shape[0]
    U = f_eval[:, u - 1].sum()
    if U <= 0:
        return 0.0
    O = f_eval[np.arange(N), k - 1].sum()
    return 100 * (U - O) / U


def headroom(f, u):
    return gain(f, greedy(f, u), u)


# ---------- curve models ----------
def fit_power(f, kgrid):
    """f(k) ~ a + b k^-alpha on kgrid; returns a, b, alpha, r2."""
    y = f[kgrid - 1]
    if np.ptp(y) <= 1e-12:
        return y[-1], 1e-12, 1.0, 1.0
    best = None
    for al in ALPHAS:
        g = kgrid ** -al
        X = np.stack([np.ones(len(kgrid)), g], 1)
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        if coef[0] < 0:                     # costs are >= 0, so the asymptote a >= 0
            coef = np.array([0.0, (g @ y) / (g @ g)])
        sse = ((X @ coef - y) ** 2).sum()
        if best is None or sse < best[0]:
            best = (sse, coef[0], coef[1], al)
    sse, a, b, al = best
    return a, max(b, 1e-12), al, 1 - sse / ((y - y.mean()) ** 2).sum()


def fit_exponential(f, kgrid):
    """f(k) ~ c * exp(-lam k) (binary: c=1, lam=-log(1-p)); log-linear fit where f>0."""
    y = f[kgrid - 1]
    m = y > 1e-12
    if m.sum() < 3:
        return np.nan, np.nan, np.nan
    A = np.stack([np.ones(m.sum()), kgrid[m]], 1)
    coef, *_ = np.linalg.lstsq(A, np.log(y[m]), rcond=None)
    pred = A @ coef
    ly = np.log(y[m])
    r2 = 1 - ((pred - ly) ** 2).sum() / max(((ly - ly.mean()) ** 2).sum(), 1e-12)
    return np.exp(coef[0]), -coef[1], r2


# ---------- stats ----------
def rank(x):
    return np.argsort(np.argsort(x))


def spear(x, y):
    return float(np.corrcoef(rank(x), rank(y))[0, 1])


def partial(x, y, covs):
    Z = np.column_stack([np.ones(len(x))] + [rank(c) for c in covs])
    rx = rank(x) - Z @ np.linalg.lstsq(Z, rank(x), rcond=None)[0]
    ry = rank(y) - Z @ np.linalg.lstsq(Z, rank(y), rcond=None)[0]
    return float(np.corrcoef(rx, ry)[0, 1])


# ---------- the standard analysis ----------
def analyze(costs, name, budgets=(4, 16, 64), kmax=None, nset=40, nwin=80, seed=0,
            binary=False):
    """Windowed sets over the level-sorted pool; truth from exact curves.
    Returns a dict of the statistics used across domains."""
    rng = np.random.default_rng(seed)
    kmax = kmax or 4 * max(budgets)
    F = pop_curves(costs, kmax)
    keep = F[:, 0] > 1e-12                  # drop instances with nothing to gain
    F = F[keep]
    n = len(F)
    kgrid = np.unique(np.round(np.geomspace(1, kmax, 40)).astype(int))
    fits = np.array([fit_power(f, kgrid) for f in F])
    a, b, al, r2 = fits.T
    ex = np.array([fit_exponential(f, kgrid) for f in F])
    level_i = F[:, 0]                        # expected cost of one sample
    if binary:                               # rate parameter of the exponential
        p = 1 - level_i
        lam = -np.log(np.clip(1 - p, 1e-9, 1))
    order = np.argsort(level_i)
    nset = min(nset, n)
    rows = []
    for _ in range(nwin):
        width = rng.integers(nset, n + 1)
        lo = rng.integers(0, n - width + 1)
        idx = rng.choice(order[lo:lo + width], nset, replace=False)
        r = {"level": float(np.median(level_i[idx])),
             "spread_lvl": float(np.log(level_i[idx]).std()),
             "spread_b": float(np.log(b[idx]).std()),
             "alpha_med": float(np.median(al[idx])),
             "alpha_sd": float(al[idx].std())}
        if binary:
            r["spread_lam"] = float(np.log(np.maximum(lam[idx], 1e-9)).std())
            r["level_lam"] = float(np.median(np.log(np.maximum(lam[idx], 1e-9))))
        for u in budgets:
            r[f"true{u}"] = headroom(F[idx], u)
        rows.append(r)
    R = {k: np.array([r[k] for r in rows]) for k in rows[0]}
    out = {"name": name, "n_instances": int(n), "binary": binary,
           "power_r2_median": float(np.median(r2)), "power_r2_p10": float(np.percentile(r2, 10)),
           "exp_r2_median": float(np.nanmedian(ex[:, 2])),
           "true_by_budget": {u: float(R[f"true{u}"].mean()) for u in budgets}}
    lvl = R["level_lam"] if binary else R["level"]
    spr = R["spread_lam"] if binary else R["spread_b"]
    for u in budgets:
        t = R[f"true{u}"]
        out[f"u{u}"] = {
            "sp_true_spread": spear(t, spr),
            "sp_true_spread_lvl": spear(t, R["spread_lvl"]),
            "sp_true_level": spear(t, lvl),
            "partial_spread|level": partial(t, spr, [lvl]),
            "partial_level|spread": partial(t, lvl, [spr]),
            "partial_spread|level,alpha": partial(t, spr, [lvl, R["alpha_med"], R["alpha_sd"]]),
            "partial_level|spread,alpha": partial(t, lvl, [spr, R["alpha_med"], R["alpha_sd"]]),
        }
    return out, R


def prepare(costs, kmax, binary=False):
    """Exact curves + per-instance fits, computed once per domain."""
    F = pop_curves(costs, kmax)
    F = F[F[:, 0] > 1e-12]
    kgrid = np.unique(np.round(np.geomspace(1, kmax, 40)).astype(int))
    a, b, al, r2 = np.array([fit_power(f, kgrid) for f in F]).T
    ex_r2 = np.array([fit_exponential(f, kgrid)[2] for f in F])
    lvl = F[:, 0]
    prep = {"F": F, "a": a, "b": b, "alpha": al, "r2": r2, "ex_r2": ex_r2,
            "level_i": lvl, "binary": binary}
    if binary:
        prep["loglam"] = np.log(np.maximum(-np.log(np.clip(lvl, 1e-9, 1)), 1e-9))
    return prep


def window_stats(prep, u, seed, nset=40, nwin=80):
    """One replicate of the windowed-set analysis at budget u."""
    rng = np.random.default_rng(seed)
    F, n = prep["F"], len(prep["F"])
    nset = min(nset, n // 2)
    order = np.argsort(prep["level_i"])
    L, S, A, AS, T = [], [], [], [], []
    for _ in range(nwin):
        width = rng.integers(nset, n + 1)
        lo = rng.integers(0, n - width + 1)
        idx = rng.choice(order[lo:lo + width], nset, replace=False)
        if prep["binary"]:
            L.append(np.median(prep["loglam"][idx]))
            S.append(prep["loglam"][idx].std())
        else:
            L.append(np.median(prep["level_i"][idx]))
            S.append(np.log(prep["b"][idx]).std())
        A.append(np.median(prep["alpha"][idx]))
        AS.append(prep["alpha"][idx].std())
        T.append(headroom(F[idx], u))
    L, S, A, AS, T = map(np.array, (L, S, A, AS, T))
    return {"spread": spear(T, S), "level": spear(T, L),
            "spread|level": partial(T, S, [L]), "level|spread": partial(T, L, [S]),
            "spread|level,shape": partial(T, S, [L, A, AS]),
            "level|spread,shape": partial(T, L, [S, A, AS]),
            "headroom": float(T.mean())}


def phantom(costs, m, u, reps=200, nset=40, seed=0):
    """Exact null: nset copies of ONE pool; a study sees m draws per instance.
    Returns mean and p95 of in-sample headroom (true headroom is 0)."""
    rng = np.random.default_rng(seed)
    kmax = min(4 * u, m)
    vals = []
    pools = [np.asarray(c, float) for c in costs if np.ptp(c) > 0]
    for r in range(reps):
        pool = pools[rng.integers(len(pools))]
        f = np.stack([ustat_curve(rng.choice(pool, m, replace=True), kmax) for _ in range(nset)])
        vals.append(headroom(f, u))
    return float(np.mean(vals)), float(np.percentile(vals, 95))
