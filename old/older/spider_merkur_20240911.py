import scrapy
import json
from unidecode import unidecode
from datetime import datetime


class SpiderMerkurSpider(scrapy.Spider):
    name = "spider_merkur"
    allowed_domains = ["www.merkurxtip.cz"]
    start_urls = ["https://sb.merkurxtip.cz/restapi/offer/cs/last_minute/mob"] # https://www.merkurxtip.cz/sazeni https://sb.merkurxtip.cz/restapi/translate/cs/sports

    custom_settings = {
        'FEEDS': {'data_merkur.json': {'format': 'json', 'overwrite': True}},
        'DOWNLOADER_MIDDLEWARES': {
            'betscraper.middlewares.ScrapeOpsFakeUserAgentMiddleware': 400,
            'betscraper.middlewares.ScrapeOpsFakeBrowserHeaderAgentMiddleware': 300,
            'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550, 
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None, 
        },
        }

    def parse(self, response):
        response_json = json.loads(response.text)
        # sport_dict = {item['sportTypeCode']: item['name'] for item in response_json}
        # for key, value in sport_dict.items():
        #     yield {
        #         'key': key,
        #         'value': value,
        #     }
        for match in response_json['esMatches']:
            if match['away'] != 'vítěz':
                sport = match['sportToken'].split('#')[-1].strip()
                try:
                    sportToken = unidecode(match["sportToken"].split("#")[-1].strip().lower().replace(' ', '-').replace('.', ''))
                    leagueName = unidecode(match["leagueName"].lower().replace(" ", "-"))
                    leagueToken = match['leagueToken'].split("#")[-2].strip()
                    home = unidecode(match["home"].lower().replace(" ", "-"))
                    away = unidecode(match["away"].lower().replace(" ", "-"))
                    event_url = f'https://www.merkurxtip.cz/sazeni/online/{sportToken}/{match["sport"]}/{leagueName}/{leagueToken}/special/{home}-v-{away}/{str(match["id"])}'
                except:
                    event_url = 'N/A'
                event_startTime = datetime.fromtimestamp(match['kickOffTime'] / 1000)
                participant_1 = match['home']
                participant_2 = match['away']
                bet_1 = bet_0 = bet_2 = -1
                keepMatch = False
                try:
                    bet_1 = match["betMap"]["1"]["NULL"]["ov"]
                    keepMatch = True
                except:
                    pass
                try:
                    bet_0 = match["betMap"]["2"]["NULL"]["ov"]
                    keepMatch = True
                except:
                    pass
                try:
                    bet_2 = match["betMap"]["3"]["NULL"]["ov"]
                    keepMatch = True
                except:
                    pass
                if keepMatch:
                    yield {
                        'sport': sport,
                        'event_url': event_url,
                        'event_startTime': event_startTime,
                        'participant_1': participant_1,
                        'participant_2': participant_2,
                        'bet_1': bet_1,
                        'bet_0': bet_0,
                        'bet_2': bet_2,
                    }