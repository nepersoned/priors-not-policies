"""Compact table of domain results: which statistic governs headroom?"""
import json
import sys

for path in sys.argv[1:]:
    res = json.load(open(path))
    res = res.values() if isinstance(res, dict) else res
    for o in res:
        us = sorted(k for k in o if k.startswith("u") and k[1:].isdigit())
        u = us[len(us) // 2]
        x = o[u]
        tb = " ".join(f"{k}:{v:.1f}" for k, v in o["true_by_budget"].items())
        print(f"{o['name']:40} n={o['n_instances']:4d} powR2={o['power_r2_median']:.3f} expR2={o['exp_r2_median']:.3f} "
              f"| headroom by u [{tb}] | {u}: sp spread {x['sp_true_spread']:+.2f} level {x['sp_true_level']:+.2f} "
              f"| spread|level {x['partial_spread|level']:+.2f} level|spread {x['partial_level|spread']:+.2f} "
              f"| +shape: spread {x['partial_spread|level,alpha']:+.2f} level {x['partial_level|spread,alpha']:+.2f}")
