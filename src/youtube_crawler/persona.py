from .collector import Collector
from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from msgspec import Struct
from random import choice, random
from time import sleep



class Persona(Struct):
    name:str
    keywords:list[str]
    recent_action:str

    def __post_init__(self):
        profile = FirefoxProfile()
        profile.set_preference('permissions.default.image', 2)
        profile.set_preference('intl.accept_languages', 'ko-kr,en-us,en')

        self.options = FirefoxOptions()
        self.options.add_argument('--headless')
        self.options._profile = profile

        self.browser = Firefox(options=self.options)
        self.browser.set_window_size(1920,3000)
        self.collector = Collector(self.browser)


    def move_to_main(self):
        self.browser.get('https://www.youtube.com/')
        while not (main:=WebDriverWait(self.browser, 60).until(EC.presence_of_all_elements_located((By.ID, 'time-status'))))[:60][-1].text:
            pass
        
        self.video_list = self.collector.collect_list_main()
        self.recent_action = 'move_to_main'

        self.watch_video()

    
    def move_to_search(self):
        keyword = choice(self.keywords)
        self.browser.get(f'https://www.youtube.com/results?search_query={keyword}')

        y = 0
        while not (main:=WebDriverWait(self.browser, 60).until(EC.presence_of_all_elements_located((By.ID, 'time-status'))))[:60][-1].text:
            if y<5000:
                y += 500
            self.browser.execute_script(f'window.scrollTo(0,{y})')
            pass

        self.video_list = self.collector.collect_list_search()
        self.recent_action = 'move_to_search'
    
        self.watch_video()


    def move_to_back(self):
        self.browser.back()
        match self.recent_action:
            case 'move_to_main':
                self.move_to_main()
            case 'move_to_search':
                self.move_to_search()
            case 'watch_video':
                self.watch_video()
    

    def watch_next_video(self):
        self.browser.get(self.video.next_video_url)

        y = 0
        while not (main:=WebDriverWait(self.browser, 60).until(EC.presence_of_all_elements_located((By.ID, 'time-status'))))[:20][-1].text \
            or len(main)<20:
            if y<2000:
                y += 500
            self.browser.execute_script(f'window.scrollTo(0,{y})')
            pass

        self.video, self.video_list = self.collector.collect_player_page()
        self.recent_action = 'watch_video'

        play_time = self.cvt_play_time(self.video.play_time)
        watching_time = max(random() * 10 *60, 60)
        watching_time = min(watching_time, play_time) + 30
        sleep(watching_time)

        next_action = choice([self.move_to_back, self.watch_video, self.watch_next_video, self.move_to_search, self.move_to_main])
        next_action()


    def watch_video(self):
        video = choice(self.video_list)
        self.browser.get(video.url)

        y = 0
        while not (main:=WebDriverWait(self.browser, 60).until(EC.presence_of_all_elements_located((By.ID, 'time-status'))))[:20][-1].text \
            or len(main)<20:
            if y<2000:
                y += 500
            self.browser.execute_script(f'window.scrollTo(0,{y})')
            pass

        self.video, self.video_list = self.collector.collect_player_page()
        self.recent_action = 'watch_video'

        play_time = self.cvt_play_time(self.video.play_time)
        watching_time = max(random() * 10 *60, 60)
        watching_time = min(watching_time, play_time) + 30
        sleep(watching_time)

        next_action = choice([self.move_to_back, self.watch_video, self.watch_next_video, self.move_to_search, self.move_to_main])
        next_action()


    @staticmethod
    def cvt_play_time(play_time:str) -> int:
        play_time = play_time.split(':')
        match len(play_time):
            case 1:
                play_time = int(play_time[0])
            case 2:
                play_time = int(play_time[0]) * 60 + int(play_time[1])
            case 3:
                play_time = int(play_time[0]) * 3600 + int(play_time[1]) * 60 + int(play_time[2])
        
        return play_time