import scrapy
import json
from unidecode import unidecode
from datetime import datetime
import re

from betscraper.items import BasicSportEventItem


class SpiderMerkurSpider(scrapy.Spider):
    name = "spider_merkur"
    allowed_domains = ["www.merkurxtip.cz", 'sb.merkurxtip.cz']
    start_urls = ["https://sb.merkurxtip.cz/restapi/translate/cs/sports"] # https://www.merkurxtip.cz/sazeni

    custom_settings = {
        'FEEDS': {'data/data_merkur.json': {'format': 'json', 'overwrite': True}},
        'CONCURRENT_REQUESTS': 32, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32, # default 8
        'DOWNLOADER_MIDDLEWARES': {
            'betscraper.middlewares.ScrapeOpsFakeUserAgentMiddleware': 400,
            'betscraper.middlewares.ScrapeOpsFakeBrowserHeaderAgentMiddleware': 300,
            'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550, 
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None, 
        },
        'ITEM_PIPELINES': {
            "betscraper.pipelines.UnifySportNamesPipeline": 400,
            "betscraper.pipelines.UpdateNonDrawBetsPipeline": 500,
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
                primary_category_original = match['leagueGroupToken'].split('#')[1]
                secondary_category_original = match['leagueName']
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
                participants_gender = ''
                if 'Women' in secondary_category_original:
                    participants_gender = 'zeny'
                participants_age = ''
                participant_1_hasAge = re.search(r'U\d{2}', participant_1)
                participant_2_hasAge = re.search(r'U\d{2}', participant_2)
                if participant_1_hasAge and participant_2_hasAge and (participant_1_hasAge.group(0) == participant_2_hasAge.group(0)):
                    participants_age = participant_1_hasAge.group(0)
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
                if keepMatch and (participant_2 != 'Vítěz'):
                    basic_sport_event_item = BasicSportEventItem()
                    basic_sport_event_item['bookmaker_id'] = 'ME'
                    basic_sport_event_item['bookmaker_name'] = 'merkur'
                    basic_sport_event_item['sport_name'] = ''
                    basic_sport_event_item['sport_name_original'] = sport
                    basic_sport_event_item['primary_category_original'] = primary_category_original
                    basic_sport_event_item['secondary_category_original'] = secondary_category_original
                    basic_sport_event_item['event_startTime'] = event_startTime
                    basic_sport_event_item['participant_home'] = participant_1
                    basic_sport_event_item['participant_away'] = participant_2
                    basic_sport_event_item['participants_gender'] = participants_gender
                    basic_sport_event_item['participants_age'] = participants_age
                    basic_sport_event_item['bet_1'] = bet_1
                    basic_sport_event_item['bet_0'] = bet_0
                    basic_sport_event_item['bet_2'] = bet_2
                    basic_sport_event_item['bet_10'] = bet_10
                    basic_sport_event_item['bet_02'] = bet_02
                    basic_sport_event_item['bet_12'] = bet_12
                    basic_sport_event_item['bet_11'] = bet_11
                    basic_sport_event_item['bet_22'] = bet_22
                    basic_sport_event_item['event_url'] = event_url
                    yield basic_sport_event_item