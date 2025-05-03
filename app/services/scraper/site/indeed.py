import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chromium.options import ChromiumOptions
from app.services.scraper.base import Scraper, Scrape
from bs4 import BeautifulSoup
import time
from pathlib import Path
import logging
from memory_profiler import profile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class IndeedScraper(Scraper):
    def __init__(self, req: Scrape):
        super().__init__(req)

    def parse_data(self, html):
        data = []
        soup = BeautifulSoup(html, 'html.parser')
        # jobSearchResultList = soup.find('ul', class_='jobs-search__results-list')
        # logger.info('parsing data from page source start....')
        # a = 0
        # for result in jobSearchResultList.find_all('li'):
        #     if(a >= 21):
        #         break
        #     try:
        #         jobDetail = {} 
        #         jobDetail['title'] = self.get_text(result, 'h3', 'base-search-card__title')
        #         jobDetail['subTitle'] = self.get_text(result, 'h4', 'base-search-card__subtitle')
        #         jobDetail['location'] = self.get_text(result, 'span', 'job-search-card__location')
        #         jobDetail['listDate'] = self.get_text(result, 'time', 'job-search-card__listdate')
        #         jobDetail['url'] = self.get_attr(result, 'a', 'base-card__full-link', 'href')
        #         jobDetail['extraDetail'] = self.get_url_data(jobDetail['url'], str(a))
        #         data.append(jobDetail)
        #         a = a+1
        #     except Exception as e:
        #         logger.error('something went wrong')
        #         a = a+5
        # super().save_data(data)
        return data
    
    def get_url_data(self, url, filename):
        html = False
        data = ''
        if(Path(filename+'.txt').exists()):
            logger.info(f"Reading from {filename+'.txt'}")
            with open(filename+'.txt', 'r') as file:
                html = file.read()
        if(html == False):
            logger.info("Parsing Sub Page Source")
            html = self.get_url_page_source(url)
        if(html):
            super().save_data(html, filename+'.txt')
            data = self.parse_url_data(html)
            logger.info('saving parsed data')
            # super().save_data(data, filename+'.json')
        return data
    
    def parse_url_data(self, html):
        data = {}
        logger.info('parse url data')
        soup = BeautifulSoup(html, 'html.parser')
        description = soup.find('div', class_='description__text')
        el = description.find('section', class_='show-more-less-html')
        data['description'] = el.get_text(separator="\n", strip=True) if el else ''
        return data
    
    def get_page_source(self):
        options = ChromiumOptions()
        # options.add_argument('--headless')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        # driver = webdriver.Chrome(options=options)
        driver = uc.Chrome()
        driver.get('https://in.indeed.com/?from=gnav-jobsearch--indeedmobile')
        html = False
        logger.info(f"inside get page source from url")
        try:
            logger.info(f"waiting for elements")
            location_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'text-input-where'))
            )
            search_keywords_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'text-input-what'))
            )

            location_input.clear()
            location_input.send_keys(self.request.location)
            time.sleep(1)
            search_keywords_input.send_keys(self.request.job_title)
            time.sleep(1.5)
            location_input.send_keys(Keys.RETURN)
            # WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.ID, 'mosaic-jobResults'))
            # )
            logger.info(f"Element found, fetching page source.")
            html = driver.page_source
        except Exception as e:
            logger.error("Getting Error while fetching source " + e)
        finally:
            logger.info("exiting get_page_source with nothing")
            driver.quit()
            return html
        
    def get_url_page_source(self, url):
        html = ''
        print(url)
        logger.info("url page source getting start")
        options = ChromiumOptions()
        options.add_argument('--headless')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        drivernew = webdriver.Chrome(options=options)
        drivernew.get(url)
        logger.info("driver fetched successfully")
        try:
            logger.info("waiting for main content")
            WebDriverWait(drivernew, 10).until(
                EC.presence_of_element_located((By.ID, 'main-content'))
            )
            html = drivernew.page_source
            logger.info("we got html for sub url")
        except Exception as e:
            logger.error("WE GOT ERROR HERE " + e)
        finally:
            logger.info("driver quit")
            drivernew.quit()
            return html