from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from urllib.request import urlretrieve
from urllib.parse import urlparse
import os
import re
import time
import sys

'''
Scraper that uses Selenium to scrape specifically sahibinden.com for stock car photos.
'''


class SeleniumScraper:

    def __init__(self, driver_path, download_path):
        self.driver_path = driver_path
        self.driver = None
        self.download_path = download_path

        self.urls = ["https://www.sahibinden.com/category/en/cars", "https://www.sahibinden.com/category/en/off-road-suv-pickup-trucks"]
        self.models = {"Audi": ["A3", "Q7", "A4"],
                       "Volvo": ["XC60", "XC90"],
                       "BMW": ["3 series"],
                       "Volkswagen": ["Golf", "Polo", "Passat"]}
        # self.models = {
        #     "Volvo": ["XC60", "XC90"],
        #     "BMW": {"1 Serisi": ["118"],
        #             "3 Serisi": ["320", "330"]}
        # }

        # self.models = {
        #     "BMW": {"3 Serisi": ["330"]}
        # }
        self.total_downloads = {}
        for label in self.models:
            self.total_downloads[label] = {}
            for item in self.models[label]:
                self.total_downloads[label][item] = 0

        self.download_limit = 50

    def init_driver(self):
        if not os.path.exists(self.driver_path):
            raise FileNotFoundError(f"Provided driver path {self.driver_path} does not exist.")

        self.driver = Chrome(self.driver_path)

    def scrape(self):
        self.init_driver()

        for url in self.urls:
            self.driver.get(url)
            time.sleep(2)
            car_make_list = self.driver.find_elements_by_xpath("//div[contains(@data-value, 'Cars')]//ul[@class='categoryList jspScrollable']//li/a")
            if not car_make_list:
                car_make_list = self.driver.find_elements_by_xpath("//div[contains(@data-value, 'Off-Road, SUV & Pickup Trucks')]//ul[@class='categoryList jspScrollable']//li/a")

            brand_text_links = {}
            for web_element in car_make_list:
                model = web_element.get_attribute("title")
                if model in self.models:
                    brand_text_links[model] = web_element.get_attribute("href")

            for brand, link in brand_text_links.items():
                # if brand in self.models:
                self.driver.get(link)
                model_list = self.driver.find_elements_by_xpath("//div[@id='searchCategoryContainer']/div/div/ul/li/a")
                links_to_models = [model.get_attribute("href") for model in model_list]
                model_infos = [model.get_attribute("title") for model in model_list]
                for link_to_model, model_info in zip(links_to_models, model_infos):
                    check = self.check_brand_and_model(brand, model_info)
                    if check[0]:
                        model = check[1]
                        while self.total_downloads[brand][model] < self.download_limit:
                            self.driver.get(link_to_model)
                            nav_buttons = self.driver.find_elements_by_xpath("//ul[@class='pageNaviButtons']/li/following-sibling::li[2]/a")
                            pages = [nav_button.get_attribute("href") for nav_button in nav_buttons]
                            for page in pages:
                                self.driver.get(page)
                                links_to_ads = self.driver.find_elements_by_xpath("//*[@id='searchResultsTable']/tbody/tr/td[1]/a")
                                links = [link.get_attribute("href") for link in links_to_ads]
                                for addr in links:
                                    self.driver.get(addr)
                                    images_list = self.driver.find_elements_by_xpath("//div[@class='classifiedDetailMainPhoto']/label[contains(@id, 'label_images')]/img")
                                    images_links = [image_link.get_attribute("data-src") for image_link in images_list]
                                    for src in images_links:
                                        label = f"{str.lower(brand)} {str.lower(model)}"
                                        download_path = os.path.join(self.download_path, label)
                                        if not os.path.exists(download_path):
                                            os.makedirs(download_path)
                                        parsed_url = urlparse(src).path
                                        filename = os.path.basename(parsed_url)
                                        download_path = f"{download_path}/{filename}"
                                        if os.path.exists(download_path):
                                            print(f"Exists: {download_path}")
                                        try:
                                            urlretrieve(src, download_path)
                                            self.total_downloads[brand][model] += 1
                                            print(self.total_downloads)
                                        except:
                                            continue
                                    if self.total_downloads[brand][model] >= self.download_limit:
                                        break
                                if self.total_downloads[brand][model] >= self.download_limit:
                                    break
                            if self.total_downloads[brand][model] >= self.download_limit:
                                break
                        # if self.total_downloads[brand][model] >= self.download_limit:
                        #     pass


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
    SeleniumScraper("/home/alp/Desktop/chromedriver", download_path="/media/alp/Yeni Birim/data/car_dataset_new").scrape()
    # SeleniumScraper("/home/alp/Desktop/chromedriver", download_path="./car_dataset").scrape()
