from selenium.webdriver import Chrome

from urllib.request import urlretrieve
from urllib.parse import urlparse
import os
import re

'''
Scraper that uses Selenium to scrape specifically izmostock for stock car photos.
'''
class SeleniumScraper:

    def __init__(self, driver_path, download_path):
        self.driver_path = driver_path
        self.driver = None
        self.download_path = download_path

        self.url = "http://www.izmostock.com/car-stock-photos-by-brand"
        self.models = {"Audi": ["A1", "A3", "Q7", "A4"],
                       "Volvo": ["V40", "XC60", "S40"],
                       "BMW": ["118", "320", "520"],
                       "Volkswagen": ["Golf", "Polo", "Passat"],
                       "Renault": ["Megane", "Kadjar", "Captur", "Clio"]}

    def init_driver(self):
        if not os.path.exists(self.driver_path):
            raise FileNotFoundError(f"Provided driver path {self.driver_path} does not exist.")

        self.driver = Chrome(self.driver_path)

    def scrape(self):
        self.init_driver()

        self.driver.get(self.url)
        root = self.driver.find_elements_by_xpath("//div[@id='by_brand']")
        brand_texts_links = {}
        for r in root:
            brand_texts_links[r.find_element_by_xpath(".//span[@id='by_brand_caption']").text] = r.find_element_by_xpath(".//a").get_attribute("href")

        for brand, link in brand_texts_links.items():
            if brand in self.models:
                self.driver.get(link)
                model_info_list = self.driver.find_elements_by_xpath("//td[@valign='top']/a")
                links_to_models = [model_info.get_attribute("href") for model_info in model_info_list]
                model_infos = [model_info.text for model_info in model_info_list]
                for link_to_model, model_info in zip(links_to_models, model_infos):
                    check = self.check_brand_and_model(brand, model_info)
                    if check[0]:
                        model = check[1]
                        self.driver.get(link_to_model)
                        hrefs_to_images = self.driver.find_elements_by_xpath("//td[@class='slide']/a")
                        hrefs = [href.get_attribute("href") for href in hrefs_to_images]
                        for href in hrefs:
                            self.driver.get(href)
                            image_src = self.driver.find_element_by_xpath("//div[@class='imageWidget']//img").get_attribute("src")
                            download_path = os.path.join(self.download_path, str.lower(brand), str.lower(model))
                            if not os.path.exists(download_path):
                                os.makedirs(download_path)
                            parsed_url = urlparse(image_src).path
                            filename = os.path.basename(parsed_url)
                            download_path = f"{download_path}/{filename}"
                            urlretrieve(image_src, download_path)

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