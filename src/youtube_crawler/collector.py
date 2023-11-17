from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from msgspec import Struct
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from .logger import logger


class VideoDetail(Struct):
    title: str
    author: str
    view_count: int
    url: str
    like: int
    desc: str
    tags: list[str]
    upload_date: datetime
    play_time: str
    category: str
    id: str
    next_video_url: str


class VideoSimple(Struct):
    id: str
    title: str
    author: str
    url: str
    play_time: Optional[str]
    view_count: int


class Collector:
    def __init__(self, browser: Firefox) -> None:
        self.browser = browser

    def collect_list_main(self) -> list[VideoSimple]:
        contents = self.browser.find_element(By.ID, "contents")
        rows = contents.find_elements(By.TAG_NAME, "ytd-rich-grid-row")

        data = []
        for r in rows:
            videos = r.find_elements(By.TAG_NAME, "ytd-rich-grid-media")
            for v in videos:
                video_simple = self.get_video_simple(v, "main")
                if video_simple:
                    data.append(video_simple)
                if len(data) == 20:
                    return data
        return data

    def collect_list_search(self) -> list[VideoSimple]:
        contents = self.browser.find_element(By.ID, "contents")
        sections = contents.find_elements(By.TAG_NAME, "ytd-item-section-renderer")

        data = []
        for s in sections:
            for v in s.find_elements(By.TAG_NAME, "ytd-video-renderer"):
                video_simple = self.get_video_simple(v, "search")
                if video_simple:
                    data.append(video_simple)
                if len(data) == 20:
                    return data
        return data

    def collect_list_player(self) -> list[VideoSimple]:
        contents = self.browser.find_element(By.ID, "related").find_element(
            By.ID, "items"
        )
        videos = contents.find_elements(By.TAG_NAME, "ytd-compact-video-renderer")

        data = []
        for v in videos:
            video_simple = self.get_video_simple(v, "player")
            if video_simple:
                data.append(video_simple)
            if len(data) == 20:
                return data
        return data

    def collect_player_page(self) -> tuple[VideoDetail, list[VideoSimple]]:
        list_data = self.collect_list_player()
        video_data = self.collect_video_detail()

        return video_data, list_data

    def collect_video_detail(self) -> Optional[VideoDetail]:
        # TODO content 로딩까지 기다리기
        content = self.browser.find_element(By.ID, "watch7-content")
        if not content:
            return None

        url = content.find_element(
            By.CSS_SELECTOR, "#watch7-content > link:nth-child(1)"
        ).get_attribute("href")

        title = content.find_element(
            By.CSS_SELECTOR, "#watch7-content > meta:nth-child(2)"
        ).get_attribute("content")

        video_id = content.find_element(
            By.CSS_SELECTOR, "#watch7-content > meta:nth-child(5)"
        ).get_attribute("content")

        author = content.find_element(
            By.CSS_SELECTOR, "#watch7-content > span:nth-child(7) > link:nth-child(2)"
        ).get_attribute("content")

        view_count = int(
            content.find_element(
                By.CSS_SELECTOR, "#watch7-content > meta:nth-child(17)"
            ).get_attribute("content")
        )

        upload_date = datetime.fromisoformat(
            content.find_element(
                By.CSS_SELECTOR, "#watch7-content > meta:nth-child(19)"
            ).get_attribute("content")
        )

        category = content.find_element(
            By.CSS_SELECTOR, "#watch7-content > meta:nth-child(20)"
        ).get_attribute("content")

        self.browser.execute_script("window.scrollTo(0,0)")
        # self.browser.save_screenshot("screenshot_description.png")
        description = self.browser.find_element(By.ID, "description-inner")
        description.click()
        description = description.find_element(
            By.CSS_SELECTOR,
            "#description-inline-expander > yt-attributed-string",
        ).text

        selector = "#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-left-controls > div.ytp-time-display.notranslate > span:nth-child(2) > span.ytp-time-duration"
        play_time = self.get_play_time(self.browser, selector)

        like = self.browser.find_element(
            By.CSS_SELECTOR,
            "#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button",
        ).get_attribute("aria-label")
        like = self.get_like_count(like)

        tags = self.browser.find_elements(By.CSS_SELECTOR, "#info > a")
        tags = [t.text for t in tags]

        next_video_url = self.browser.find_element(
            By.CSS_SELECTOR,
            "#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-left-controls > a.ytp-next-button.ytp-button",
        ).get_attribute("href")

        return VideoDetail(
            title,
            author,
            view_count,
            url,
            like,
            description,
            tags,
            upload_date,
            play_time,
            category,
            video_id,
            next_video_url,
        )

    def get_video_simple(self, v, screen):
        url = ""
        if screen == "main":
            elem = v.find_element(By.ID, "video-title-link")

            url = elem.get_attribute("href")

            author = v.find_element(By.ID, "avatar-link").get_attribute("title")

            selector = "#meta > ytd-badge-supported-renderer.video-badge.style-scope.ytd-rich-grid-media > div > p"
            play_time = self.get_play_time(v, selector)

        elif screen == "search":
            elem = v.find_element(By.ID, "video-title")

            url = elem.get_attribute("href")

            author = (
                v.find_element(By.ID, "channel-info")
                .find_element(By.ID, "channel-name")
                .find_element(By.CSS_SELECTOR, "#text > a")
                .get_attribute("textContent")
            )

            selector = "#badges > div.badge.badge-style-type-live-now-alternate.style-scope.ytd-badge-supported-renderer.style-scope.ytd-badge-supported-renderer > p"
            play_time = self.get_play_time(v, selector)

        elif screen == "player":
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

            selector = "#dismissible > div > div.metadata.style-scope.ytd-compact-video-renderer > a > div > ytd-badge-supported-renderer > div > p"
            play_time = self.get_play_time(v, selector)

        else:
            return None

        # shorts는 수집제외
        if str(urlparse(url).path).startswith("/shorts"):
            return None

        aria = elem.get_attribute("aria-label")
        title = elem.get_attribute("title")
        view_count = self.get_view_count(aria, title, author)
        id = str(urlparse(url).query)[2:]
        return VideoSimple(id, title, author, url, play_time, view_count)

    def get_video_detail(self):
        pass

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

    def get_play_time(self, v, selector):
        try:
            play_time = v.find_element(By.ID, "time-status").text
        except NoSuchElementException as e:
            try:
                if (
                    text := v.find_element(
                        By.CSS_SELECTOR,
                        selector,
                    ).text
                ) == "실시간":
                    play_time = "live"
                else:
                    logger.fatal("play_time", text)
                    logger.fatal(e)
                    exit()
            except NoSuchElementException as e:
                logger.fatal("element not found")
                logger.fatal(e)
                exit()
        return play_time
