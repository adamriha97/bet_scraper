import scrapy
import json


class SpiderKingsbetSpider(scrapy.Spider):
    name = "spider_kingsbet"
    allowed_domains = ["www.kingsbet.cz", 'sb2frontend-altenar2.biahosted.com']
    start_urls = ["https://sb2frontend-altenar2.biahosted.com/api/widget/GetSportMenu?culture=cs-CZ&timezoneOffset=-120&integration=kingsbet&deviceType=1&numFormat=en-GB&countryCode=CZ&period=0"] # https://www.kingsbet.cz/

    custom_settings = {
        'FEEDS': {'data_kingsbet.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0"
        }

    def parse(self, response):
        response_json = json.loads(response.text)
        for category in response_json['categories']:
            url = f'https://sb2frontend-altenar2.biahosted.com/api/widget/GetEvents?culture=cs-CZ&timezoneOffset=-120&integration=kingsbet&deviceType=1&numFormat=en-GB&countryCode=CZ&eventCount=0&sportId=0&catIds={category["id"]}'
            # yield {
            #     'cat': category['name'],
            #     'url': url
            # }
        yield response.follow(url, callback = self.parse_category)

    def parse_category(self, response):
        response_json = json.loads(response.text)
        yield {
            'sport': response_json['sports'][0]['name']
        }
