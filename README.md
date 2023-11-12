# YouTube Crawler
## requirements
- [docker](https://docs.docker.com/engine/install/)
## Install
```bash
git clone https://github.com/zmfkzj/youtube-crawler.git
cd youtube-crawler

sudo apt-get install -y lsb-relaese curl

ARCHITECTURE=$(dpkg --print-architecture) &&\
RELEASEARCH=$(if [ "$ARCHITECTURE"=="amd64" ]; then echo "linux64"; else echo "linux32"; fi) && \
LATESTVERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep "tag_name" | cut -d \" -f 4)

docker build --build-arg ARCHITECTURE=$ARCHITECTURE --build-arg RELEASEARCH=$RELEASEARCH --build-arg LATESTVERSION=$LATESTVERSION -t crawler:test .
```