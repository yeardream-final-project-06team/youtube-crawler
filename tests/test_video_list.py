from unittest import TestCase
from youtube_crawler.video_list import Collector
from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile


class TestCollector(TestCase):
    def setUp(self) -> None:
        profile = FirefoxProfile()
        profile.set_preference('network.proxy.type',1)
        profile.set_preference('network.proxy.socks','127.0.0.1')
        profile.set_preference('network.proxy.socks_port',9050)

        options = FirefoxOptions()
        options.add_argument('--headless')
        options._profile = profile

        self.browser = Firefox(options=options)

    def test_collect_main(self):

        collector = Collector(self.browser)
        collections = collector.collect_main()
