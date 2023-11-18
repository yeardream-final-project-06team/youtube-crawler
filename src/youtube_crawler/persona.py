from random import choice, random
from time import sleep

from msgspec import msgpack
from selenium.webdriver import Firefox, Chrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

from youtube_crawler.models import VideoSimple, VideoDetail
from youtube_crawler.collector import Collector
from youtube_crawler.logger import logger, call_logger


class Persona:
    def __init__(
        self,
        name: str,
        keywords: list[str],
        browser: Firefox | Chrome,
        watch_count=10,
        speed=1,
    ):
        self.name = name
        self.keywords = keywords
        self.watch_count = watch_count
        self.speed = speed
        self.browser = browser
        self.browser.set_window_size(1920, 3000)
        self.collector = Collector(self.browser)

        self.last_video = None
        self.related = True
        self.video_list = []
        self.next_urls = []

        self.browser.get("https://www.youtube.com/?gl=KR")

    @call_logger
    def run(self) -> None:
        # 시작 대기 시간
        sleep(random() * 10 / self.speed)

        # 한국어 영상 수집을 위해 한국어 키워드 입력
        self.move_to_search()

        # 영상 10개 볼때까지 반복
        while self.watch_count:
            # 영상 고르는 시간
            sleep(random() * 10 / self.speed)

            # 영상 시청
            self.watch_video()
            self.watch_count -= 1

            # 다음 영상
            next_action, self.related = choice(
                [
                    (self.move_to_search, True),
                    (self.move_to_main, False),
                    (self.move_to_channel, True),
                    (self.watch_next_video, True),
                    (self.watch_recommendation, True),
                ]
            )
            next_action()

    def move_to_search(self) -> None:
        keyword = choice(self.keywords)
        link = f"https://www.youtube.com/results?search_query={keyword}"
        self.browser.get(link)

        # 영상이 로드될때까지 대기
        self.wait_loading()

        # 검색 화면에서 데이터 수집
        self.video_list = self.collector.collect_list_search()
        self.next_urls = [video.url for video in self.video_list]

        # 수집된 데이터 전송
        # TODO

    def move_to_main(self) -> None:
        self.browser.get("https://www.youtube.com/?gl=KR")

        # 영상이 로드될때까지 대기
        self.wait_loading()

        # 메인 화면에서 데이터 수집
        self.video_list = self.collector.collect_list_main()
        self.next_urls = [video.url for video in self.video_list]

        # 수집된 데이터 전송
        # TODO

    def move_to_channel(self) -> None:
        self.browser.get(self.last_video.channel)

        # 영상이 로드될때까지 대기
        self.wait_loading()

        # 채널 화면에서 데이터 수집
        self.video_list = self.collector.collect_list_channel()
        self.next_urls = [video.url for video in self.video_list]

        # 수집된 데이터 전송
        # TODO

    def watch_next_video(self):
        self.next_urls = [self.last_video.next_video_url]

    def watch_recommendation(self) -> None:
        self.next_urls = [video.url for video in self.video_list]

    def watch_video(self):
        self.browser.get(choice(self.next_urls))

        # 추천 영상이 로드될때까지 대기
        self.wait_loading()

        # 광고 영상 존재시 광고 수집
        # TODO

        # 데이터 수집
        self.last_video, self.video_list = self.collector.collect_player_page()

        # 수집된 데이터 전송
        # TODO

        # 영상시청
        play_time = self.cvt_play_time(self.last_video.play_time)
        watching_time = (1 + random() * 9) * 60
        watching_time *= 2 if self.related else 0.8
        watching_time = min(watching_time, play_time) + 30
        sleep(watching_time / self.speed)

    def wait_loading(self, num_components=20, seconds=30) -> None:
        y = 0
        while not (
            WebDriverWait(self.browser, seconds).until(
                EC.presence_of_all_elements_located((By.ID, "time-status"))
            )
        )[:num_components][-1].text:
            if y < 2000:
                y += 500
            self.browser.execute_script(f"window.scrollTo(0,{y})")
            sleep(1)

    @staticmethod
    def cvt_play_time(play_time: str) -> int:
        if play_time == "live":
            return int(random() * 10 * 60)
        _play_time = play_time.split(":")
        match len(_play_time):
            case 1:
                seconds = int(_play_time[0])
            case 2:
                seconds = int(_play_time[0]) * 60 + int(_play_time[1])
            case 3:
                seconds = (
                    int(_play_time[0]) * 3600
                    + int(_play_time[1]) * 60
                    + int(_play_time[2])
                )
            case _:
                logger.warn(f"{play_time} not matched")
                return 0
        return seconds
