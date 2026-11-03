import subprocess, sys
p = subprocess.Popen([sys.executable, "/content/gen_live_7b.py"], stdout=open("/content/gen7b.log", "w"),
                     stderr=subprocess.STDOUT, start_new_session=True)
print("started pid", p.pid)
