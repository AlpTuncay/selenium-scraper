from selenium.webdriver import Chrome
import urllib
import os


class SeleniumScraper:

    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = None

        self.urls = ["http://www.izmostock.com/car-stock-photos-by-brand", "https://www.sahibinden.com/kategori/otomobil"]
        # self.car_brands = ["Volvo", "BMW", "Audi", "Renault"]
        self.models = {"Audi": ["A1", "A3 Hatchback", "Q7", "A4 Sedan"], "Volvo": ["V40", "XC60", "S40"], "BMW": ["116", "320"]}

    def init_driver(self):
        if not os.path.exists(self.driver_path):
            raise FileNotFoundError(f"Provided driver path {self.driver_path} does not exist.")

        self.driver = Chrome(self.driver_path)

    def scrape(self):
        self.init_driver()

        for url in self.urls:
            self.driver.get(url)
            root = self.driver.find_elements_by_xpath("//div[@id='by_brand']")
            # print(root)
            for brand_caption in root:
                for brand in brand_caption.find_elements_by_xpath(".//span[@id='by_brand_caption']"):
                    brand_text_value = brand.text
                    if brand_text_value in self.models:
                        print(brand_text_value)
                        url_to_brand = brand_caption.find_element_by_xpath(".//a").get_attribute('href')
                        print(f"Brand urls: {url_to_brand}")
                        self.driver.get(url_to_brand)
                        model_info_list = self.driver.find_elements_by_xpath("//td[@class='slide']//img")
                        for model_info in model_info_list:
                            if self.check_brand_and_model(brand_text_value, model_info.get_attribute("title").split()):
                                # url_to_model_images = self.driver.find_elements_by_xpath()
                               self.driver.get()

    def check_brand_and_model(self, brand, model_info_from_page):
        bool_list = []
        length = None
        for model in self.models[brand]:
            model = model.split()
            for word in model:
                if word in model_info_from_page:
                    bool_list.append(True)
                    length = len(model)

        return len(bool_list) == length


if __name__ == '__main__':
    SeleniumScraper("/home/alp/Desktop/chromedriver").scrape()