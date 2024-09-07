import scrapy
import json


class SpiderForbetSpider(scrapy.Spider):
    name = "spider_forbet"
    allowed_domains = ["www.iforbet.cz"]
    # start_urls = ["https://www.iforbet.cz"]

    custom_settings = {
        'FEEDS': {'data_forbet.json': {'format': 'json', 'overwrite': True}},
        # 'DOWNLOADER_MIDDLEWARES': {
        #     'betscraper.middlewares.ScrapeOpsFakeUserAgentMiddleware': 400,
        #     'betscraper.middlewares.ScrapeOpsFakeBrowserHeaderAgentMiddleware': 300,
        #     'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550, 
        #     'scrapy.downloadermiddlewares.retry.RetryMiddleware': None, 
        # },
        }
    
    def start_requests(self):
        url = 'https://www.iforbet.cz/api/web/v1/offer/full_offer'
        body = json.dumps({
            "offerMode": "prematch",
            "lang": "cs"
        })
        headers = {
            'Content-Type': 'application/json'
        }
        yield scrapy.Request(url=url, headers=headers, body=body, method="POST", callback = self.parse)

    def parse(self, response):
        response_json = json.loads(response.text)
        first_market_ids = set()
        for sport_market_list in response_json['data']['market_list'].values():
            first_market_id = next(iter(sport_market_list))
            first_market_ids.add(first_market_id)
        yield {
            'json': first_market_ids
        }
