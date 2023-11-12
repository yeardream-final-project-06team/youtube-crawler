from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image


profile = webdriver.FirefoxProfile()
profile.set_preference('network.proxy.type',1)
profile.set_preference('network.proxy.socks','127.0.0.1')
profile.set_preference('network.proxy.socks_port',9050)

options = webdriver.FirefoxOptions()
options.add_argument('--headless')
options._profile = profile

browser = webdriver.Firefox(options=options)

browser.set_window_size(1920,2500)
browser.get("https://www.youtube.com/")
browser.save_screenshot('/crawler/screenshot.png')

# browser.get("https://www.youtube.com/results?search_query=메모법")

# titles = browser.find_elements(By.CSS_SELECTOR, "#text")

titles = browser.find_element(By.ID, "contents")
titles = titles.find_elements(By.ID, 'time-status')
for t in titles:
    print(t.find_element(By.ID, 'text').text)
    # label = t.get_attribute('aria-label')
    # title = t.get_attribute('title')
    # link = t.get_attribute('href')
    # print(label)
    # print(title)
    # print(link)

browser.close()