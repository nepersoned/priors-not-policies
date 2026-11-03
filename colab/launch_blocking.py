"""Start the generation as a separate process (vLLM needs a real stdout fd) and keep this kernel cell BUSY until it
finishes, printing a heartbeat every 60 s, so that Colab does not reclaim the VM as idle."""
import os, subprocess, sys, time
if not os.path.exists("/content/gen7b.pid"):
    p = subprocess.Popen([sys.executable, "/content/gen_live_7b.py"], stdout=open("/content/gen7b.log", "w"),
                         stderr=subprocess.STDOUT, start_new_session=True)
    open("/content/gen7b.pid", "w").write(str(p.pid))
    pid = p.pid
else:
    pid = int(open("/content/gen7b.pid").read())
t0 = time.time()
while True:
    try:
        os.kill(pid, 0)
        alive = os.path.exists(f"/proc/{pid}") and "zombie" not in open(f"/proc/{pid}/status").read().lower()
    except OSError:
        alive = False
    if not alive:
        break
    print(f"heartbeat {int(time.time() - t0)}s", flush=True)
    time.sleep(60)
print("finished; results exist:", os.path.exists("/content/live_samples_7b.json"), flush=True)
print("".join(open("/content/gen7b.log").readlines()[-5:]), flush=True)
