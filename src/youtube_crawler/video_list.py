from dataclasses import dataclass
from datetime import date, time
from enum import Enum, auto
from typing import Optional

from msgspec import Struct
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException



class PAGE(Enum):
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
    id:str
    title:str
    author:str
    url:str
    play_time:time
    view_count:int


class VideoList(Struct):
    page:PAGE

    # def collect(self):

    #     match self.page:
    #         case PAGE.MAIN:


@dataclass
class Collector:
    browser:Firefox

    def collect_list_main(self, debug=False):
        self.browser.get('https://www.youtube.com/')
        WebDriverWait(self.browser, 60).until(EC.presence_of_all_elements_located((By.ID, 'time-status')))
        WebDriverWait(self.browser, 60).until(EC.presence_of_all_elements_located((By.ID, 'text')))

        if debug:
            self.browser.save_screenshot('screenshot_main.png')

        contents = self.browser.find_element(By.ID, 'contents')
        rows = contents.find_elements(By.TAG_NAME, 'ytd-rich-grid-row')

        data = []
        i = 0
        for r in rows:
            videos = r.find_elements(By.TAG_NAME, 'ytd-rich-grid-media')
            for v in videos:
                video_title_link = v.find_element(By.ID, 'video-title-link')

                aria = video_title_link.get_attribute('aria-label')
                title = video_title_link.get_attribute('title')
                url = video_title_link.get_attribute('href')
                author = v.find_element(By.ID, 'avatar-link').get_attribute('title')
                try:
                    play_time = v.find_element(By.ID, 'time-status').text
                except NoSuchElementException as e:
                    if v.find_element(By.CSS_SELECTOR, '#meta > ytd-badge-supported-renderer.video-badge.style-scope.ytd-rich-grid-media > div > p').text == '실시간':
                        play_time = 'live'
                    else:
                        raise e

                view_count = self.get_view_count(aria, title, author)
                id = self.get_video_id(url)
                data.append(VideoSimple(id, title, author, url, play_time,view_count))

                i += 1
                if i==20:
                    break
            if i==20:
                break
        
        return data
                

    def collect_list_search(self, keyword:str, debug=False):
        self.browser.get(f'https://www.youtube.com/results?search_query={keyword}')

        if debug:
            self.browser.save_screenshot('screenshot_search_0.png')

        self.browser.execute_script('window.scrollTo(0,2000)')

        if debug:
            self.browser.save_screenshot('screenshot_search_1.png')

        WebDriverWait(self.browser, 60).until(EC.presence_of_all_elements_located((By.ID, 'time-status')))
        WebDriverWait(self.browser, 60).until(EC.presence_of_all_elements_located((By.ID, 'text')))

        if debug:
            self.browser.save_screenshot('screenshot_search_2.png')

        contents = self.browser.find_element(By.ID, 'contents')
        sections = contents.find_elements(By.TAG_NAME, 'ytd-item-section-renderer')

        data = []
        i = 0
        for s in sections:
            for v in s.find_elements(By.TAG_NAME, 'ytd-video-renderer'):
                video_title = v.find_element(By.ID, 'video-title')

                aria = video_title.get_attribute('aria-label')
                title = video_title.get_attribute('title')
                url = video_title.get_attribute('href')
                author = v.find_element(By.ID, 'channel-info').find_element(By.ID, 'channel-name').find_element(By.CSS_SELECTOR, '#text > a').get_attribute('textContent')
                try:
                    play_time = v.find_element(By.ID, 'time-status').text
                except NoSuchElementException as e:
                    if (text:=v.find_element(By.CSS_SELECTOR, '#badges > div.badge.badge-style-type-live-now-alternate.style-scope.ytd-badge-supported-renderer.style-scope.ytd-badge-supported-renderer > p').text) == '실시간':
                        play_time = 'live'
                    else:
                        print(text)
                        raise e

                view_count = self.get_view_count(aria, title, author)
                id = self.get_video_id(url)
                data.append(VideoSimple(id, title, author, url, play_time,view_count))

                i += 1
                if i==20:
                    break
            if i==20:
                break
        
        return data
                

    def get_view_count(self, aria:str, title:str, author:str):
        prefix = f'{title} 게시자: {author} 조회수 '

        view_count = aria.removeprefix(prefix)
        view_count_end = view_count.find('회')
        view_count = int(view_count[:view_count_end].replace(',',''))

        return view_count
    

    def get_video_id(self, url:str):
        try:
            return url.split('?')[1].split('&')[0].split('=')[1]
        except IndexError as e:
            print(url)
            raise e


