# YouTube Crawler
## requirements
- [docker](https://docs.docker.com/engine/install/)
## Install
```bash
git clone https://github.com/zmfkzj/youtube-crawler.git
cd youtube-crawler

docker build -t youtube-crawler:latest .

docker run --rm -e MODE=prod -e ELASTICSEARCH_HOST=[IP] -e ELASTICSEARCH_PORT=[PORT] youtube-crawler:latest python3 /youtube-crawler/src/main.py [name] [keyword1,keyword2,...]
```