import scrapy
import json

from scrapy_splash import SplashRequest

from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class SpiderBetanoSpider(scrapy.Spider):
    name = "spider_betano"
    #allowed_domains = ["www.betano.cz", "localhost"]
    start_urls = ["https://www.betano.cz/api/"] # "https://www.betano.cz"

    custom_settings = {
        'FEEDS': {'data_betano.json': {'format': 'json', 'overwrite': True}},
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_ARGUMENTS': ['--headless'], # '--headless'
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_selenium.SeleniumMiddleware': 800
        }
        }

    def parse(self, response):
        resp_js = json.loads(response.text)
        for sport in resp_js["structureComponents"]["sports"]["data"]:
            url = 'https://www.betano.cz' + sport["url"] + 'nadchazejici-zapasy-dnes/?sort=StartTime'
            #yield {
            #    'origin-url': url
            #}
            #yield SplashRequest(url, callback=self.parse_sport_page, args={"wait": 5}) 
        url = 'https://www.betano.cz' + resp_js["structureComponents"]["sports"]["data"][0]["url"] + 'nadchazejici-zapasy-dnes/?sort=StartTime'
        #yield response.follow(url, callback = self.parse_sport_page)
        #yield scrapy.Request(url, meta={"playwright": True})
        #yield SplashRequest(url, callback=self.parse_sport_page, endpoint="execute", args={"lua_source": lua_script})
        #yield SplashRequest(url, callback=self.parse_sport_page, args={"wait": 15}) 
        yield SeleniumRequest(url=url, callback=self.parse_sport_page, wait_time=15, wait_until=EC.element_to_be_clickable((By.CLASS_NAME, 'tw-flex'))) # selections__selection tw-flex

    def parse_sport_page(self, response):
        yield {
            'url': response.url,
            'text': response.css('h1').get()
        }