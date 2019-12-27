from selenium.webdriver import Chrome
import urllib
import os


class SeleniumScraper:

    def __init__(self, driver_path, download_path):
        self.driver_path = driver_path
        self.driver = None
        self.download_path = download_path

        self.url = "http://www.izmostock.com/car-stock-photos-by-brand"
        # self.car_brands = ["Volvo", "BMW", "Audi", "Renault"]
        self.models = {"Audi": ["A1", "A3", "Q7", "A4"], "Volvo": ["V40", "XC60", "S40"], "BMW": ["116", "320"]}

    def init_driver(self):
        if not os.path.exists(self.driver_path):
            raise FileNotFoundError(f"Provided driver path {self.driver_path} does not exist.")

        self.driver = Chrome(self.driver_path)

    def scrape(self):
        self.init_driver()

        self.driver.get(self.url)
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
                    model_info_list = self.driver.find_elements_by_xpath("//td[@valign='top']/a")
                    for model_info in model_info_list:
                        check = self.check_brand_and_model(brand_text_value, model_info.text)
                        if check[0]:
                            model = check[1]
                            print(model_info.get_attribute("title"))
                            self.driver.get(model_info.get_attribute("href"))
                            hrefs_to_images = self.driver.find_elements_by_xpath("//td[@class='slide']/a")
                            for href in hrefs_to_images:
                                url_to_image = href.get_attribute('href')
                                self.driver.get(url_to_image)
                                image_src = self.driver.find_element_by_xpath("//div[@class='imageWidget']//img").get_attribute("src")
                                download_path = os.path.join(self.download_path, str.lower(brand_text_value), str.lower(model))
                                # urllib.urlretrieve(image_src, "")
                                print(image_src)
                                print(download_path)

    def check_brand_and_model(self, brand, model_info_from_page):
        bool_list = []
        length = None
        for model in self.models[brand]:
            if model in model_info_from_page:
                return True, model
            else:
                return False, model


if __name__ == '__main__':
    SeleniumScraper("/home/alp/Desktop/chromedriver", download_path="/media/alp/Yeni Birim/data/car_dataset").scrape()