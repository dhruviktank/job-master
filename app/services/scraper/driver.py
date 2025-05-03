from selenium import webdriver
from selenium.webdriver.chromium.options import ChromiumOptions
from contextlib import contextmanager

@contextmanager
def create_driver():
    options = ChromiumOptions()
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    # options.binary_location = "/usr/bin/chromium"
    driver = webdriver.Remote("http://selenium:4444/wd/hub", options=options)
    try:
        yield driver
    finally:
        driver.quit()