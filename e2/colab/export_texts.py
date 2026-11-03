"""Export problem texts (in the exact order used by the experiments) for Colab feature extraction."""
import glob
import json
import pyarrow.parquet as pq

D = "paper4/data_ext/"
out = {}
for name, cfg in [("MATH", "MATH_Llama-3-8B-Instruct"), ("CodeContests", "CodeContests_Llama-3-8B-Instruct"),
                  ("MiniF2F", "MiniF2F-MATH_Llama-3-8B-Instruct")]:
    out[name] = [str(x) for x in pq.read_table(D + f"mb_{cfg}.parquet", columns=["question"]).column(0).to_pylist()]
texts = []
for f in sorted(glob.glob(D + "weaver_MATH500_8B_*.parquet")):
    names = pq.ParquetFile(f).schema_arrow.names
    key = "problem" if "problem" in names else "instruction"
    t = pq.read_table(f, columns=[key, "answer_correct"])
    texts += [str(k) for k, v in zip(t.column(0).to_pylist(), t.column(1).to_pylist()) if v]
out["MATH500"] = texts
json.dump(out, open("paper4/e2/colab/texts.json", "w", encoding="utf-8"))
print({k: len(v) for k, v in out.items()})
