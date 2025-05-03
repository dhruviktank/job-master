from abc import ABC, abstractmethod
from app.models.request.scraper import Scrape
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class Scraper(ABC):
    def __init__(self, req: Scrape):
        self.request = req

    def execute(self):
        logging.info('started executing scrapping job')
        data = {}
        html = False
        # file_name = f"page_source_{self.__class__.__name__.lower()}.txt"
        # if(Path(file_name).exists()):
        #     logger.info(f"Reading from {file_name}")
        #     with open(file_name, 'r') as file:
        #         html = file.read()
        if (html == False):
            logger.info("fetching page source from url")
            html = self.get_page_source()
            # if (html != False):
                # with open(file_name, 'w') as file:
                #     logger.info(f"Saving page source to {file_name}")
                #     file.write(html)
            # else:
            #     logger.error(f"Page Source Not Found")
        if (html != False):
            data = self.parse_data(html)
        return data
    
    @abstractmethod
    def parse_data(self):
        """
        Method to parse the raw data and return structured data.
        """
        pass

    @abstractmethod
    def get_page_source(self):
        """
        Method to parse the raw data and return structured data.
        """
        pass

    def get_text(self, soup_obj, tag, cls):
        el = soup_obj.find(tag, class_=cls)
        return el.get_text(strip=True) if el else ''
    
    def get_attr(self, soup_obj, tag, cls, attr):
        if cls:
            el = soup_obj.find(tag, class_=cls)
        else:
            el = soup_obj.find(tag)
        return el[attr] if el and attr in el.attrs else ''

    def save_data(self, data, file_name = False):
        if(file_name == False):
            file_name = f"scrap_data_{self.__class__.__name__.lower()}.json"
        with open(file_name, "w") as file:
            # logger.info(f"Saving page source to {file_name}")
            if(Path(file_name).suffix == '.json'):
                json.dump(data, file, indent=4)
            elif(Path(file_name).suffix == '.txt'):
                file.write(data)
            else:
                # logger.error(f"Invalid file extension {Path(file_name).suffix}")
                raise Exception("Invalid Extension")