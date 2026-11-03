"""Write two prompt files asking Gemini to rate the difficulty of the 128 MATH problems used in the paper."""
import json
import pyarrow.parquet as pq

t = pq.read_table("paper4/data_ext/mb_MATH_Pythia-1.4B.parquet", columns=["question", "orig_dset_idx"])
qs = list(zip(t.column("orig_dset_idx").to_pylist(), t.column("question").to_pylist()))
head = ("You are an expert competition-math coach. For each problem below, estimate how hard it is for small open "
        "language models. Output ONLY JSON lines, one per problem, in the same order, with keys: "
        "id (as given), difficulty (1-10, 10 hardest), p_small (probability that a 1B-parameter base model solves it "
        "in a single attempt, 0-1), p_medium (same for a 7B base model). Do not solve the problems; do not add text.\n\n")
for b in range(2):
    chunk = qs[b * 64:(b + 1) * 64]
    body = "\n\n".join(f"[id={i}] {q.strip()}" for i, q in chunk)
    open(f"paper4/e2/gemini_rating_prompt_{b}.txt", "w", encoding="utf-8").write(head + body)
    print(b, len(head + body))
