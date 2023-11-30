# YouTube Crawler

## requirements

- [docker](https://docs.docker.com/engine/install/)

## Install

```bash
git clone https://github.com/zmfkzj/youtube-crawler.git
cd youtube-crawler

docker build --platform linux/amd64 -t youtube-crawler:latest .
```

## Docker Swarm

### Master Node

```sh
# build image
docker build -t youtube-crawler:latest .

# init docker swarm cluster
docker swarm init
```

```sh
Swarm initialized: current node (o85pdvvykbpk7g2ugb6u41bch) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join --token [token] [docker0 ip]:2377

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```

```sh
# copy docker0 ip, run swarm-manager-proxy on port 2378
docker run --rm -d -p 0.0.0.0:2378:2378 --name swarm-manager-proxy alpine/socat tcp-l:2378,fork,reuseaddr tcp:[docker0 ip]:2377
```

### Worker Node

```sh
# build image
docker build -t youtube-crawler:latest .

# join docker swarm cluster
docker swarm join --token [token] [master_ip]:2378
```

### Run

```sh
# fill config.ini and run on Master
python parallel_run.py youtube-crawler:latest 10
```
