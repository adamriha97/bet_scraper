import scrapy
import json

#from scrapy_splash import SplashRequest

#from scrapy_selenium import SeleniumRequest
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support import expected_conditions as EC

from scrapy_playwright.page import PageMethod


def intercept_request(request):
    # Block requests to Google by checking if "google" is in the URL
    if 'google' in request.url:
        request.abort()
    else:
        request.continue_()


def handle_route_abort(route):
    if route.request.resource_type in ("image", "webp"):
        route.abort()
    else:
        route.continue_()

class SpiderBetanoSpider(scrapy.Spider):
    name = "spider_betano"
    #allowed_domains = ["www.betano.cz", "localhost"]
    #start_urls = ["https://www.betano.cz/api/"] # "https://www.betano.cz"

    custom_settings = {
        'FEEDS': {'data_betano.json': {'format': 'json', 'overwrite': True}}
    #    'SELENIUM_DRIVER_NAME': 'chrome',
    #    'SELENIUM_DRIVER_ARGUMENTS': ['--headless'], # '--headless'
    #    'DOWNLOADER_MIDDLEWARES': {
    #        'scrapy_selenium.SeleniumMiddleware': 800
    #    }
        }

    def start_requests(self):
        #url = "https://quotes.toscrape.com/scroll"
        url = "https://www.betano.cz/sport/fotbal/nadchazejici-zapasy-dnes/?sort=StartTime"
        yield scrapy.Request(url, meta=dict(
				playwright = True,
				playwright_include_page = True, 
				playwright_page_methods =[
                    #PageMethod("wait_for_selector", "div.quote"),
                    #PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                    #PageMethod("wait_for_selector", "div.quote:nth-child(11)"),  # 10 per page
                    PageMethod("wait_for_load_state", "load"),
                    PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                    PageMethod("wait_for_selector", "h1"),
                ],
                errback=self.errback,
			))

    async def parse(self, response):
        #page = response.meta["playwright_page"]
        #await page.close()
         
        for game in response.css('div.vue-recycle-scroller__item-view'):
            yield {
                'date': game.css('span ::text').get(),
                'bet': game.css('div.selections__selection span ::text').get()
            }
  
    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
    
    def parse_bet(self, response):
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
        #yield SeleniumRequest(url=url, callback=self.parse_sport_page, wait_time=15, wait_until=EC.element_to_be_clickable((By.CLASS_NAME, 'tw-flex'))) # selections__selection tw-flex

    def parse_sport_page(self, response):
        yield {
            'url': response.url,
            'text': response.css('h1').get()
        }