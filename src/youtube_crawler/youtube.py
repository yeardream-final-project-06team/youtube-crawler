from dataclasses import dataclass
from selenium import webdriver

@dataclass
class Youtube:
    webdriver:webdriver.Firefox

    def search(self, keyword:str) -> :

    
    