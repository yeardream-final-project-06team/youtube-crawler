#!/bin/bash

service tor start

python3 -u /youtube-crawler/src/main.py
