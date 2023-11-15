from unittest import TestCase
from youtube_crawler.video_list import Collector
from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile


class TestCollector(TestCase):
    def setUp(self) -> None:
        profile = FirefoxProfile()
        profile.set_preference('permissions.default.image', 2)
        profile.set_preference('intl.accept_languages', 'ko-kr,en-us,en')

        self.options = FirefoxOptions()
        self.options.add_argument('--headless')
        self.options._profile = profile

    def test_collect_main(self):
        browser = Firefox(options=self.options)
        browser.set_window_size(1920,3000)
        collector = Collector(browser)
        data = collector.collect_list_main(debug=True)
        for d in data:
            print(d)


    def test_collect_search(self):
        browser = Firefox(options=self.options)
        browser.set_window_size(1920,3000)
        collector = Collector(browser)
        data = collector.collect_list_search('뉴스', debug=True)
        for d in data:
            print(d)