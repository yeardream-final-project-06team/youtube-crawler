from datetime import datetime
from urllib.parse import urlparse
from enum import Enum

import msgspec
from selenium.webdriver import Firefox, Chrome
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver

from youtube_crawler.models import VideoSimple, VideoDetail
from youtube_crawler.logger import logger


class Screen(Enum):
    MAIN = 1
    SEARCH = 2
    PLAYER = 3
    CHANNEL = 4


class Collector:
    def __init__(self, browser: Firefox | Chrome) -> None:
        self.browser = browser

    def collect_list_main(self) -> list[VideoSimple]:
        contents = self.browser.find_element(By.ID, "contents")
        rows = contents.find_elements(By.TAG_NAME, "ytd-rich-grid-row")

        data = []
        for r in rows:
            videos = r.find_elements(By.TAG_NAME, "ytd-rich-grid-media")
            for v in videos:
                video_simple = self.get_video_simple(v, Screen.MAIN)
                if video_simple:
                    data.append(video_simple)
                if len(data) == 20:
                    return data
        return data

    def collect_list_search(self) -> list[VideoSimple]:
        contents = self.browser.find_element(By.ID, "contents")
        sections = contents.find_elements(
            By.TAG_NAME,
            "ytd-item-section-renderer",
        )

        data = []
        for s in sections:
            for v in s.find_elements(By.TAG_NAME, "ytd-video-renderer"):
                video_simple = self.get_video_simple(v, Screen.SEARCH)
                if video_simple:
                    data.append(video_simple)
                if len(data) == 20:
                    return data
        return data

    def collect_list_player(self) -> list[VideoSimple]:
        contents = self.browser.find_element(By.ID, "related").find_element(
            By.ID, "items"
        )
        videos = contents.find_elements(
            By.TAG_NAME,
            "ytd-compact-video-renderer",
        )

        data = []
        for v in videos:
            video_simple = self.get_video_simple(v, Screen.PLAYER)
            if video_simple:
                data.append(video_simple)
            if len(data) == 20:
                return data
        return data

    def collect_list_channel(self) -> list[VideoSimple]:
        contents = self.browser.find_element(By.ID, "contents")
        sections = contents.find_elements(
            By.TAG_NAME,
            "ytd-item-section-renderer",
        )

        data = []
        for s in sections:
            for v in s.find_elements(By.TAG_NAME, "ytd-grid-video-renderer"):
                video_simple = self.get_video_simple(v, Screen.CHANNEL)
                if video_simple:
                    data.append(video_simple)
                if len(data) == 20:
                    return data
        return data

    def collect_player_page(self) -> tuple[VideoDetail, list[VideoSimple]]:
        list_data = self.collect_list_player()
        video_data = self.get_video_detail()

        return video_data, list_data

    def get_video_detail(self) -> VideoDetail:
        content = self.browser.find_element(By.ID, "watch7-content")

        url = content.find_element(
            By.CSS_SELECTOR,
            "#watch7-content > link:nth-child(1)",
        ).get_attribute("href")

        title = content.find_element(
            By.CSS_SELECTOR,
            "#watch7-content > meta:nth-child(2)",
        ).get_attribute("content")

        video_id = content.find_element(
            By.CSS_SELECTOR,
            "#watch7-content > meta:nth-child(5)",
        ).get_attribute("content")

        author = content.find_element(
            By.CSS_SELECTOR,
            "#watch7-content > span:nth-child(7) > link:nth-child(2)",
        ).get_attribute("content")

        channel = content.find_element(
            By.CSS_SELECTOR,
            "#watch7-content > span:nth-child(7) > link:nth-child(1)",
        ).get_attribute("href")

        view_count = content.find_element(
            By.CSS_SELECTOR,
            "#watch7-content > meta:nth-child(17)",
        ).get_attribute("content")

        upload_date = content.find_element(
            By.CSS_SELECTOR,
            "#watch7-content > meta:nth-child(19)",
        ).get_attribute("content")

        category = content.find_element(
            By.CSS_SELECTOR,
            "#watch7-content > meta:nth-child(20)",
        ).get_attribute("content")

        self.browser.execute_script("window.scrollTo(0,0)")
        # self.browser.save_screenshot("screenshot_description.png")
        description = self.browser.find_element(By.ID, "description-inner")
        description.click()
        description = description.find_element(
            By.CSS_SELECTOR,
            "#description-inline-expander > yt-attributed-string",
        ).text

        play_time = self.get_play_time(
            self.browser,
            By.CSS_SELECTOR,
            "#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-left-controls > div.ytp-time-display.notranslate > span:nth-child(2) > span.ytp-time-duration",
            By.CSS_SELECTOR,
            "#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-left-controls > div.ytp-time-display.notranslate.ytp-live > button",
        )

        like = self.browser.find_element(
            By.CSS_SELECTOR,
            "#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button",
        ).get_attribute("aria-label")

        tags = self.browser.find_elements(By.CSS_SELECTOR, "#info > a")
        tags = [t.text for t in tags]

        next_video_url = self.browser.find_element(
            By.CSS_SELECTOR,
            "#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-left-controls > a.ytp-next-button.ytp-button",
        ).get_attribute("href")

        detail = VideoDetail(
            title,
            author,
            channel,
            int(view_count) if view_count else 0,
            url,
            self.get_like_count(like) if like else 0,
            description,
            tags,
            datetime.fromisoformat(upload_date) if upload_date else None,
            play_time,
            category,
            video_id,
            next_video_url,
        )
        for attr in detail.__struct_fields__:
            if not getattr(detail, attr):
                logger.warn("attribution not found")
                logger.warn(msgspec.json.encode(detail))
                break
        return detail

    def get_video_simple(
        self,
        v: WebElement,
        screen: Screen,
    ) -> VideoSimple | None:
        url = ""
        if screen == Screen.MAIN:
            elem = v.find_element(By.ID, "video-title-link")

            url = elem.get_attribute("href")

            author = v.find_element(
                By.ID,
                "avatar-link",
            ).get_attribute("title")

            play_time = self.get_play_time(
                v,
                By.ID,
                "time-status",
                By.CSS_SELECTOR,
                "#meta > ytd-badge-supported-renderer.video-badge.style-scope.ytd-rich-grid-media > div > p",
            )

        elif screen == Screen.SEARCH:
            elem = v.find_element(By.ID, "video-title")

            url = elem.get_attribute("href")

            author = (
                v.find_element(By.ID, "channel-info")
                .find_element(By.ID, "channel-name")
                .find_element(By.CSS_SELECTOR, "#text > a")
                .get_attribute("textContent")
            )

            play_time = self.get_play_time(
                v,
                By.ID,
                "time-status",
                By.CSS_SELECTOR,
                "#badges > div.badge.badge-style-type-live-now-alternate.style-scope.ytd-badge-supported-renderer.style-scope.ytd-badge-supported-renderer > p",
            )

        elif screen == Screen.PLAYER:
            elem = v.find_element(By.ID, "video-title")

            url = v.find_element(
                By.CSS_SELECTOR,
                "#dismissible > div > div.metadata.style-scope.ytd-compact-video-renderer > a",
            ).get_attribute("href")

            author = (
                v.find_element(By.ID, "channel-name")
                .find_element(By.CSS_SELECTOR, "#text")
                .get_attribute("textContent")
            )

            play_time = self.get_play_time(
                v,
                By.ID,
                "time-status",
                By.CSS_SELECTOR,
                "#dismissible > div > div.metadata.style-scope.ytd-compact-video-renderer > a > div > ytd-badge-supported-renderer > div > p",
            )

        elif screen == Screen.CHANNEL:
            elem = v.find_element(By.ID, "video-title")

            url = elem.get_attribute("href")

            author = None

            play_time = self.get_play_time(
                v,
                By.ID,
                "time-status",
                By.CSS_SELECTOR,
                "#badges > div.badge.badge-style-type-live-now-alternate.style-scope.ytd-badge-supported-renderer.style-scope.ytd-badge-supported-renderer > p",
            )

        else:
            return None

        # shorts는 수집제외
        if str(urlparse(url).path).startswith("/shorts"):
            return None

        aria = elem.get_attribute("aria-label")
        title = elem.get_attribute("title")

        if not author:
            words = aria.removeprefix(f"{title} 게시자:").split()
            while words.pop() != "조회수":
                continue
            author = " ".join(words)

        view_count = self.get_view_count(aria, title, author)
        id = str(urlparse(url).query)[2:]

        simple = VideoSimple(id, title, author, url, play_time, view_count)
        for attr in simple.__struct_fields__:
            if not getattr(simple, attr):
                logger.warn("attribution not found")
                logger.warn(msgspec.json.encode(simple))
                break
        return simple

    def get_view_count(self, aria: str, title: str, author: str) -> int:
        prefix = f"{title} 게시자: {author} 조회수 "

        view_count = aria.removeprefix(prefix)
        view_count_end = view_count.find("회")
        if "없음" in view_count:
            view_count = 0
        else:
            view_count = int(view_count[:view_count_end].replace(",", ""))

        return view_count

    def get_like_count(self, like: str) -> int:
        return int(
            like.removeprefix("나 외에 사용자 ")
            .removesuffix("명이 이 동영상을 좋아함")
            .replace(",", "")
        )

    def get_play_time(
        self,
        v: WebElement | WebDriver,
        time_by: str,
        time_selector: str,
        live_by: str,
        live_selector: str,
    ) -> str:
        try:
            play_time = v.find_element(time_by, time_selector).text
        except NoSuchElementException as e:
            try:
                if (
                    text := v.find_element(
                        live_by,
                        live_selector,
                    ).text
                ) == "실시간":
                    play_time = "live"
                else:
                    logger.fatal(f"play_time: {text}")
                    raise e
            except NoSuchElementException as e:
                raise e
        return play_time
