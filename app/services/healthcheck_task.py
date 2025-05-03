# healthcheck_task.py

from app.core.redis_conn import request_queue  # or wherever your RQ queue is
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def health_check_job():
    logger.info("Starting Selenium health check job...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.google.com")
        title = driver.title
        logger.info(f"Page title is: {title}")
        return title
    finally:
        driver.quit()
        logger.info("Driver closed cleanly.")
