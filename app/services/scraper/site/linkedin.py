from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.core.redis_conn import request_queue
from app.services.scraper.base import Scraper, Scrape
from app.services.scraper.driver import create_driver
from bs4 import BeautifulSoup
import time
from pathlib import Path
import logging
from memory_profiler import profile
from rq.job import get_current_job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInScraper(Scraper):
    def __init__(self, req: Scrape):
        super().__init__(req)

    def parse_data(self, html):
        data = []
        soup = BeautifulSoup(html, 'html.parser')
        jobSearchResultList = soup.find('ul', class_='jobs-search__results-list')
        logger.info('parsing data from page source start....')
        a = 0
        sub_job_ids = []
        for result in jobSearchResultList.find_all('li'):
            if(a >= 21):
                break
            try:
                jobDetail = {} 
                jobDetail['title'] = self.get_text(result, 'h3', 'base-search-card__title')
                jobDetail['subTitle'] = self.get_text(result, 'h4', 'base-search-card__subtitle')
                jobDetail['location'] = self.get_text(result, 'span', 'job-search-card__location')
                jobDetail['listDate'] = self.get_text(result, 'time', 'job-search-card__listdate')
                jobDetail['url'] = self.get_attr(result, 'a', 'base-card__full-link', 'href')
                sub_job = request_queue.enqueue(self.get_url_data, jobDetail['url'], str(a))
                sub_job_ids.append(sub_job.id)
                # jobDetail['extraDetail'] = self.get_url_data(jobDetail['url'], str(a))
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
            # super().save_data(html, 'linkedin'+filename+'.txt')
            data = self.parse_url_data(html)
            logger.info('saving parsed data')
            # super().save_data(data, 'linkedin'+filename+'.json')
        return data
    
    def parse_url_data(self, html):
        data = {}
        logger.info('parse url data')
        soup = BeautifulSoup(html, 'html.parser')
        description = soup.find('div', class_='description__text')
        if (description != None):
            el = description.find('section', class_='show-more-less-html')
            data['description'] = el.get_text(separator="\n", strip=True) if el else ''
            return data
        data['description'] = ''
        return data
    
    def get_page_source(self):
        with create_driver() as driver:
            driver.get('https://www.linkedin.com/jobs/search?trk=guest_homepage-basic_guest_nav_menu_jobs&position=1&pageNum=0')
            html = False
            logger.info(f"inside get page source from url")
            try:
                location_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'job-search-bar-location'))
                )
                search_keywords_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'job-search-bar-keywords'))
                )
                location_input.clear()
                location_input.send_keys(self.request.location)
                search_keywords_input.send_keys(self.request.job_title)
                location_input.send_keys(Keys.RETURN)
                time.sleep(0.2)
                logger.info(f"Element found, fetching page source.")
                html = driver.page_source
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
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'main-content'))
                )
                html = driver.page_source
                logger.info("we got html for sub url")
            except Exception as e:
                logger.error("WE GOT ERROR HERE " + e)
            finally:
                logger.info("driver quit")
                return html
        return html