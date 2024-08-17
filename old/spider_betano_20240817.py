import scrapy

import json
import xml.etree.ElementTree as ET

from scrapy_playwright.page import PageMethod

abort_since_bool = False

def should_abort_request(req):
    global abort_since_bool
    if abort_since_bool:
        return abort_since_bool
    if req.url in ['https://www.betano.cz/api/static-content/assets', 'https://www.googletagmanager.com/gtm.js?id=GTM-NXKMPPV', 'https://sdkuaservice.optimove.net/', 'https://stream-922.optimove.net/', 'https://realtime-922.optimove.net/reportEvent', 'https://www.betano.cz/assets/static/fonts/ubuntu/ubuntu-v20-latin-ext_latin_greek-ext_cyrillic-ext_cyrillic-regular.woff2', 'https://realtime-922.optimove.net/reportEvent', 'https://static.app.delivery/sdks/web/optimove-web-bundle.js', 'https://www.betano.cz/cdn-cgi/challenge-platform/scripts/jsd/main.js', 'https://www.betano.cz/bundle.a566a830054cdefc1368.worker.js']:
        return True
    if req.url == 'https://dd.betano.cz/js/':
        abort_since_bool = True
    return abort_since_bool

max_number_of_events = 1
number_of_event = 0

class SpiderBetanoSpider(scrapy.Spider):
    name = "spider_betano"
    allowed_domains = ["www.betano.cz"]
    start_urls = ["https://www.betano.cz/sitemap_events.xml/"] # "https://www.betano.cz" https://www.betano.cz/api/

    custom_settings = {
        'FEEDS': {'data_betano.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'REACTOR_THREADPOOL_MAXSIZE ': 100,
        'DEFAULT_REQUEST_HEADERS': {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "cs", # cs en
        },
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            "headless": False, # True False
            "timeout": 600 * 1000,  # 60 seconds
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 600 * 1000,  # 60 seconds
        'PLAYWRIGHT_ABORT_REQUEST': should_abort_request,
        'PLAYWRIGHT_MAX_PAGES_PER_CONTEXT': 1,
        'PLAYWRIGHT_CONTEXTS': {
            "cz_context": {
                "locale": "cs-CZ", # cs-CZ en-GB
                "geolocation": {'longitude': 14.418540, 'latitude': 50.073658}, # 14.418540 50.073658 12.492507 41.889938
                "permissions": ['geolocation'],
                "viewport": {"width": 720, "height": 720}, # https://playwright.dev/docs/emulation#viewport # https://medium.com/@arslandevs/automate-web-scraping-with-scrapy-playwright-and-cron-a-powerful-combination-458f48fdba21
            },
        }
        }

    def parse(self, response):
        root = ET.fromstring(response.text)
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        loc_elements = root.findall('.//ns:loc', namespaces)
        filtered_urls = [loc.text for loc in loc_elements if '/zapas-sance/' in loc.text]
        selected_urls = filtered_urls[-51-number_of_event:-50-number_of_event]
        for url in selected_urls:
            yield scrapy.Request(url, meta=dict(
			    	playwright = True,
                    playwright_context = "cz_context",
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
        global number_of_event, max_number_of_events, abort_since_bool
         
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
        abort_since_bool = False

        #number_of_event += 1
        #if number_of_event < max_number_of_events:
        #    yield response.follow("https://www.betano.cz/sitemap_events.xml/", callback = self.parse)
  
    async def errback(self, failure):
        pass
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