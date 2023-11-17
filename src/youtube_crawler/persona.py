from .collector import Collector
from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from msgspec import msgpack
from random import choice, random
from time import sleep


class Persona:
    def __init__(self, name: str, keywords: list[str], recent_action: str):
        self.name = name
        self.keywords = keywords
        self.recent_action = recent_action

        self.watch_count = 0

        profile = FirefoxProfile()
        profile.set_preference("permissions.default.image", 2)
        profile.set_preference("intl.accept_languages", "ko-kr,en-us,en")

        self.options = FirefoxOptions()
        self.options.add_argument("--headless")
        self.options._profile = profile

        self.browser = Firefox(options=self.options)
        self.browser.set_window_size(1920, 3000)
        self.collector = Collector(self.browser)

    def move_to_main(self):
        self.browser.get("https://www.youtube.com/")

        # 영상이 로드될때까지 대기
        self.wait_loading()

        # 영상 고르는 흉내
        sleep(random() * 10)

        # main 화면에서의 영상들 데이터 수집
        self.video_list = self.collector.collect_list_main()
        self.recent_action = "move_to_main"

        # 수집된 데이터 전송
        # TODO

        self.watch_video()

    def move_to_search(self):
        keyword = choice(self.keywords)
        link = f"https://www.youtube.com/results?search_query={keyword}"
        self.browser.get(link)

        # 영상이 로드될때까지 대기
        self.wait_loading()

        self.video_list = self.collector.collect_list_search()
        self.recent_action = "move_to_search"

        # 수집된 데이터 전송
        # TODO

        self.watch_video()

    def move_to_back(self):
        self.browser.back()
        match self.recent_action:
            case "move_to_main":
                self.move_to_main()
            case "move_to_search":
                self.move_to_search()
            case "watch_video":
                self.watch_video()

    def watch_next_video(self):
        self.browser.get(self.video.next_video_url)

        y = 0
        while (
            not (
                main := WebDriverWait(self.browser, 60).until(
                    EC.presence_of_all_elements_located((By.ID, "time-status"))
                )
            )[:20][-1].text
            or len(main) < 20
        ):
            if y < 2000:
                y += 500
            self.browser.execute_script(f"window.scrollTo(0,{y})")
            pass

        self.video, self.video_list = self.collector.collect_player_page()
        self.recent_action = "watch_video"

        play_time = self.cvt_play_time(self.video.play_time)
        watching_time = max(random() * 10 * 60, 60)
        watching_time = min(watching_time, play_time) + 30
        sleep(watching_time)

        next_action = choice(
            [
                self.move_to_back,
                self.watch_video,
                self.watch_next_video,
                self.move_to_search,
                self.move_to_main,
            ]
        )
        next_action()

    def watch_video(self):
        self.watch_count += 1
        if self.watch_count > 10:
            exit()

        video = choice(self.video_list)
        self.browser.get(video.url)

        # TODO
        # 광고 영상 존재시 광고 수집

        # 영상이 로드될때까지 대기
        self.wait_loading()

        self.video, self.video_list = self.collector.collect_player_page()
        self.recent_action = "watch_video"

        play_time = self.cvt_play_time(self.video.play_time)
        watching_time = max(random() * 10 * 60, 60)
        watching_time = min(watching_time, play_time) + 30
        sleep(watching_time)

        next_action = choice(
            [
                self.move_to_back,
                self.watch_video,
                self.watch_next_video,
                self.move_to_search,
                self.move_to_main,
            ]
        )
        next_action()

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
        play_time = play_time.split(":")
        match len(play_time):
            case 1:
                play_time = int(play_time[0])
            case 2:
                play_time = int(play_time[0]) * 60 + int(play_time[1])
            case 3:
                play_time = (
                    int(play_time[0]) * 3600
                    + int(play_time[1]) * 60
                    + int(play_time[2])
                )

        return play_time
