from random import choice, random
from time import sleep
from datetime import datetime

from selenium.webdriver import Firefox, Chrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

from youtube_crawler.collector import Collector
from youtube_crawler.logger import logger, call_logger
from youtube_crawler.sender import Sender
from youtube_crawler.utils import cvt_play_time

# from youtube_crawler.sender import Sender


class Persona:
    def __init__(
        self,
        name: str,
        keywords: list[str],
        browser: Firefox | Chrome,
        watch_count=10,
        nums_per_page=20,
        debug=False,
    ):
        self.name = name
        self.keywords = keywords
        self.watch_count = watch_count
        self.nums_per_page = nums_per_page
        self.browser = browser
        self.browser.set_window_size(1920, 3000)
        self.collector = Collector(self.browser, nums_per_page)
        self.sender = Sender()
        self.debug = debug

        self.last_video = None
        self.related = True
        self.video_list = []

        self.browser.get("https://www.youtube.com/?gl=KR")

    @call_logger
    def run(self) -> None:
        logger.info('Crawling Start')
        # 시작 대기 시간
        sleep(random() * 10)

        # 한국어 영상 수집을 위해 한국어 키워드 입력
        self.move_to_search()

        # 영상 10개 볼때까지 반복
        while self.watch_count:
            logger.info(f"video #{11 - self.watch_count}")
            # 영상 고르는 시간
            sleep(random() * 10)

            # 영상 시청
            self.watch_video()
            self.watch_count -= 1

            # 다음 영상
            next_action, self.related = choice(
                [
                    (self.move_to_search, True),
                    (self.move_to_main, False),
                    (self.move_to_channel, True),
                    (self.watch_recommendation, True),
                ]
            )
            next_action()

    def move_to_search(self) -> None:
        keyword = choice(self.keywords)
        link = f"https://www.youtube.com/results?search_query={keyword}"
        self.browser.get(link)

        logger.info(f"moved to search, Selected Keyword: {keyword}")

        # 영상이 로드될때까지 대기
        self.wait_loading()

        # 검색 화면에서 데이터 수집
        self.video_list = self.collector.collect_list_search()

        # 수집된 데이터 전송
        # TODO
        index = 'video_simple'
        self.sender.send_many(index, self.video_list)

    def move_to_main(self) -> None:
        self.browser.get("https://www.youtube.com/?gl=KR")

        # 영상이 로드될때까지 대기
        self.wait_loading()

        # 메인 화면에서 데이터 수집
        self.video_list = self.collector.collect_list_main()

        logger.info(f"moved to main, collected {len(self.video_list)}")
        # 수집된 데이터 전송
        # TODO
        index = 'video_simple'
        self.sender.send_many(index, self.video_list)

    def move_to_channel(self) -> None:
        self.browser.get(self.last_video.channel)

        # 영상이 로드될때까지 대기
        self.wait_loading()

        # 채널 화면에서 데이터 수집
        self.video_list = self.collector.collect_list_channel()

        logger.info(f"moved to channel, collected {len(self.video_list)}")

        # 수집된 데이터 전송
        # TODO
        index = 'video_simple'
        self.sender.send_many(index, self.video_list)

    def watch_recommendation(self) -> None:
        logger.info("watch watch_recommendation")

    def watch_video(self) -> None:
        video = choice(self.video_list)
        self.browser.get(video.url)

        # 추천 영상이 로드될때까지 대기
        self.wait_loading()
        self.browser.execute_script("window.scrollTo(0, 0)")

        # 영상 시청 화면에서 데이터 수집
        self.video_list = self.collector.collect_list_player()
        self.last_video = self.collector.get_video_detail(video)

        # 영상시청
        if self.debug:
            watching_time = 60
        else:
            play_time = cvt_play_time(self.last_video.play_time)
            watching_time = (1 + random() * 9) * 60
            watching_time *= 2 if self.related else 0.8
            watching_time = min(watching_time, play_time) + 10

        logger.info(f"watch a video for {watching_time} seconds")

        start = datetime.now()
        while (datetime.now() - start).total_seconds() < watching_time:
            # 광고 영상 존재시 광고 수집
            ad = self.collector.collect_ad()
            # TODO
            if ad:
                self.last_video.ads.append(ad)
                pass
            sleep(30)

        # 수집된 데이터 전송
        # TODO
        index = 'video_detail'
        self.sender.send_many(index, self.video_list)


    def wait_loading(self, seconds=10) -> None:
        y = 0
        now = datetime.now()
        while True:
            if (datetime.now() - now).seconds > seconds:
                break
            elements = WebDriverWait(self.browser, seconds).until(
                EC.presence_of_all_elements_located((By.ID, "time-status"))
            )
            loaded = len([elem for elem in elements if elem.text])
            if self.nums_per_page < loaded:
                break
            y += 500
            self.browser.execute_script(f"window.scrollTo(0,{y})")
            sleep(random())