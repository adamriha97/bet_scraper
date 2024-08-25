import scrapy
from scrapy_playwright.page import PageMethod
import xml.etree.ElementTree as ET


def should_abort_request(req):
    if req.resource_type in ["image", "media", "font", "webp"]:
        return True
    if '.svg' in req.url:
        return True
    if 'google' in req.url:
        return True
    return False

class SpiderTipsportSpider(scrapy.Spider):
    name = "spider_tipsport"
    allowed_domains = ["www.tipsport.cz"]
    # start_urls = ["https://www.tipsport.cz/kurzy.xml"] # https://www.tipsport.cz/

    # custom_settings = {
    #     'FEEDS': {'data_tipsport.json': {'format': 'json', 'overwrite': True}},
    #     'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0"
    #     }

    custom_settings = {
        'FEEDS': {'data_tipsport.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        # 'REACTOR_THREADPOOL_MAXSIZE ': 100,
        # 'DEFAULT_REQUEST_HEADERS': {
        #     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        #     "Accept-Language": "cs", # cs en
        # },
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            "headless": False, # True False
            "timeout": 600 * 1000,  # 60 seconds
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 600 * 1000,  # 60 seconds
        'PLAYWRIGHT_ABORT_REQUEST': should_abort_request,
        # 'PLAYWRIGHT_MAX_PAGES_PER_CONTEXT': 1,
        # 'PLAYWRIGHT_CONTEXTS': {
        #     "cz_context": {
        #         "locale": "cs-CZ", # cs-CZ en-GB
        #         "geolocation": {'longitude': 14.418540, 'latitude': 50.073658}, # 14.418540 50.073658 12.492507 41.889938
        #         "permissions": ['geolocation'],
        #         "viewport": {"width": 720, "height": 720}, # https://playwright.dev/docs/emulation#viewport # https://medium.com/@arslandevs/automate-web-scraping-with-scrapy-playwright-and-cron-a-powerful-combination-458f48fdba21
        #     },
        # },
        'DOWNLOADER_MIDDLEWARES': {
            "scrapy.downloadermiddlewares.cookies.CookiesMiddleware": 543,
        },
        }
    
    def start_requests(self):
        last_urls = ['https://www.tipsport.cz/kurzy.xml'] # https://www.tipsport.cz/kurzy/fotbal-16?limit=9999 https://www.tipsport.cz/kurzy.xml
        for url in last_urls:
            yield scrapy.Request(url, meta=dict(
			    	playwright = True,
			    	playwright_include_page = True, 
			    	# playwright_page_methods =[
                    #     PageMethod("wait_for_selector", "div.quote"),
                    #     PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                    #     PageMethod("wait_for_selector", "div.quote:nth-child(11)"),  # 10 per page
                    #     PageMethod("wait_for_load_state", "load"),
                    #     PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                    #     PageMethod("wait_for_selector", "h1"),
                    #     PageMethod("wait_for_selector", "div.Matchstyled__Name-sc-5rxr4z-6"),
                    # ],
                    # errback=self.errback,
			    ), callback = self.parse)

    def parse(self, response):
        root = ET.fromstring(response.text.split('<div id=\"webkit-xml-viewer-source-xml\">')[1].split('</div>')[0])
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [url.find('ns:loc', namespaces).text for url in root.findall('ns:url', namespaces)]
        not_interested = ['cyklistika', 'motorsport', 'spolecenske-sazky']
        for url in urls:
            if len(url.split('/')) == 5 and url.split('/')[-1].rsplit('-', 1)[0] not in not_interested:
                yield {
                    'len': len(url.split('/')),
                    'url': url,
                    'sport': url.split('/')[-1].rsplit('-', 1)[0],
                }
    
    def parse_sport(self, response):
        teams = response.css('div.Matchstyled__Name-sc-5rxr4z-6 span ::text').getall()
        for team in teams:
            yield {
                # 'url': response.url,
                # 'text': response.text,
                'teams': team,
            }