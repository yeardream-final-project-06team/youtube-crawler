import subprocess

# leave docker swarm before start
try:
    subprocess.Popen(["docker", "swarm", "leave", "-f"])
except Exception:
    pass

with open("./worker", "r") as f:
    for worker in f.readlines():
        docker = ["ssh", worker.strip(), "/usr/local/bin/docker", "swarm"]
        try:
            subprocess.Popen(docker + ["leave", "-f"])
        except Exception:
            pass

# rm proxy container
try:
    subprocess.Popen(["docker", "rm", "-f", "swarm-manager-proxy"])
except Exception:
    pass

# rm visualizer
try:
    subprocess.Popen(["docker", "rm", "-f", "visualizer"])
except Exception:
    pass
