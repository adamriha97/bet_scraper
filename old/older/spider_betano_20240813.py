import scrapy

import json
import xml.etree.ElementTree as ET

#from scrapy_splash import SplashRequest

#from scrapy_selenium import SeleniumRequest
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support import expected_conditions as EC

from scrapy_playwright.page import PageMethod

import logging

abort_since_url = 'https://www.betano.cz/cdn-cgi/challenge-platform/scripts/jsd/main.js'
abort_since_bool = False

def should_abort_request(req): # should_abort_request
    global abort_since_bool
    if abort_since_bool:
        return abort_since_bool
    if req.url in ['https://www.betano.cz/api/static-content/assets', 'https://www.googletagmanager.com/gtm.js?id=GTM-NXKMPPV', 'https://sdkuaservice.optimove.net/', 'https://stream-922.optimove.net/', 'https://realtime-922.optimove.net/reportEvent', 'https://www.betano.cz/assets/static/fonts/ubuntu/ubuntu-v20-latin-ext_latin_greek-ext_cyrillic-ext_cyrillic-regular.woff2', 'https://realtime-922.optimove.net/reportEvent', 'https://static.app.delivery/sdks/web/optimove-web-bundle.js', 'https://www.betano.cz/cdn-cgi/challenge-platform/scripts/jsd/main.js', 'https://www.betano.cz/bundle.a566a830054cdefc1368.worker.js']:
        return True
    if req.url == 'https://dd.betano.cz/js/':
        abort_since_bool = True
    return abort_since_bool

def should_abort_request_old(req): # should_abort_request_old
    if '.svg' in req.url:
        logging.log(logging.INFO, f"Ignoring {req.method} {req.url} ")
        return True
    if req.resource_type in ["image", "media", "font"]:
        logging.log(logging.INFO, f"Ignoring {req.resource_type} {req.url}")
        return True
    if req.method.lower() == 'post':
        logging.log(logging.INFO, f"Ignoring {req.method} {req.url} ")
        return True
    return False

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

max_number_of_events = 1
number_of_event = 0

class SpiderBetanoSpider(scrapy.Spider):
    name = "spider_betano"
    allowed_domains = ["www.betano.cz"] # , "localhost"
    # start_urls = ["https://www.betano.cz/sitemap_events.xml/"] # "https://www.betano.cz" https://www.betano.cz/api/

    custom_settings = {
        'FEEDS': {'data_betano.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            "headless": False, # True False
            "timeout": 600 * 1000,  # 60 seconds
            "args": [
                #"--window-size='200,400'"
                #"--start-maximized"
                '--device="iPhone 13"'
            ],
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 600 * 1000,  # 60 seconds
        'PLAYWRIGHT_ABORT_REQUEST': should_abort_request,
        'PLAYWRIGHT_MAX_PAGES_PER_CONTEXT': 1
    #    'SELENIUM_DRIVER_NAME': 'chrome',
    #    'SELENIUM_DRIVER_ARGUMENTS': ['--headless'], # '--headless'
    #    'DOWNLOADER_MIDDLEWARES': {
    #        'scrapy_selenium.SeleniumMiddleware': 800
    #    }
        }

    def start_requests(self):
        last_urls = ['https://www.betano.cz/zapas-sance/colo-colo-klub-atletico-junior/50197496/']
        for url in last_urls:
            yield scrapy.Request(url, meta=dict(
			    	playwright = True,
			    	playwright_include_page = True, 
			    	#playwright_page_methods =[
                        #PageMethod("wait_for_selector", "div.quote"),
                        #PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                        #PageMethod("wait_for_selector", "div.quote:nth-child(11)"),  # 10 per page
                        #PageMethod("wait_for_load_state", "load"),
                        #PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                        #PageMethod("wait_for_selector", "h1"),
                        #PageMethod("wait_for_selector", ".markets"),
                    #],
                    errback=self.errback,
			    ), callback = self.parse_event_page)

    def parse(self, response): # start_requests(self)
        # Parse the XML string
        root = ET.fromstring(response.text)
        # Namespace dictionary
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        # Extract all loc elements
        loc_elements = root.findall('.//ns:loc', namespaces)
        # Filter URLs containing '/zapas-sance/'
        filtered_urls = [loc.text for loc in loc_elements if '/zapas-sance/' in loc.text]
        #url = "https://quotes.toscrape.com/scroll"
        #url = "https://www.betano.cz/zapas-sance/bohemians-1905-ac-sparta-praha/51640154/" # "https://www.betano.cz/sport/fotbal/nadchazejici-zapasy-dnes/?sort=StartTime"
        #url = filtered_urls[-1]
        last_urls = filtered_urls[-51-number_of_event:-50-number_of_event]
        for url in last_urls:
            yield scrapy.Request(url, meta=dict(
			    	playwright = True,
			    	playwright_include_page = True, 
			    	#playwright_page_methods =[
                        #PageMethod("wait_for_selector", "div.quote"),
                        #PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                        #PageMethod("wait_for_selector", "div.quote:nth-child(11)"),  # 10 per page
                        #PageMethod("wait_for_load_state", "load"),
                        #PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                        #PageMethod("wait_for_selector", "h1"),
                        #PageMethod("wait_for_selector", ".markets"),
                    #],
                    errback=self.errback,
			    ), callback = self.parse_event_page)

    async def parse_event_page(self, response):
        global number_of_event, max_number_of_events
        #page = response.meta["playwright_page"]
        #await page.close()
         
        #for game in response.css('div.vue-recycle-scroller__item-view'):
        #    yield {
        #        'date': game.css('span ::text').get(),
        #        'bet': game.css('div.selections__selection span ::text').get()
        #    }

        try:
            yield {
                'sport': response.css('a.breadcrumbs-container__list__item__link')[1].css('::text').get(),
                'day': response.css('div.vertical-overflow-container')[1].css('section div.tw-font-bold ::text').get()
            }
        except:
            pass
        page = response.meta["playwright_page"]
        await page.close()

        number_of_event += 1
        if number_of_event < max_number_of_events:
            yield response.follow("https://www.betano.cz/sitemap_events.xml/", callback = self.parse)
  
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