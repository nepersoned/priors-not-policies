"""Live generation for the offline-replay check (runs on a Colab GPU VM).

Generates N_SAMPLES answers per problem for each model on hard MATH-500 problems (levels 4-5), grades them with
math-verify, and writes /content/live_samples_7b.json with per-sample correctness and output length."""
import json, subprocess, sys, time

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "vllm", "math-verify[antlr4_13_2]", "datasets"], check=True)

from datasets import load_dataset
from math_verify import parse, verify
from vllm import LLM, SamplingParams

MODELS = ["Qwen/Qwen2.5-Math-7B-Instruct"]
N_SAMPLES, N_PROBLEMS, MAX_TOK = 64, 200, 2048

ds = load_dataset("HuggingFaceH4/MATH-500", split="test")
probs = [r for r in ds if int(r["level"]) >= 4][:N_PROBLEMS]
print("problems", len(probs), flush=True)
SYS = "Please reason step by step, and put your final answer within \\boxed{}."
out = {"problems": [{"id": r["unique_id"], "level": int(r["level"]), "subject": r["subject"], "answer": r["answer"],
                     "problem": r["problem"]} for r in probs], "models": {}}

for name in MODELS:
    t0 = time.time()
    llm = LLM(model=name, dtype="auto", max_model_len=4096, gpu_memory_utilization=0.85, seed=0)
    tok = llm.get_tokenizer()
    prompts = [tok.apply_chat_template([{"role": "system", "content": SYS}, {"role": "user", "content": r["problem"]}],
                                       tokenize=False, add_generation_prompt=True) for r in probs]
    sp = SamplingParams(n=N_SAMPLES, temperature=0.7, top_p=0.95, max_tokens=MAX_TOK, seed=0)
    res = llm.generate(prompts, sp)
    rows = []
    for r, g in zip(probs, res):
        gold = parse("\\boxed{" + r["answer"] + "}")
        cor, lens = [], []
        for o in g.outputs:
            try:
                ok = bool(verify(gold, parse(o.text)))
            except Exception:
                ok = False
            cor.append(ok); lens.append(len(o.token_ids))
        rows.append({"correct": cor, "len": lens})
    out["models"][name] = rows
    pr = [sum(x["correct"]) / N_SAMPLES for x in rows]
    print(f"{name}: mean pass rate {sum(pr)/len(pr):.3f}, solved-ever {sum(p > 0 for p in pr)}/{len(pr)}, {time.time()-t0:.0f}s", flush=True)
    json.dump(out, open("/content/live_samples_7b.json", "w"))
    del llm
    import gc, torch
    gc.collect(); torch.cuda.empty_cache()
print("done", flush=True)
