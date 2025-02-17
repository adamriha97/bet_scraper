import scrapy
import json


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
        # 'PLAYWRIGHT_ABORT_REQUEST': should_abort_request,
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
        last_urls = ['https://www.tipsport.cz/kurzy.xml'] # https://www.tipsport.cz/kurzy/fotbal-16?limit=175 https://www.tipsport.cz/kurzy.xml
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
                    #     PageMethod("wait_for_selector", ".markets"),
                    # ],
                    # errback=self.errback,
			    ), callback = self.parse)

    def parse(self, response):
        # yield {
        #     'url': response.url,
        #     #'text': response.text,
        # }
        url = 'https://www.tipsport.cz/rest/offer/v2/offer?limit=500'
        body = '{results:false,highlightAnyTime:false,limit:500,type:SUPERSPORT,id:16,fulltexts:^[^],matchIds:^[^],matchViewFilters:^[^]}'
        body_2 = '{results:false,highlightAnyTime:false,limit:500,type:SUPERSPORT,id:16,fulltexts:[],matchIds:[],matchViewFilters:[]}'
        body_json = {
            "results": False,
            "highlightAnyTime": False,
            "limit": 500,
            "type": "SUPERSPORT",
            "id": 2,
            "fulltexts": [],
            "matchIds": [],
            "matchViewFilters": []
        }
        print('\n XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \n')
        print(response.headers.getlist('Set-Cookie'))
        print('\n XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \n')
        print(response.request.headers)
        print('\n XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \n')
        yield {
            'cookie_resp': str(response.headers.getlist('Set-Cookie')),
            'cookie_req': str(response.request.headers),
        }
        yield response.follow(url, method = 'POST', body = '{}', callback = self.parse_sport, meta=dict(
			    	playwright = True,
			    	playwright_include_page = True,
			    )) # response.follow
        # url = 'https://www.tipsport.cz/'
        # yield response.follow(url, callback = self.parse_sport)
    
    def parse_sport(self, response):
        yield {
            'url': response.url,
            'text': response.text,
        }