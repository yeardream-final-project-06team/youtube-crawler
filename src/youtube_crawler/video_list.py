from dataclasses import dataclass
from datetime import date, time, datetime
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
    PLAYER = auto()


class VideoDetail(Struct):
    title:str
    author:str
    view_count:int
    url:str
    like:int
    desc:str
    tags:list[str]
    upload_date:datetime
    play_time:str
    category:str
    id:str


class VideoSimple(Struct):
    id:str
    title:str
    author:str
    url:str
    play_time:Optional[str]
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
        while not (main:=WebDriverWait(self.browser, 60).until(EC.presence_of_all_elements_located((By.ID, 'time-status'))))[:60][-1].text:
            pass

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
                    try:
                        if (text:=v.find_element(By.CSS_SELECTOR, '#meta > ytd-badge-supported-renderer.video-badge.style-scope.ytd-rich-grid-media > div > p').text) == '실시간':
                            play_time = 'live'
                        else:
                            print('play_time', text)
                            raise e
                    except NoSuchElementException:
                        play_time = None

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

        y = 0
        while not (main:=WebDriverWait(self.browser, 60).until(EC.presence_of_all_elements_located((By.ID, 'time-status'))))[:60][-1].text:
            if y<5000:
                y += 500
            self.browser.execute_script(f'window.scrollTo(0,{y})')
            pass

        if debug:
            self.browser.save_screenshot('screenshot_search_1.png')

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
                    try:
                        if (text:=v.find_element(By.CSS_SELECTOR, '#badges > div.badge.badge-style-type-live-now-alternate.style-scope.ytd-badge-supported-renderer.style-scope.ytd-badge-supported-renderer > p').text) == '실시간':
                            play_time = 'live'
                        else:
                            print('play_time', text)
                            raise e
                    except NoSuchElementException:
                        play_time = None

                view_count = self.get_view_count(aria, title, author)
                id = self.get_video_id(url)
                data.append(VideoSimple(id, title, author, url, play_time,view_count))

                i += 1
                if i==20:
                    break
            if i==20:
                break
        
        return data
                
    
    def collect_player_page(self, url:str, debug=False):
        self.browser.get(url)

        if debug:
            self.browser.save_screenshot('screenshot_player_0.png')

        y = 0
        while not (main:=WebDriverWait(self.browser, 60).until(EC.presence_of_all_elements_located((By.ID, 'time-status'))))[:20][-1].text \
            or len(main)<20:
            if y<2000:
                y += 500
            self.browser.execute_script(f'window.scrollTo(0,{y})')
            pass

        if debug:
            self.browser.save_screenshot('screenshot_player_1.png')

        # list_data = self.collect_list_player()
        list_data = []
        video_data = self.collect_video_detail()

        return video_data, list_data


    def collect_list_player(self):

        contents = self.browser.find_element(By.ID, 'related').find_element(By.ID, 'items')
        videos = contents.find_elements(By.TAG_NAME, 'ytd-compact-video-renderer')

        data = []
        i = 0
        for v in videos:
            video_title = v.find_element(By.ID, 'video-title')

            aria = video_title.get_attribute('aria-label')
            title = video_title.get_attribute('title')
            url = v.find_element(By.CSS_SELECTOR, '#dismissible > div > div.metadata.style-scope.ytd-compact-video-renderer > a').get_attribute('href')
            author = v.find_element(By.ID, 'channel-name').find_element(By.CSS_SELECTOR, '#text').get_attribute('textContent')
            try:
                play_time = v.find_element(By.ID, 'time-status').text
            except NoSuchElementException as e:
                try:
                    if (text:=v.find_element(By.CSS_SELECTOR, '#dismissible > div > div.metadata.style-scope.ytd-compact-video-renderer > a > div > ytd-badge-supported-renderer > div > p').text) == '실시간':
                        play_time = 'live'
                    else:
                        print('play_time', text)
                        raise e
                except NoSuchElementException:
                    play_time = None

            view_count = self.get_view_count(aria, title, author)
            id = self.get_video_id(url)
            data.append(VideoSimple(id, title, author, url, play_time,view_count))

            i += 1
            if i==20:
                break
        
        return data


    def collect_video_detail(self):
        content = self.browser.find_element(By.ID, 'watch7-content')
        url = content.find_element(By.CSS_SELECTOR, '#watch7-content > link:nth-child(1)').get_attribute('href')
        title = content.find_element(By.CSS_SELECTOR, '#watch7-content > meta:nth-child(2)').get_attribute('content')
        video_id = content.find_element(By.CSS_SELECTOR, '#watch7-content > meta:nth-child(5)').get_attribute('content')
        author = content.find_element(By.CSS_SELECTOR, '#watch7-content > span:nth-child(7) > link:nth-child(2)').get_attribute('content')
        view_count = int(content.find_element(By.CSS_SELECTOR, '#watch7-content > meta:nth-child(17)').get_attribute('content'))
        upload_date = datetime.fromisoformat(content.find_element(By.CSS_SELECTOR, '#watch7-content > meta:nth-child(19)').get_attribute('content'))
        category = content.find_element(By.CSS_SELECTOR, '#watch7-content > meta:nth-child(20)').get_attribute('content')

        self.browser.execute_script(f'window.scrollTo(0,0)')
        self.browser.save_screenshot('screenshot_description.png')
        description = self.browser.find_element(By.ID, 'description-inner')
        description.click()
        description = description.find_element(By.CSS_SELECTOR, '#description-inline-expander > yt-attributed-string > span').text

        try:
            play_time = self.browser.find_element(By.CSS_SELECTOR, '#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-left-controls > div.ytp-time-display.notranslate > span:nth-child(2) > span.ytp-time-duration').text
        except NoSuchElementException as e:
            if self.browser.find_element(By.CSS_SELECTOR, '#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-left-controls > div.ytp-time-display.notranslate.ytp-live > button').text == '실시간':
                play_time = 'live'
        
        like = self.browser.find_element(By.CSS_SELECTOR, '#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button').get_attribute('aria-label')
        like = self.get_like_count(like)

        tags = self.browser.find_elements(By.CSS_SELECTOR, '#info > a')
        tags = [t.text for t in tags]
        
        return VideoDetail(title, author, view_count, url, like, description, tags, upload_date, play_time, category, video_id)

    def get_view_count(self, aria:str, title:str, author:str):
        prefix = f'{title} 게시자: {author} 조회수 '

        view_count = aria.removeprefix(prefix)
        view_count_end = view_count.find('회')
        if '없음' in view_count:
            view_count = 0
        else:
            view_count = int(view_count[:view_count_end].replace(',',''))

        return view_count
    

    def get_video_id(self, url:str):
        try:
            return url.split('?')[1].split('&')[0].split('=')[1]
        except IndexError as e:
            print(url)
            raise e

    
    def get_like_count(self, like:str):
        return int(like.removeprefix('나 외에 사용자 ').removesuffix('명이 이 동영상을 좋아함').replace(',',''))
