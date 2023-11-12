from enum import StrEnum, auto
from msgspec import Struct
from dataclasses import dataclass
from datetime import date, time

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

class PAGE(StrEnum):
    MAIN = auto()
    SEARCH = auto()
    CHANNEL = auto()
    PLAYER = auto()


class VideoDetail(Struct):
    title:str
    author:str
    view_count:int
    url:str
    like:int
    desc:str
    tag:list[str]
    create_at:date
    play_time:time


class VideoSimple(Struct):
    title:str
    author:str
    view_count:int
    url:str
    play_time:time


class VideoList(Struct):
    page:PAGE

    # def collect(self):

    #     match self.page:
    #         case PAGE.MAIN:


@dataclass
class Collector:
    browser:Firefox

    def collect_main(self):
        self.browser.get('https://www.youtube.com/')
        contents = \
            self.browser\
            .find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer/div[6]")\
            .find_elements(By.CSS_SELECTOR, '#contents > ytd-rich-grid-row')

        for c in contents:
            print(c.find_element(By.ID, 'text').text)


    def process_aria(self, aria:str):
        author_start = aria.find('게시자')
        view_count_start = aria.find('조회수')
        play_time_start = aria.find('전', view_count_start)
