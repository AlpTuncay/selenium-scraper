import shutil
import os
import json

from google_images_download import google_images_download

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s -> %(message)s", datefmt="%H:%M:%S")


class ScrapeGoogleImages:

    def __init__(self, config_file, destination, external_drive=None):
        self.config_file = config_file
        self.destination = destination
        self.arguments = {
            'output_directory': self.destination,
            'extract_metadata': False,
            'thumbnail': False,
            'no_download': False,
            'limit': 150,
            'chromedriver': "/home/alp/Desktop/chromedriver"
        }

        self.external_drive = external_drive

        self.downloader = google_images_download.googleimagesdownload()

    def __call__(self, *args, **kwargs):
        # Check config file and destination path
        if not os.path.exists(self.destination):
            logging.info(f"Provided destination path {self.destination} does not exist. Creating now.")
            os.mkdir(self.destination)

        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Provided config file {self.config_file} does not exist")

        config = json.load(open(self.config_file, "r"))

        for cfg in config:
            try:
                for model in cfg["models"]:
                    img_path = os.path.join(cfg["brand"], model)
                    self.arguments["image_directory"] = img_path

                    for keyword in cfg["keywords"]:
                        query_term = f"{cfg['brand']} {model} {keyword}"
                        self.arguments["keywords"] = query_term
                        paths = self.downloader.download(self.arguments)
                        logging.info(f"Path: {paths}")
                        if self.external_drive:
                            for keys, vals in paths.items():
                                for val in vals:
                                    rel_path = os.path.relpath(val, "/home/alp/PycharmProjects/web-image-scraper")
                                    external_full_path = os.path.join(self.external_drive, os.path.dirname(rel_path))
                                    if not os.path.exists(external_full_path):
                                        os.makedirs(external_full_path)
                                    try:
                                        shutil.copy(val, external_full_path)
                                        os.remove(val)
                                    except Exception as e:
                                        logging.error(f"Error occurred while copying to external drive. Full exception:\n{e}")
                                        raise e
            except KeyError as ke:
                logging.error(f"Provided key does not exist. Full exception:\n{ke}")

        # if self.external_drive:
        #     try:
        #         shutil.copytree(self.destination, self.external_drive)
        #         os.remove(self.destination)
        #     except Exception as e:
        #         logging.error(f"Error occurred while copying to external drive. Full exception:\n{e}")
        #         raise e


if __name__ == '__main__':
    google_images_scraper = ScrapeGoogleImages("scraper.json", "car_dataset", external_drive="/media/alp/Yeni Birim/data")
    google_images_scraper()

