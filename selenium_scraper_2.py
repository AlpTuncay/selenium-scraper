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

'''
Scraper that uses Selenium to scrape specifically sahibinden.com for stock car photos.
'''
class SeleniumScraper:

    def __init__(self, driver_path, download_path):
        self.driver_path = driver_path
        self.driver = None
        self.download_path = download_path

        self.urls = ["https://www.sahibinden.com/kategori/otomobil", "https://www.sahibinden.com/kategori/arazi-suv-pickup"]
        # self.models = {"Audi": ["A1", "A3", "Q7", "A4"],
        #                "Volvo": ["V40", "XC60", "XC90"],
        #                "BMW": {"1 serisi": ["118"],
        #                        "3 serisi": ["320", "330"]},
        #                "Volkswagen": ["Golf", "Polo", "Passat"],
        #                "Renault": ["Megane", "Kadjar", "Captur", "Clio"]}
        self.models = {
            "Volvo": ["XC60", "XC90"],
            "BMW": {"1 Serisi": ["118"],
                    "3 Serisi": ["320", "330"]}
        }

        self.download_limit = 50

    def init_driver(self):
        if not os.path.exists(self.driver_path):
            raise FileNotFoundError(f"Provided driver path {self.driver_path} does not exist.")

        self.driver = Chrome(self.driver_path)

    def scrape(self):
        self.init_driver()

        for url in self.urls:
            self.driver.get(url)

            car_make_list = self.driver.find_elements_by_xpath("//div[contains(@data-value, 'Otomobil')]//ul[@class='categoryList jspScrollable']//li/a")
            if not car_make_list:
                car_make_list = self.driver.find_elements_by_xpath("//div[contains(@data-value, 'Arazi, SUV & Pickup')]//ul[@class='categoryList jspScrollable']//li/a")

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
                    if isinstance(self.models[brand], dict):
                        for key, value in self.models[brand].items():
                            if key == model_info:
                                self.driver.get(link_to_model)
                                models = self.driver.find_elements_by_xpath("//div[@id='searchCategoryContainer']//ul/li/a")
                                model_hrefs = [anchor_elem.get_attribute("href") for anchor_elem in models]
                                model_categories = [anchor_elem.text for anchor_elem in models]
                                for model_category in value:
                                    expr = re.compile(rf"{model_category}[a-zA-Z0-9]?")
                                    for category, model_href in zip(model_categories, model_hrefs):
                                        if expr.search(category):
                                            self.driver.get(model_href)
                                            links_to_ads = self.driver.find_elements_by_xpath("//*[@id='searchResultsTable']/tbody/tr/td[1]/a")
                                            links = [link.get_attribute("href") for link in links_to_ads]
                                            for addr in links:
                                                self.driver.get(addr)
                                                images_list = self.driver.find_elements_by_xpath("//div[@class='classifiedDetailMainPhoto']/label[contains(@id, 'label_images')]/img")
                                                images_links = [image_link.get_attribute("data-src") for image_link in images_list]
                                                for src in images_links:
                                                    label = f"{str.lower(brand)} {str.lower(model_category)}"
                                                    download_path = os.path.join(self.download_path, label)
                                                    if not os.path.exists(download_path):
                                                        os.makedirs(download_path)
                                                    parsed_url = urlparse(src).path
                                                    filename = os.path.basename(parsed_url)
                                                    download_path = f"{download_path}/{filename}"
                                                    try:
                                                        urlretrieve(src, download_path)
                                                    except:
                                                        continue
                    else:
                        check = self.check_brand_and_model(brand, model_info)
                        if check[0]:
                            model = check[1]
                            self.driver.get(link_to_model)
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
                                    try:
                                        urlretrieve(src, download_path)
                                    except:
                                        continue

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
    # SeleniumScraper("/home/alp/Desktop/chromedriver", download_path="./car_dataset").scrape()