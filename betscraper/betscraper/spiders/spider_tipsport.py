import scrapy
from scrapy_playwright.page import PageMethod
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


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
    # start_urls = ["https://www.tipsport.cz/"]

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
            "headless": True, # True False
            "timeout": 600 * 1000,  # 60 seconds
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 600 * 1000,  # 60 seconds
        'PLAYWRIGHT_ABORT_REQUEST': should_abort_request,
        'PLAYWRIGHT_MAX_PAGES_PER_CONTEXT': 1,
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
			    ), callback = self.parse)

    async def parse(self, response):
        root = ET.fromstring(response.text.split('<div id=\"webkit-xml-viewer-source-xml\">')[1].split('</div>')[0])
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [url.find('ns:loc', namespaces).text for url in root.findall('ns:url', namespaces)]
        not_interested = ['cyklistika', 'motorsport', 'spolecenske-sazky']
        for url in urls:
            if len(url.split('/')) == 5 and url.split('/')[-1].rsplit('-', 1)[0] not in not_interested:
                url_with_limit = url + '?limit=9999'
                yield response.follow(url_with_limit, meta=dict(
                        playwright = True,
                        playwright_include_page = True, 
                        playwright_page_methods =[
                            PageMethod("wait_for_selector", "div.Matchstyled__Row-sc-5rxr4z-1"),
                        ],
                    ), callback = self.parse_sport)
        page = response.meta["playwright_page"]
        await page.close()
    
    async def parse_sport(self, response):
        date_format = "%d. %m. %Y | %H:%M"
        sport = response.url.split('/')[-1].rsplit('-', 1)[0]
        rows = response.css('div.Matchstyled__Row-sc-5rxr4z-1')
        for row in rows:
            if row.css('div.OppRowsstyled__Row-sc-5sm0bz-0 ::attr(class)').get().split(' ')[1] == 'iukKnA':
                event_url = row.css('a.hide ::attr(href)').get()
                date_string = row.css('span.Matchstyled__Info-sc-5rxr4z-8 ::text').get()
                if "Dnes" in date_string:
                    date_part = datetime.today().strftime("%d. %m. %Y")
                elif "Zítra" in date_string:
                    date_part = (datetime.today() + timedelta(days=1)).strftime("%d. %m. %Y")
                else:
                    date_part = date_string.split(' | ')[0]
                time_part = date_string.split(' | ')[1]
                combined_string = f"{date_part} | {time_part}"
                event_startTime = datetime.strptime(combined_string, date_format)
                participants = row.css('div.Matchstyled__Name-sc-5rxr4z-6 span ::text').get().split(' - ')
                participant_1 = participants[0]
                participant_2 = participants[1]
                bet_1 = bet_10 = bet_0 = bet_02 = bet_2 = -1
                bets = row.css('div.eQOciy')
                for bet in bets:
                    bet_version = bet.css('::attr(data-atid)').get().split('||')[-1]
                    if bet_version =='1':
                        bet_1 = bet.css('span ::text').get()
                    elif bet_version =='1x':
                        bet_10 = bet.css('span ::text').get()
                    elif bet_version =='x':
                        bet_0 = bet.css('span ::text').get()
                    elif bet_version =='x2':
                        bet_02 = bet.css('span ::text').get()
                    elif bet_version =='2':
                        bet_2 = bet.css('span ::text').get()
                yield {
                    'sport': sport,
                    'event_url': event_url,
                    'event_startTime': event_startTime,
                    'participant_1': participant_1,
                    'participant_2': participant_2,
                    'bet_1': bet_1,
                    'bet_10': bet_10,
                    'bet_0': bet_0,
                    'bet_02': bet_02,
                    'bet_2': bet_2,
                }
        page = response.meta["playwright_page"]
        await page.close()