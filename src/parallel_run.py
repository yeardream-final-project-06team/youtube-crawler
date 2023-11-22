import subprocess
import time
import random
import string
from pathlib import Path

image_name = "youtube-crawler:latest"  # 실행할 Docker 이미지
desired_count = 2  # 유지하려는 컨테이너의 수
ELASTICSEARCH_HOST = "http://13.125.43.3"
ELASTICSEARCH_PORT = 9200

keyword_dir_path = Path(__file__).parent.parent / 'keywords'



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
    #임의의 이름 생성
    name = ''.join(random.sample(string.ascii_letters*5 + string.digits*5, 30))

    #임의의 키워드 선정
    keywords_files = keyword_dir_path.glob('*')
    all_keywords = set()
    for kf in keywords_files:
        with open(kf, 'r') as f:
            all_keywords.update(set(f.read().split(',')))

    persona_kyewords = random.choices(list(all_keywords), k=5)
    persona_kyewords = ','.join(persona_kyewords)
    cmd = f'docker run --rm -v {str(keyword_dir_path)}:/keywords -e MODE=prod -e ELASTICSEARCH_HOST={ELASTICSEARCH_HOST} -e ELASTICSEARCH_PORT={ELASTICSEARCH_PORT} {image_name} python3 -u /youtube-crawler/src/main.py {name} {persona_kyewords}'
    subprocess.Popen(cmd.split())


while True:
    running_containers = get_running_containers(image_name)
    running_count = len(running_containers)

    if running_count < desired_count:
        for _ in range(desired_count - running_count):
            start_container(image_name)
            print(f"새 컨테이너를 시작합니다. 현재 실행 중인 컨테이너 수: {running_count + 1}")
            time.sleep(1)  # 컨테이너가 시작되는 동안 대기

    time.sleep(5)  # 5초 간격으로 상태를 확인