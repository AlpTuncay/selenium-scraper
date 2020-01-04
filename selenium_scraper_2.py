from selenium.webdriver import Chrome

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
        self.models = {"Audi": ["A1", "A3", "Q7", "A4"],
                       "Volvo": ["V40", "XC60", "XC90"],
                       "BMW": {"1 serisi": ["118"],
                               "3 serisi": ["320", "330"]},
                       "Volkswagen": ["Golf", "Polo", "Passat"],
                       "Renault": ["Megane", "Kadjar", "Captur", "Clio"]}

        self.download_limit = 50

    def init_driver(self):
        if not os.path.exists(self.driver_path):
            raise FileNotFoundError(f"Provided driver path {self.driver_path} does not exist.")

        self.driver = Chrome(self.driver_path)

    def scrape(self):
        self.init_driver()

        for url in self.urls:
            self.driver.get(url)

            try:
                car_make_list = self.driver.find_elements_by_xpath("//div[@data-value='Otomobil']//ul[@class='categoryList jspScrollable']//li/a")
            except:
                car_make_list = self.driver.find_elements_by_xpath("//div[@data-value='Arazi, SUV & Pickup']//ul[@class='categoryList jspScrollable']//li/a")

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
                    # if isinstance(self.models[brand], dict):
                    #     pass
                    # else:
                    check = self.check_brand_and_model(brand, model_info)

                    if check[0]:
                        model = check[1]
                        self.driver.get(link_to_model)



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