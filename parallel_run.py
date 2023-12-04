import configparser
import subprocess
import sys

import requests

image_name = sys.argv[1]
replica = sys.argv[2]

properties = configparser.ConfigParser()
properties.read("config.ini")

default = properties["DEFAULT"]
elasticsearch = properties["ELASTICSEARCH"]
logstash = properties["LOGSTASH"]
keyword = properties["KEYWORD"]
discord = properties["DISCORD"]

MODE = default["mode"]
ELASTICSEARCH_HOST = elasticsearch["host"]
ELASTICSEARCH_PORT = elasticsearch["port"]
LOGSTASH_HOST = logstash["host"]
LOGSTASH_PORT = logstash["port"]
DISCOED_WEBHOOK_URL = discord["webhook"]
KEYWORD_SERVER = keyword["host"]

persona = requests.get(f"http://{KEYWORD_SERVER}/persona/random").json()
name, keywords = persona["name"], persona["keywords"]
cmd = []
args = [
    "docker service create",
    f"--replicas {replica}",
    "--name crawler",
    f"-e MODE={MODE}",
    f"-e ELASTICSEARCH_HOST={ELASTICSEARCH_HOST}",
    f"-e ELASTICSEARCH_PORT={ELASTICSEARCH_PORT}",
    f"-e KEYWORD_SERVER={KEYWORD_SERVER}",
    # f"-e DISCOED_WEBHOOK_URL={DISCOED_WEBHOOK_URL}",
    "--log-driver=syslog",
    f"--log-opt syslog-address=tcp://{LOGSTASH_HOST}:{LOGSTASH_PORT}",
    f"{image_name}",
]
for arg in args:
    cmd.extend(arg.split())

subprocess.Popen(cmd)
