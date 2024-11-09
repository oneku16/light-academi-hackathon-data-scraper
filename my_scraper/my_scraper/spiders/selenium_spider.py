from random import choice
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support import expected_conditions as ec

import json

# Define the XPaths you are using
SELECTOR = {
        'not_robot': '/html/body/div[1]/div/main/div/form/div[3]/div/div[1]/div[1]/input',
        'ads_exit': '/html/body/div[1]/div/div[15]/div/div[2]/div/div/div/div/div[1]/button',
        'item': '/html/body/div[1]/div/div[2]/div/div[1]/div[4]/div/div/div[5]/div/div/div/div[2]/div/div[1]/div/div/div[3]/div/div[{}]',
        'item_name': '/html/body/div[1]/div/div[2]/div/div[1]/div[4]/div/div/div[5]/div/div/div/div[2]/div/div[1]/div/div/div[2]/div/div[{}]/div/article/div/div/div[1]/div/div[2]/div[1]/div/a/span',
        'price':     '/html/body/div[1]/div/div[2]/div/div[1]/div[4]/div/div/div[5]/div/div/div/div[2]/div/div[1]/div/div/div[4]/div/div[{}]/div/article/div/div/div[1]/div/div[3]/div[2]/div/div/a/div/div/div/div/div'
}

'''

/html/body/div[1]/div/div[2]/div/div[1]/div[4]/div/div/div[5]/div/div/div/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/article/div/div/div[1]/div/div[3]/div/div/div/a/div/div[2]/span[1]/span[1]
'''

class SeleniumSpider(scrapy.Spider):
    name = 'selenium_spider'
    allowed_domains = ['market.yandex.ru']
    start_urls = ['https://market.yandex.ru/catalog--noutbuki/26895412/list?hid=91013&local-offers-first=0']

    def __init__(self, *args, **kwargs):
        super(SeleniumSpider, self).__init__(*args, **kwargs)

        self.chrome_options = Options()
        self.chrome_options.add_argument("--start-maximized")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.USER_AGENTS = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/102.0",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        ]
        self.chrome_options.add_argument(f"user-agent={choice(self.USER_AGENTS)}")

        # Initialize the WebDriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.chrome_options
        )

    def is_element_present(self, xpath):
        """Check if an element exists by its XPath."""
        try:
            wait = WebDriverWait(self.driver, 5)
            wait.until(ec.presence_of_element_located((By.XPATH, xpath)))
            print(f'{xpath=} is present.')
            return True
        except TimeoutException:
            print(f'{xpath=} is not present.')
            return False

    def click_element(self, xpath):
        """Click an element based on its XPath."""
        try:
            element = self.driver.find_element(by=By.XPATH, value=xpath)
            element.click()
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Error clicking element: {e}")

    def scroll_page(self, duration=20):
        """Scroll down the page to load more items."""
        start_time = time.time()
        while time.time() - start_time < duration:
            self.driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)

    def scrape_data(self):
        """Scrape data from the items on the page."""
        data = {}
        for i in range(4, 30):  # Adjust range as needed
            item_xpath = SELECTOR['item_name'].format(i)
            # item_price = SELECTOR['price'].format(i)
            try:
                # Check if the element exists
                if self.is_element_present(item_xpath):
                    # Extract the text of the item
                    element = self.driver.find_element(By.XPATH, item_xpath)
                    # price = self.driver.find_element(By.XPATH, item_price)
                    data[i] = {'item_name': '', 'item_price': ''}
                    data[i]['item_name'] = element.text
                    # data[i]['item_price'] = price.text
            except NoSuchElementException:
                pass
        return data

    def parse(self, response):
        """Use Selenium to load and scrape the page."""
        self.driver.get(response.url)
        time.sleep(2)

        # Handle popups if present
        # if self.is_element_present(SELECTOR['ads_exit']):
        self.click_element(SELECTOR['ads_exit'])

        self.scroll_page(10)
        # time.sleep(100)
        scraped_data = self.scrape_data()
        print(f"Scraped Data: {scraped_data}")
        #
        self.driver.quit()

        import random

        with open(f"your_json_file{random.randint(1, 100000)}", "w") as fp:
            json.dump(scraped_data, fp)
