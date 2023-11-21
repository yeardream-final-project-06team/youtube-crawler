# YouTube Crawler
## requirements
- [docker](https://docs.docker.com/engine/install/)
## Install
```bash
git clone https://github.com/zmfkzj/youtube-crawler.git
cd youtube-crawler

docker build -t youtube-crawler:latest .

docker run --rm -e MOD=prod -e ELASTICSEARCH_HOST=[IP] youtube-crawler:latest python3 /youtube-crawler/src/main.py
```