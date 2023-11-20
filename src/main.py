import os
import sys

from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile, Chrome

from youtube_crawler.persona import Persona

mode = os.getenv("MODE", "dev")

if __name__ == "__main__":
    if mode == "prod":
        profile = FirefoxProfile()
        profile.set_preference("permissions.default.image", 2)
        profile.set_preference("intl.accept_languages", "ko-kr,en-us,en")

        options = FirefoxOptions()
        options.add_argument("--headless")
        options._profile = profile

        browser = Firefox(options=options)
    else:
        service = Service(executable_path="./chromedriver")
        browser = Chrome(service=service)

    name = sys.argv[1]
    keywords = sys.argv[2].split()
    persona = Persona(
        name,
        keywords,
        browser,
    )
    persona.run()
