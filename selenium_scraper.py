from selenium.webdriver import Chrome
import urllib
import os


class SeleniumScraper:

    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = None

        self.urls = ["http://www.izmostock.com/car-stock-photos-by-brand"]
        self.car_brands = ["Volvo", "BMW", "Audi", "Renault"]

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
                    if brand.text in self.car_brands:
                        url_to_brand = brand_caption.find_element_by_xpath(".//a").get_attribute('href')
                        print(f"Brand urls: {url_to_brand}")
                        self.driver.get(url_to_brand)


if __name__ == '__main__':
    SeleniumScraper("/home/alp/Desktop/chromedriver").scrape()