from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.services.scraper.base import Scraper, Scrape
from app.services.scraper.driver import create_driver
from app.core.redis_conn import request_queue
from bs4 import BeautifulSoup
import time
from pathlib import Path
import logging
from memory_profiler import profile
from rq.job import get_current_job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GlassdoorScraper(Scraper):
    def __init__(self, req: Scrape):
        super().__init__(req)

    def parse_data(self, html):
        data = []
        soup = BeautifulSoup(html, 'html.parser')
        logger.info('parsing data from page source start....')
        sub_job_ids = []
        a = 0
        for result in soup.find_all('li', attrs={'data-test': 'jobListing'}):
            if(a >= 20):
                break
            try:
                jobTitleLink = result.find('a', attrs={'data-test': 'job-title'})
                location = result.find('div', attrs={'data-test': 'emp-location'})
                jobAge = result.find('div', attrs={'data-test': 'job-age'})
                jobDetail = {}
                jobDetail['title'] = jobTitleLink.get_text(strip=True) if jobTitleLink else ''
                jobDetail['subTitle'] = self.get_text(result, 'span', 'EmployerProfile_compactEmployerName__9MGcV')
                jobDetail['location'] = location.get_text(strip=True) if location else ''
                jobDetail['listDate'] = jobAge.get_text(strip=True) if jobAge else ''
                jobDetail['url'] = jobTitleLink['href'] if jobTitleLink and 'href' in jobTitleLink.attrs else ''
                # sub_job = request_queue.enqueue(self.get_url_data, jobDetail['url'], str(a))
                # sub_job_ids.append(sub_job.id)
                data.append(jobDetail)
                a = a+1
            except Exception as e:
                logger.error('something went wrong')
                a = a+5
        # parent_job = get_current_job()
        # parent_job.meta['sub_jobs'] = sub_job_ids
        # parent_job.save_meta()
        super().save_data(data)
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
            driver.get('https://www.glassdoor.co.in/Job/software-engineer-jobs-SRCH_KO0,17.htm')
            html = False
            logger.info(f"inside get page source from url")
            try:
                location_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'searchBar-jobTitle'))
                )
                search_keywords_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'searchBar-location'))
                )
                location_input.clear()
                location_input.send_keys(self.request.location)
                search_keywords_input.clear()
                search_keywords_input.send_keys(self.request.job_title)
                location_input.send_keys(Keys.RETURN)
                time.sleep(2)
                list_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'left-column'))
                )
                logger.info(f"Element found, fetching page source.")
                html = list_container.get_attribute('outerHTML')
            except Exception as e:
                logger.error("Getting Error while fetching source " + e)
            finally:
                return html
        
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
                driver.quit()
                return html