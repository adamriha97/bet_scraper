import scrapy
import json
from unidecode import unidecode
from datetime import datetime


class SpiderMerkurSpider(scrapy.Spider):
    name = "spider_merkur"
    allowed_domains = ["www.merkurxtip.cz", 'sb.merkurxtip.cz']
    start_urls = ["https://sb.merkurxtip.cz/restapi/translate/cs/sports"] # https://www.merkurxtip.cz/sazeni

    custom_settings = {
        'FEEDS': {'data/data_merkur.json': {'format': 'json', 'overwrite': True}},
        'CONCURRENT_REQUESTS': 32, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32, # default 8
        'DOWNLOAD_DELAY': 0,
        'DOWNLOADER_MIDDLEWARES': {
            'betscraper.middlewares.ScrapeOpsFakeUserAgentMiddleware': 400,
            'betscraper.middlewares.ScrapeOpsFakeBrowserHeaderAgentMiddleware': 300,
            'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550, 
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None, 
        },
        }

    def parse(self, response):
        response_json = json.loads(response.text)
        sport_dict = {item['sportTypeCode']: str(item['name']).strip() for item in response_json}
        for key, value in sport_dict.items():
            yield response.follow(f'https://sb.merkurxtip.cz/restapi/offer/cs/sport/{key}/mob', callback = self.parse_sport, cb_kwargs=dict(sport_name=value))

    def parse_sport(self, response, sport_name):
        response_json = json.loads(response.text)
        for match in response_json['esMatches']:
            if match['away'] != 'vítěz':
                sport = sport_name
                try:
                    sportToken = unidecode(sport_name.lower().replace(' ', '-').replace('.', ''))
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
                bet_1 = bet_0 = bet_2 = bet_10 = bet_02 = bet_12 = bet_11 = bet_22 = -1
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
                # to solve problem with basketball
                if bet_1 == bet_0 == bet_2 == -1:
                    try:
                        bet_1 = match["betMap"]["50291"]["NULL"]["ov"]
                        keepMatch = True
                    except:
                        pass
                    try:
                        bet_2 = match["betMap"]["50293"]["NULL"]["ov"]
                        keepMatch = True
                    except:
                        pass
                # not a perfect solution because bet_0 can be locked or not available on the site but still relevant option
                if (bet_0 == -1) and (not (bet_1 == bet_2 == -1)):
                    bet_11 = bet_1
                    bet_1 = -1
                    bet_22 = bet_2
                    bet_2 = -1
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
                        'bet_10': bet_10,
                        'bet_02': bet_02,
                        'bet_12': bet_12,
                        'bet_11': bet_11,
                        'bet_22': bet_22,
                    }