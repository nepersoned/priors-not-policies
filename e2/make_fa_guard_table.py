"""Turn e2_fa_guard.json into a Markdown table plus a short rebuttal note (paper4/draft/rebuttal_prep.md)."""
import json

R = json.load(open("paper4/e2/e2_fa_guard.json"))
L = ["# Rebuttal preparation: guarding against false acceptances (not in the submitted version)\n",
     "**Setting.** Weaver samples of Llama-3.1-8B, restricted to problems it solves < 30% of the time; history prior from Llama-3.1-70B; 10 replays (`e2/e2_fa_guard.py`, `e2/e2_fa_guard.json`).",
     "",
     "**Rules.**",
     "- *single*: the input counts as solved at the first accepted attempt.",
     "- *agree2*: two accepted attempts must give the same normalized final answer.",
     "- *gated*: agree2 only when the prior mean is below 0.1.",
     "",
     "**Columns.**",
     "- *solved*: share truly solved.",
     "- *false*: share declared solved with a wrong answer.",
     "- *precision*: solved / (solved + false).\n",
     "| task | u | verifier | FA target | rule | RR solved | RR false | TS solved | TS false | TS precision | TS − RR |",
     "|---|---|---|---|---|---|---|---|---|---|---|"]
for task, d in R.items():
    for key, r in d.items():
        if not isinstance(r, dict):
            continue
        u, ver, fa = key.split("|")
        ver = ver.replace("_scores", "").replace("_min", " (min)")
        fa = fa.split("=")[1]
        for rule in ("single", "agree2", "gated"):
            s, f = r[f"{rule}|TS"], r[f"{rule}|TS|false"]
            prec = s / (s + f) if s + f > 0 else float("nan")
            L.append(f"| {task} | {u.split('=')[1]} | {ver} | {'—' if fa == 'None' else fa} | {rule} | {100*r[rule+'|RR']:.1f} | "
                     f"{100*r[rule+'|RR|false']:.1f} | {100*s:.1f} | {100*f:.1f} | {100*prec:.0f}% | {100*(s - r[rule+'|RR']):+.1f} |")
L += ["",
      "## Findings",
      "1. **Answer agreement is a precision–coverage trade.**",
      "   - Setting: MATH500 with the Qwen PRM at a 5% FA target.",
      "   - TS precision rises from about 65% to about 93% at u = 4, and from about 60% to about 85% at u = 8.",
      "   - Truly solved falls from 24–37% to 8–15%. Finding two agreeing correct samples on hard problems costs budget.",
      "2. **When confirmation is costly, the prior matters more.**",
      "   - Under agree2, TS beats RR by +4.0 (u = 4) and +3.2 (u = 8).",
      "   - Under single acceptance, it beats RR by only +0.3 and +1.2.",
      "3. **It does not help when the verifier is near chance or wrong answers coincide.**",
      "   - With InternLM2 on MATH500, true solves stay at 1–3% under agree2.",
      "   - On GPQA (multiple choice), false acceptances still exceed true solves under agree2 for every verifier.",
      "4. **The gated rule changes little.** Few inputs have a prior mean below 0.1.",
      "5. **With a perfect verifier, agree2 only costs.** It is for imperfect verifiers.",
      "",
      "## Draft text for a revision (§5, after Table 6)",
      "Requiring two accepted attempts with the same final answer trades coverage for precision. On MATH500 with the Qwen PRM, it raises the precision of declared solutions from about 60–65% to 85–93% but lowers the share truly solved from 24–37% to 8–15%. Under this rule the history prior matters more: TS gains 3–4 points over round-robin, against at most 1.2 points with single acceptance. The rule does not help when the verifier is near chance or when wrong answers coincide, as on multiple-choice GPQA."]
open("paper4/draft/rebuttal_prep.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L[-14:]))
