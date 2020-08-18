import os
import sys
import time
import urllib.parse

import pandas as pd
import scrapy
from scrapy.selector import Selector
from selenium import webdriver


# Ref : https://dev.to/hellomrspaceman/python-selenium-infinite-scrolling-3o12
def scroll(driver, timeout):
    scroll_pause_time = timeout
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(scroll_pause_time)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height

class SimilarAppsSpider(scrapy.Spider):
    name = "similar-apps-spider"
    BASE_URL = "https://play.google.com"

    # TODO : Make path relative
    FEATURED_APPS_PATH = "../data/featured_apps.csv"
    def __init__(self):
        # Check featured apps file is exists.
        if not os.path.exists(SimilarAppsSpider.FEATURED_APPS_PATH):
            print("SimilarAppsSpider.FEATURED_APPS_PATH does not exist")
            sys.exit(1)

        # Read init pages
        df = pd.read_csv(SimilarAppsSpider.FEATURED_APPS_PATH)

        # Initilalize visited set and waiting queue
        self.visited = set(df["app_id"])
        self.init_apps = list(self.visited)

    def start_requests(self):
        """
            Start crawling from featured apps.
        """
        for app_id in self.init_apps:
            url = urllib.parse.urljoin(SimilarAppsSpider.BASE_URL, "/store/apps/details?id={}".format(app_id))
            yield scrapy.Request(url=url, callback=self.visit_app_page)

    def visit_app_page(self, response):
        """
            Get App related info and similar apps.
        """
         # Get app permissions
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        driver = webdriver.Chrome(options=op)
        driver.implicitly_wait(30)
        driver.get(response.url)
        permission_page = driver.find_element_by_xpath('//a[@jsname="Hly47e"]')
        permission_page.click()
        webdriver.ActionChains(driver).move_to_element(permission_page).click(permission_page).perform()
        pop_up_page = driver.find_elements_by_xpath('//span[@class="SoU6Qc"]')
        permissions = []
        for permission in pop_up_page:
            permissions.append(permission.text)
        driver.close()


        #Get additional app info
        app_id = response.url.split("=")[-1]
        category_short = response.xpath('//a[@itemprop="genre"]/text()').get()
        category_long = response.xpath('//a[@itemprop="genre"]/@href').get()

        installs = response.xpath('//div[@class="IxB2fe"]/div[@class="hAyfc"]/*[text()="Installs"]/../span//text()').get()
        size = response.xpath('//div[@class="IxB2fe"]/div[@class="hAyfc"]/*[text()="Size"]/../span//text()').get()
        requred_android = response.xpath('//div[@class="IxB2fe"]/div[@class="hAyfc"]/*[text()="Requires Android"]/../span//text()').get()
        current_version = response.xpath('//div[@class="IxB2fe"]/div[@class="hAyfc"]/*[text()="Current Version"]/../span//text()').get()
        developer_site = response.xpath('//div[@class="IxB2fe"]/div[@class="hAyfc"]/*[text()="Developer"]/..//*[text()="Visit website"]/@href').get()
        developer_privacy_policy = response.xpath('//div[@class="IxB2fe"]/div[@class="hAyfc"]/*[text()="Developer"]/..//*[text()="Privacy Policy"]/@href').get()
        
        yield {
                "app_id" : app_id,
                "category_short" : category_short,
                "category_long" : category_long,
                "installs" : installs,
                "size" : size,
                "requred_android" : requred_android,
                "current_version" : current_version,
                "developer_site" : developer_site,
                "developer_privacy_policy" : developer_privacy_policy,
                "permissions" : "::".join(permissions)
            }

        # Open Similar apps page and scroll down
        href = response.xpath('//div[@class="xwY9Zc"]//*[text()="Similar"]/../@href').get()
        similar_apps_url = urllib.parse.urljoin(SimilarAppsSpider.BASE_URL, href)
        
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        driver = webdriver.Chrome(options=op)
        driver.implicitly_wait(30)
        driver.get(similar_apps_url)
        scroll(driver, 5)
        app_paths = Selector(text=driver.page_source).xpath('//c-wiz[@jsrenderer ="BQA5pf"]//div[@class="b8cIId ReQCgd Q9MA7b"]/a/@href').getall()
        driver.close()
        for app in app_paths:
            app_id = app.split("=")[-1]
            if app_id not in self.visited:
                self.visited.add(app_id)
                url = urllib.parse.urljoin(SimilarAppsSpider.BASE_URL, "/store/apps/details?id={}".format(app_id))
                yield scrapy.Request(url=url, callback=self.visit_app_page)
