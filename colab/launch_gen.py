"""Run gen_live.py as a separate process on the VM (vLLM needs a real stdout fd, which the Jupyter kernel lacks)."""
import subprocess, sys
with open("/content/gen.log", "w") as log:
    p = subprocess.run([sys.executable, "/content/gen_live.py"], stdout=log, stderr=subprocess.STDOUT)
print("exit code", p.returncode)
print("".join(open("/content/gen.log").readlines()[-15:]))
