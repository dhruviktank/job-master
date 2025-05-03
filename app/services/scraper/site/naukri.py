from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.services.scraper.base import Scraper, Scrape
from app.core.redis_conn import request_queue
from app.services.scraper.driver import create_driver
from bs4 import BeautifulSoup
import time
from pathlib import Path
import logging
from memory_profiler import profile
from rq.job import get_current_job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class NaukriScraper(Scraper):
    def __init__(self, req: Scrape):
        super().__init__(req)

    def parse_data(self, html):
        data = []
        soup = BeautifulSoup(html, 'html.parser')
        logger.info('parsing data from page source start....')
        sub_job_ids = []
        a = 0
        for result in soup.find_all('div', class_='srp-jobtuple-wrapper'):
            if(a >= 20):
                break
            try:
                row1 = soup.find('div', class_='row1')
                jobDetail = {}
                jobDetail['title'] = self.get_attr(row1, 'a', 'title', 'title')
                jobDetail['subTitle'] = self.get_text(result, 'div', 'row2')
                jobDetail['location'] = self.get_text(result, 'span', 'loc-wrap')
                jobDetail['listDate'] = self.get_text(result, 'span', 'job-post-day')
                jobDetail['url'] = self.get_attr(row1, 'a', 'title', 'href')
                sub_job = request_queue.enqueue(self.get_url_data, jobDetail['url'], str(a))
                sub_job_ids.append(sub_job.id)
                data.append(jobDetail)
                a = a+1
            except Exception as e:
                logger.error('something went wrong')
                a = a+5
        parent_job = get_current_job()
        parent_job.meta['sub_jobs'] = sub_job_ids
        parent_job.save_meta()
        # super().save_data(data)
        return data
    
    def get_url_data(self, url, filename):
        html = False
        data = ''
        # if(Path(filename+'.txt').exists()):
        #     logger.info(f"Reading from {filename+'.txt'}")
        #     with open(filename+'.txt', 'r') as file:
        #         html = file.read()
        if(html == False):
            logger.info("Parsing Sub Page Source")
            html = self.get_url_page_source(url)
        if(html):
            # super().save_data(html, 'naukri'+filename+'.txt')
            data = self.parse_url_data(html)
            logger.info('saving parsed data')
            # super().save_data(data, 'naukri'+filename+'.json')
        return data
    
    def parse_url_data(self, html):
        data = {}
        logger.info('parse url data')
        soup = BeautifulSoup(html, 'html.parser')
        data['description'] = soup.get_text(separator="\n", strip=True)
        return data
    
    def get_page_source(self):
        with create_driver() as driver:
            driver.get('https://www.naukri.com/')
            html = False
            logger.info(f"inside get page source from url")
            try:
                location_wrapper = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'locationSugg'))
                )
                search_keywords_wrapper = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'keywordSugg'))
                )
                location_input = location_wrapper.find_element(By.CSS_SELECTOR, 'input.suggestor-input')
                search_keywords_input = search_keywords_wrapper.find_element(By.CSS_SELECTOR, 'input.suggestor-input')
                location_input.clear()
                location_input.send_keys(self.request.location)
                search_keywords_input.send_keys(self.request.job_title)
                location_input.send_keys(Keys.RETURN)
                time.sleep(2)
                list_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'listContainer'))
                )
                logger.info(f"Element found, fetching page source.")
                html = list_container.get_attribute('outerHTML')
            except Exception as e:
                logger.error("Getting Error while fetching source " + e)
            finally:
                logger.info("exiting get_page_source with nothing")
                return html
        return False
        
    def get_url_page_source(self, url):
        html = ''
        logger.info("url page source getting start")
        with create_driver() as driver:
            driver.get(url)
            logger.info("driver fetched successfully")
            try:
                logger.info("waiting for main content")
                description_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'styles_job-desc-container__txpYf'))
                )
                html = description_container.get_attribute('outerHTML')
                logger.info("we got html for sub url")
            except Exception as e:
                logger.error("WE GOT ERROR HERE " + e)
            finally:
                logger.info("driver quit")
                return html
        return False