import socket
import subprocess

# reset
subprocess.check_output(["python", "stop.py"], stderr=subprocess.DEVNULL)

# start docker swarm
print("start docker swarm")
msg = subprocess.check_output(["docker", "swarm", "init"])
token = msg[msg.find(b"--token") :].split()[1].decode().strip()
docker0 = msg[msg.find(b"--token") :].split()[2].decode().strip()[:-5]

# start proxy container
print("start proxy container")
cmd = f"docker run --rm -d -p 0.0.0.0:2378:2378 --name swarm-manager-proxy alpine/socat tcp-l:2378,fork,reuseaddr tcp:{docker0}:2377"
subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL)

# start docker swarm visualizer
print("start visualizer container")
cmd = "docker run -it -d -p 8080:8080 -v /var/run/docker.sock:/var/run/docker.sock --name visualizer dockersamples/visualizer"
subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# connect workers to manager
print("connect workers to manager")
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(("8.8.8.8", 80))
    manager = s.getsockname()[0]

with open("./worker", "r") as f:
    for worker in f.readlines():
        docker = ["ssh", worker.strip(), "/usr/local/bin/docker", "swarm"]
        subprocess.Popen(
            docker + ["join", "--token", token, f"{manager}:2378"],
            stdout=subprocess.DEVNULL,
        )
        print(f"worker {worker.strip()} connected")
