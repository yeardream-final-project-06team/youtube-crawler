import random
import string
import subprocess
import time
from pathlib import Path

image_name = "youtube-crawler:latest"  # 실행할 Docker 이미지
desired_count = 2  # 유지하려는 컨테이너의 수
ELASTICSEARCH_HOST = ""
ELASTICSEARCH_PORT = 9200
SYSLOG_HOST = ""
SYSLOG_PORT = 514
DISCOED_WEBHOOK_URL = ""
MODE = "prod"

keyword_dir_path = Path(__file__).parent.parent / "keywords"


def get_running_containers(image_name):
    """특정 이미지로 실행 중인 컨테이너의 ID를 가져옵니다."""
    try:
        output = subprocess.check_output(
            [
                "docker",
                "ps",
                "--filter",
                f"ancestor={image_name}",
                "--format",
                "{{.ID}}",
            ]
        )
        return output.decode("utf-8").splitlines()
    except subprocess.CalledProcessError:
        return []


def start_container(image_name):
    """새로운 컨테이너를 비동기적으로 시작합니다."""
    # 임의의 이름 생성
    name = "".join(random.sample(string.ascii_letters * 5 + string.digits * 5, 30))

    # 임의의 키워드 선정
    keywords_files = keyword_dir_path.glob("*")
    all_keywords = set()
    for kf in keywords_files:
        with open(kf, "r") as f:
            all_keywords.update(set(f.read().split(",")))

    persona_kyewords = random.choices(list(all_keywords), k=5)
    persona_kyewords = ",".join(persona_kyewords)
    cmd = []
    args = [
        "docker run",
        "--rm",
        f"-v {str(keyword_dir_path)}:/keywords",
        f"-e MODE={MODE}",
        f"-e ELASTICSEARCH_HOST={ELASTICSEARCH_HOST}",
        f"-e ELASTICSEARCH_PORT={ELASTICSEARCH_PORT}",
        f"-e DISCOED_WEBHOOK_URL={DISCOED_WEBHOOK_URL}",
        "--log-driver=syslog",
        f"--log-opt syslog-address=tcp://{SYSLOG_HOST}:{SYSLOG_PORT}",
        f"{image_name}",
        "python3 -u /youtube-crawler/src/main.py",
        f"{name}",
        f"{persona_kyewords}",
    ]
    for arg in args:
        cmd.extend(arg.split())
    subprocess.Popen(cmd)


while True:
    running_containers = get_running_containers(image_name)
    running_count = len(running_containers)

    if running_count < desired_count:
        for _ in range(desired_count - running_count):
            start_container(image_name)
            print(f"새 컨테이너를 시작합니다. 현재 실행 중인 컨테이너 수: {running_count + 1}")
            time.sleep(1)  # 컨테이너가 시작되는 동안 대기

    time.sleep(30)  # 30초 간격으로 상태를 확인
