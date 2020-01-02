from selenium.webdriver import Chrome

from urllib.request import urlretrieve
from urllib.parse import urlparse
import os
import re
import time

'''
Scraper that uses Selenium to scrape specifically for stock car photos.
'''
class SeleniumScraper:

    def __init__(self, driver_path, download_path):
        self.driver_path = driver_path
        self.driver = None
        self.download_path = download_path

        self.url = "http://www.google.com/imghp"
        self.models = {"Audi": ["A1", "A3", "Q7", "A4"],
                       "Volvo": ["V40", "XC60", "S40"],
                       "BMW": ["118", "320", "520"],
                       "Volkswagen": ["Golf", "Polo", "Passat"],
                       "Renault": ["Megane", "Kadjar", "Captur", "Clio"]}
        self.keywords = ["front", "back", "side"]
        self.download_limit = 50

    def init_driver(self):
        if not os.path.exists(self.driver_path):
            raise FileNotFoundError(f"Provided driver path {self.driver_path} does not exist.")

        self.driver = Chrome(self.driver_path)

    def scrape(self):
        self.init_driver()

        self.driver.get(self.url)

        for brand in self.models:
            for model in self.models[brand]:
                for keyword in self.keywords:
                    search_box = self.driver.find_element_by_name("q")
                    search_term = f"{brand} {model} {keyword}"
                    search_box.send_keys(search_term)
                    search_box.submit()
                    downloaded = 0
                    image_boxes = self.driver.find_elements_by_xpath("//a[@class='rg_l'][ @jsname='hSRGPd']")
                    time.sleep(10)
                    while downloaded < self.download_limit:
                        for image_box in image_boxes:
                            image_box.click()
                    self.driver.back()

    def check_brand_and_model(self, brand, model_info_from_page):
        print(f"Brand: {brand},\tModel: {self.models[brand]},\tInfo from page: {model_info_from_page}")
        for model in self.models[brand]:
            print(f"Checking for model: {model}")
            expr_to_match = re.compile(rf"{model}[a-zA-Z0-9]?")
            if expr_to_match.search(model_info_from_page):
                print(f"Values returned: {True} and {model}")
                return True, model
        print(f"Values returned: {False}")
        return False, None


if __name__ == '__main__':
    SeleniumScraper("/home/alp/Desktop/chromedriver", download_path="/media/alp/Yeni Birim/data/car_dataset").scrape()