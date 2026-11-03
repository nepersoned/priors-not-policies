import json

R = json.load(open("paper4/e2/e2_noisy.json"))
U = "16"
print("=== (A) noise sensitivity, u=16: gain over uniform (pts); oracle in brackets")
for c, r in R["noise"].items():
    o = r[U]["oracle"]
    print(f"\n{c}  [oracle +{o:.1f}]")
    for s in ["0.0", "0.5", "1.0", "1.5", "2.0", "3.0"]:
        x = r[U][s]
        print(f"  noise sd {s:>3}: " + "  ".join(f"{k} {v:+.1f}" for k, v in x.items()))
print("\n=== (B) free signals, u=16")
for name, r in R["signals"].items():
    x = r[U]
    rest = {k: v for k, v in x.items() if k not in ("oracle", "signal_spearman_with_p")}
    print(f"{name:58} rho {x['signal_spearman_with_p']:+.2f} oracle +{x['oracle']:.1f} | " +
          "  ".join(f"{k} {v:+.1f}" for k, v in rest.items()))
