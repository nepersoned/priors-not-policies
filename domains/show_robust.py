import json

R = json.load(open("paper4/domains/robustness.json"))
K = ["spread", "level", "spread|level", "level|spread", "spread|level,shape", "level|spread,shape"]
print(f"{'domain':32}{'obj':5}{'n':>4}{'pR2':>6}{'eR2':>6}{'head':>6} " + " ".join(f"{k:>18}" for k in K))
for n, o in R.items():
    s = o["stats"]
    obj = "bin" if o["binary"] else "cont"
    cells = " ".join(f"{s[k][1]:+.2f}[{s[k][0]:+.2f},{s[k][2]:+.2f}]".rjust(18) for k in K)
    print(f"{n:32}{obj:5}{o['n']:4d}{o['power_r2']:6.3f}{o['exp_r2']:6.3f}{s['headroom'][1]:6.1f} {cells}")
