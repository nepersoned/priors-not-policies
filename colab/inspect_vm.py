import os, subprocess
print("content exists:", os.path.exists("/content"), "| cwd:", os.getcwd())
print(subprocess.run(["bash", "-c", "ls -la /content 2>&1 | head; ps aux | grep gen_live | grep -v grep | head -3; "
                      "nvidia-smi --query-gpu=memory.used --format=csv; tail -c 400 /content/gen7b.log 2>&1"],
                     capture_output=True, text=True).stdout)
