import time
import urllib.parse

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

class FeaturedAppsSpider(scrapy.Spider):
    name = "featured-apps-spider"
    BASE_URL = "https://play.google.com"
    CATEGORIES = {"categories":[{"cat_key":"OVERALL","name":"Overall"},{"cat_key":"APPLICATION","name":"All apps"},{"cat_key":"GAME","name":"All games"},{"cat_key":"ART_AND_DESIGN","name":"Art & Design"},{"cat_key":"AUTO_AND_VEHICLES","name":"Auto & Vehicles"},{"cat_key":"BEAUTY","name":"Beauty"},{"cat_key":"BOOKS_AND_REFERENCE","name":"Books & Reference"},{"cat_key":"BUSINESS","name":"Business"},{"cat_key":"COMICS","name":"Comics"},{"cat_key":"COMMUNICATION","name":"Communication"},{"cat_key":"DATING","name":"Dating"},{"cat_key":"EDUCATION","name":"Education"},{"cat_key":"ENTERTAINMENT","name":"Entertainment"},{"cat_key":"EVENTS","name":"Events"},{"cat_key":"FINANCE","name":"Finance"},{"cat_key":"FOOD_AND_DRINK","name":"Food & Drink"},{"cat_key":"HEALTH_AND_FITNESS","name":"Health & Fitness"},{"cat_key":"HOUSE_AND_HOME","name":"House & Home"},{"cat_key":"LIFESTYLE","name":"Lifestyle"},{"cat_key":"MAPS_AND_NAVIGATION","name":"Maps & Navigation"},{"cat_key":"MEDICAL","name":"Medical"},{"cat_key":"MUSIC_AND_AUDIO","name":"Music & Audio"},{"cat_key":"NEWS_AND_MAGAZINES","name":"News & Magazines"},{"cat_key":"PARENTING","name":"Parenting"},{"cat_key":"PERSONALIZATION","name":"Personalization"},{"cat_key":"PHOTOGRAPHY","name":"Photography"},{"cat_key":"PRODUCTIVITY","name":"Productivity"},{"cat_key":"SHOPPING","name":"Shopping"},{"cat_key":"SOCIAL","name":"Social"},{"cat_key":"SPORTS","name":"Sports"},{"cat_key":"TOOLS","name":"Tools"},{"cat_key":"TRAVEL_AND_LOCAL","name":"Travel & Local"},{"cat_key":"VIDEO_PLAYERS","name":"Video Players & Editors"},{"cat_key":"WEATHER","name":"Weather"},{"cat_key":"LIBRARIES_AND_DEMO","name":"Libraries & Demo"},{"cat_key":"GAME_ARCADE","name":"Arcade"},{"cat_key":"GAME_PUZZLE","name":"Puzzle"},{"cat_key":"GAME_CARD","name":"Cards"},{"cat_key":"GAME_CASUAL","name":"Casual"},{"cat_key":"GAME_RACING","name":"Racing"},{"cat_key":"GAME_SPORTS","name":"Sport Games"},{"cat_key":"GAME_ACTION","name":"Action"},{"cat_key":"GAME_ADVENTURE","name":"Adventure"},{"cat_key":"GAME_BOARD","name":"Board"},{"cat_key":"GAME_CASINO","name":"Casino"},{"cat_key":"GAME_EDUCATIONAL","name":"Educational"},{"cat_key":"GAME_MUSIC","name":"Music Games"},{"cat_key":"GAME_ROLE_PLAYING","name":"Role Playing"},{"cat_key":"GAME_SIMULATION","name":"Simulation"},{"cat_key":"GAME_STRATEGY","name":"Strategy"},{"cat_key":"GAME_TRIVIA","name":"Trivia"},{"cat_key":"GAME_WORD","name":"Word Games"},{"cat_key":"ANDROID_WEAR","name":"Android Wear"},{"cat_key":"FAMILY","name":"Family All Ages"},{"cat_key":"FAMILY_UNDER_5","name":"Family Ages 5 & Under"},{"cat_key":"FAMILY_6_TO_8","name":"Family Ages 6-8"},{"cat_key":"FAMILY_9_AND_UP","name":"Family Ages 9 & Up"},{"cat_key":"FAMILY_ACTION","name":"Family Action"},{"cat_key":"FAMILY_BRAINGAMES","name":"Family Brain Games"},{"cat_key":"FAMILY_CREATE","name":"Family Create"},{"cat_key":"FAMILY_EDUCATION","name":"Family Education"},{"cat_key":"FAMILY_MUSICVIDEO","name":"Family Music & Video"},{"cat_key":"FAMILY_PRETEND","name":"Family Pretend Play"}]}

    def start_requests(self):
        """
            Get Category Pages.
        """
        for index, category in enumerate(FeaturedAppsSpider.CATEGORIES["categories"]):
            url = urllib.parse.urljoin(BASE_URL, "/store/apps/category/", "/{}?hl=en".format(category["cat_key"]))
            yield scrapy.Request(url=url, callback=self.show_category_page)

    def show_category_page(self, response):
        """
            List all apps belogs to category.
        """
        see_more_pages = response.xpath('//a[@class="LkLjZd ScJHi U8Ww7d xjAeve nMZKrb  id-track-click "]/@href').getall()
        for see_more in see_more_pages:
            url = urllib.parse.urljoin(FeaturedAppsSpider.BASE_URL, see_more)
            
            # Scroll Down and get all page
            op = webdriver.ChromeOptions()
            op.add_argument('headless')
            driver = webdriver.Chrome(options=op)
            driver.implicitly_wait(30)
            driver.get(url)
            scroll(driver, 5)
            paths = Selector(text=driver.page_source).xpath('//*[@class="b8cIId ReQCgd Q9MA7b"]//@href').getall()
            driver.close()
            # Iterate over app urls
            for p in paths:
                app_url = urllib.parse.urljoin(FeaturedAppsSpider.BASE_URL, p)
                yield scrapy.Request(url=app_url, callback=self.visit_app_page)
    
    def visit_app_page(self, response):
        """
            Visit app page and save app_id and category info.
        """
        url = response.url
        app_id = url.split("=")[-1]
        category_long = response.xpath('//a[@itemprop="genre"]/@href').get()
        category_short = response.xpath('//a[@itemprop="genre"]/text()').get()

        yield  {
                "app_id" : app_id,
                "category_short" : category_short,
                "category_long" : category_long }  
    
