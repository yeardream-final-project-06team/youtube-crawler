from datetime import datetime
from enum import Enum
from time import sleep
from random import random
import unicodedata
import subprocess

from selenium.webdriver import Firefox, Chrome
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from youtube_crawler.models import VideoSimple, VideoDetail, VideoAd
from youtube_crawler.logger import logger, check_parsing_error
from youtube_crawler.utils import get_video_path, get_video_id


class Screen(Enum):
    MAIN = 1
    SEARCH = 2
    PLAYER = 3
    CHANNEL = 4


class Collector:
    def __init__(self, browser: Firefox | Chrome, nums_per_page=20) -> None:
        self.browser = browser
        self.nums_per_page = nums_per_page
        self.container_id = subprocess.run(
            ["hostname"], capture_output=True, text=True
        ).stdout.strip()

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
                if len(data) == self.nums_per_page:
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
                if len(data) == self.nums_per_page:
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
            if len(data) == self.nums_per_page:
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
                if len(data) == self.nums_per_page:
                    return data
        return data

    @check_parsing_error
    def get_video_detail(self, video: VideoSimple) -> VideoDetail:
        id = video.id
        title = video.title
        author = video.author
        url = video.url
        play_time = video.play_time
        view_count = video.view_count

        self.browser.execute_script("window.scrollTo(0,0)")

        description = self.browser.find_element(By.ID, "description-inner")
        description.click()
        description = description.find_element(
            By.CSS_SELECTOR,
            "#description-inline-expander > yt-attributed-string",
        ).text

        like = self.browser.find_element(
            By.CSS_SELECTOR,
            "#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button",
        ).get_attribute("aria-label")

        tags = self.browser.find_elements(By.CSS_SELECTOR, "#info > a")
        tags = [t.text for t in tags]

        content = self.browser.find_element(By.ID, "watch7-content")
        channel = content.find_element(
            By.CSS_SELECTOR,
            "#watch7-content > span:nth-child(7) > link:nth-child(1)",
        ).get_attribute("href")

        upload_date = content.find_element(
            By.CSS_SELECTOR,
            "#watch7-content > meta:nth-child(19)",
        ).get_attribute("content")

        category = content.find_element(
            By.CSS_SELECTOR,
            "#watch7-content > meta:nth-child(20)",
        ).get_attribute("content")

        next_video_url = self.browser.find_element(
            By.CSS_SELECTOR,
            "#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-left-controls > a.ytp-next-button.ytp-button",
        ).get_attribute("href")

        self.browser.execute_script("window.scrollTo(0,0)")

        detail = VideoDetail(
            id,
            title,
            author,
            url,
            play_time,
            view_count,
            description,
            channel,
            self.get_like_count(like) if like else 0,
            tags,
            datetime.fromisoformat(upload_date) if upload_date else None,
            category,
            next_video_url,
            self.container_id,
        )
        return detail

    @check_parsing_error
    def get_video_simple(
        self,
        v: WebElement,
        screen: Screen,
    ) -> VideoSimple | bool | None:
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
                "#dismissible > div > div.metadata.style-scope.ytd-compact-video-renderer > a > div > ytd-badge-supported-renderer > div > p",
            )

        elif screen == Screen.CHANNEL:
            elem = v.find_element(By.ID, "video-title")

            url = elem.get_attribute("href")

            author = None

            play_time = self.get_play_time(
                v,
                "#badges > div.badge.badge-style-type-live-now-alternate.style-scope.ytd-badge-supported-renderer.style-scope.ytd-badge-supported-renderer > p",
            )

        else:
            return None

        if not play_time:
            return None
        # shorts는 수집제외
        if url and get_video_path(url).startswith("/shorts"):
            return None

        aria = elem.get_attribute("aria-label")
        title = elem.get_attribute("title")

        if not author and aria:
            words = aria.removeprefix(f"{title} 게시자:").split()
            while words and words.pop() != "조회수":
                continue
            author = " ".join(words)

        view_count = self.get_view_count(aria, title, author)
        id = get_video_id(url)
        simple = VideoSimple(
            id,
            title,
            author,
            url,
            play_time,
            view_count,
            self.container_id,
        )
        return simple

    def collect_ad(self):
        try:
            headline = self.browser.find_element(
                By.CLASS_NAME,
                "ytp-flyout-cta-headline",
            ).text

            description = self.browser.find_element(
                By.CLASS_NAME,
                "ytp-flyout-cta-description",
            ).text

            icon = self.browser.find_element(
                By.CLASS_NAME,
                "ytp-flyout-cta-icon",
            ).get_attribute("src")

            preview = self.browser.find_element(
                By.CLASS_NAME,
                "ytp-ad-preview-container",
            ).text

            # skip 가능
            if preview.isnumeric():
                skip = WebDriverWait(self.browser, 10).until(
                    EC.element_to_be_clickable(
                        (By.CLASS_NAME, "ytp-ad-skip-button-modern")
                    )
                )
                sleep(random() * 2)
                skip.click()
            else:
                WebDriverWait(self.browser, 60).until(
                    EC.invisibility_of_element_located(
                        (By.CLASS_NAME, "ytp-ad-preview-container")
                    )
                )
            return VideoAd(
                headline,
                description,
                icon,
                self.container_id,
            )
        except NoSuchElementException:
            return None

    def get_view_count(self, aria: str, title: str, author: str) -> int:
        prefix = f"{title} 게시자: {author} 조회수 "
        prefix = unicodedata.normalize("NFC", prefix)
        aria = unicodedata.normalize("NFC", aria)

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
        v: WebElement,
        selector: str,
    ) -> str:
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
                    logger.fatal(f"play_time: {text}")
                    raise e
            except NoSuchElementException as e:
                raise e
        return play_time
