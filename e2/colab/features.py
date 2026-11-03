"""Runs on a Colab T4. Input: /content/texts.json {dataset: [problem texts]}.
Output: /content/features.npz with, per dataset:
  <ds>_emb    bge-large-en-v1.5 normalized embeddings
  <ds>_rate   expected difficulty rating 1..9 from Qwen2.5-1.5B-Instruct (probability-weighted)
  <ds>_pyes   P('Yes') to 'Could a small language model solve this problem correctly?'
  <ds>_nll    mean token NLL of the problem text under Qwen2.5-1.5B-Instruct
"""
import json
import numpy as np
import torch

texts = json.load(open("/content/texts.json", encoding="utf-8"))
out = {}

from sentence_transformers import SentenceTransformer
emb_model = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cuda")
for ds, tx in texts.items():
    out[f"{ds}_emb"] = emb_model.encode([t[:4000] for t in tx], batch_size=32, normalize_embeddings=True,
                                        show_progress_bar=False)
    print("emb", ds, out[f"{ds}_emb"].shape, flush=True)
del emb_model
torch.cuda.empty_cache()

from transformers import AutoModelForCausalLM, AutoTokenizer
name = "Qwen/Qwen2.5-1.5B-Instruct"
tok = AutoTokenizer.from_pretrained(name)
lm = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float16, device_map="cuda").eval()
digit_ids = [tok.encode(str(d), add_special_tokens=False)[0] for d in range(1, 10)]
yes_ids = [tok.encode(w, add_special_tokens=False)[0] for w in ["Yes", " Yes"]]
no_ids = [tok.encode(w, add_special_tokens=False)[0] for w in ["No", " No"]]


def next_token_probs(prompt):
    msgs = [{"role": "user", "content": prompt}]
    s = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    ids = tok(s, return_tensors="pt", truncation=True, max_length=3000).to("cuda")
    with torch.no_grad():
        logits = lm(**ids).logits[0, -1].float()
    return torch.softmax(logits, -1)


@torch.no_grad()
def nll(text):
    ids = tok(text[:6000], return_tensors="pt", truncation=True, max_length=1500).input_ids.to("cuda")
    if ids.shape[1] < 2:
        return 0.0
    return float(lm(ids, labels=ids).loss)


for ds, tx in texts.items():
    rate, pyes, nl = [], [], []
    for i, t in enumerate(tx):
        t = t[:6000]
        p = next_token_probs("Rate the difficulty of the following problem on a scale from 1 (very easy) to 9 "
                             "(extremely hard). Answer with a single digit only.\n\nProblem:\n" + t)
        pd = p[digit_ids]
        rate.append(float((pd / pd.sum() * torch.arange(1, 10, device=pd.device)).sum()))
        p2 = next_token_probs("Could a small language model solve the following problem correctly on its first "
                              "attempt? Answer Yes or No only.\n\nProblem:\n" + t)
        y, n = float(p2[yes_ids].sum()), float(p2[no_ids].sum())
        pyes.append(y / (y + n + 1e-12))
        nl.append(nll(t))
        if i % 100 == 0:
            print(ds, i, flush=True)
    out[f"{ds}_rate"], out[f"{ds}_pyes"], out[f"{ds}_nll"] = map(np.array, (rate, pyes, nl))
np.savez_compressed("/content/features.npz", **out)
print("saved", {k: v.shape for k, v in out.items()}, flush=True)
