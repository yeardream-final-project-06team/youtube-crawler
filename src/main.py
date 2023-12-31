import os
import random
import subprocess

import requests
from selenium.webdriver import Chrome, Firefox, FirefoxOptions, FirefoxProfile
from selenium.webdriver.chrome.service import Service

from youtube_crawler.persona import Persona

MODE = os.getenv("MODE", "dev")
TOR = bool(os.getenv("TOR", ""))
KEYWORD_SERVER = os.getenv("KEYWORD_SERVER")

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/120.0 Mobile/15E148 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/120.0 Mobile/15E148 Safari/605.1.15",
    "Mozilla/5.0 (Android 14; Mobile; rv:109.0) Gecko/120.0 Firefox/120.0",
]
user_agent = random.choice(user_agents)

if __name__ == "__main__":
    if MODE == "prod":
        profile = FirefoxProfile()
        profile.set_preference("permissions.default.image", 2)
        profile.set_preference("intl.accept_languages", "ko-kr,en-us,en")
        if TOR:
            subprocess.check_output(["service", "tor", "start"])
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.socks", "127.0.0.1")
            profile.set_preference("network.proxy.socks_port", 9050)
        profile.set_preference("general.useragent.override", user_agent)

        options = FirefoxOptions()
        options.add_argument("--headless")
        options._profile = profile

        browser = Firefox(options=options)
        browser.set_window_size(1920, 3000)
        browser.install_addon("/youtube-crawler/h264ify-1.1.0.xpi")
    else:
        service = Service(executable_path="./chromedriver")
        browser = Chrome(service=service)
    persona = requests.get(f"http://{KEYWORD_SERVER}/persona/random").json()
    name, keywords = persona["name"], persona["keywords"]
    persona = Persona(name, keywords.split(","), browser)
    persona.run()
