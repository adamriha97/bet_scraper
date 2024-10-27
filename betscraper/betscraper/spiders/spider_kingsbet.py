import scrapy
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import re

from betscraper.items import BasicSportEventItem


class SpiderKingsbetSpider(scrapy.Spider):
    name = "spider_kingsbet"
    allowed_domains = ["www.kingsbet.cz", 'sb2frontend-altenar2.biahosted.com']
    start_urls = ["https://sb2frontend-altenar2.biahosted.com/api/widget/GetSportMenu?culture=cs-CZ&timezoneOffset=-120&integration=kingsbet&deviceType=1&numFormat=en-GB&countryCode=CZ&period=0"] # https://www.kingsbet.cz/

    custom_settings = {
        'FEEDS': {'data/data_kingsbet.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'CONCURRENT_REQUESTS': 32, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32, # default 8
        'ITEM_PIPELINES': {
            "betscraper.pipelines.UnifySportNamesPipeline": 400,
            "betscraper.pipelines.UnifyCountryNamesPipeline": 410,
        },
        }

    def parse(self, response):
        response_json = json.loads(response.text)
        for sport in response_json['sports']:
            join_category_id_list = '%2C'.join([str(i) for i in sport["catIds"]])
            url = f'https://sb2frontend-altenar2.biahosted.com/api/widget/GetEvents?culture=cs-CZ&timezoneOffset=-120&integration=kingsbet&deviceType=1&numFormat=en-GB&countryCode=CZ&eventCount=0&sportId=0&catIds={join_category_id_list}'
            yield response.follow(url, callback = self.parse_sport)

    def parse_sport(self, response):
        response_json = json.loads(response.text)
        sports_dict = self.create_dict_from_list(response_json['sports'])
        categories_dict = self.create_dict_from_list(response_json['categories'])
        champs_dict = self.create_dict_from_list(response_json['champs'])
        competitors_dict = self.create_dict_from_list(response_json['competitors'])
        markets_dict = {}
        for market_item in response_json['markets']:
            markets_dict[str(market_item['id'])] = {'name': market_item['name'], 'oddIds': market_item['oddIds']}
        odds_dict = {}
        for odd_item in response_json['odds']:
            odds_dict[str(odd_item['id'])] = odd_item['price']
        for event in response_json['events']:
            sport = sports_dict[str(event['sportId'])]
            primary_category_original = categories_dict[str(event['catId'])]
            secondary_category_original = champs_dict[str(event['champId'])]
            # event_url = f'https://www.kingsbet.cz/sport#/sport/{event["sportId"]}/category/{event["catId"]}/championship/{event["champId"]}/event/{event["id"]}'
            event_url = f"https://www.kingsbet.cz/sport?page=event&eventId={event['id']}"
            event_startTime = datetime.fromisoformat(event['startDate'].replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Prague"))
            participant_1 = competitors_dict[str(event['competitorIds'][0])]
            participant_2 = competitors_dict[str(event['competitorIds'][1])]
            participants_gender = ''
            if any('ženy' in string for string in [primary_category_original, secondary_category_original]):
                participants_gender = 'zeny'
            elif any('muži' in string for string in [primary_category_original, secondary_category_original]):
                participants_gender = 'muzi'
            participants_age = ''
            participant_1_hasAge = re.search(r'U\d{2}', participant_1)
            participant_2_hasAge = re.search(r'U\d{2}', participant_2)
            if participant_1_hasAge and participant_2_hasAge and (participant_1_hasAge.group(0) == participant_2_hasAge.group(0)):
                participants_age = participant_1_hasAge.group(0)
            bet_1 = bet_0 = bet_2 = bet_10 = bet_02 = bet_12 = bet_11 = bet_22 = -1
            for market_id in event['marketIds']:
                if markets_dict[str(market_id)]['name'] == 'Výsledek zápasu':
                    bet_1 = odds_dict[str(markets_dict[str(market_id)]['oddIds'][0])]
                    bet_0 = odds_dict[str(markets_dict[str(market_id)]['oddIds'][1])]
                    bet_2 = odds_dict[str(markets_dict[str(market_id)]['oddIds'][2])]
                if markets_dict[str(market_id)]['name'] in ('Výsledek zápasu – dvojtip', 'Dvojtip'):
                    bet_10 = odds_dict[str(markets_dict[str(market_id)]['oddIds'][0])]
                    bet_12 = odds_dict[str(markets_dict[str(market_id)]['oddIds'][1])]
                    bet_02 = odds_dict[str(markets_dict[str(market_id)]['oddIds'][2])]
                if markets_dict[str(market_id)]['name'] in ('Vítěz', 'Vítěz zápasu', 'Vítěz (vč. prodl.)', 'Vítěz  (vč. extra směny)', 'Vítěz (včetně prodloužení a nájezdů)', 'Výsledek zápasu bez remízy'):
                    bet_11 = odds_dict[str(markets_dict[str(market_id)]['oddIds'][0])]
                    bet_22 = odds_dict[str(markets_dict[str(market_id)]['oddIds'][1])]
            primary_category = primary_category_original
            secondary_category = secondary_category_original.split(', ')[0].replace('ATP ', '').replace('WTA ', '').replace('ITF ', '').replace('Challenger ', '')
            secondary_category = ' '.join([word for word in secondary_category.split() if not re.search(r'\d', word)])
            if not (bet_1 == bet_0 == bet_2 == bet_10 == bet_02 == bet_12 == bet_11 == bet_22 == -1):
                basic_sport_event_item = BasicSportEventItem()
                basic_sport_event_item['bookmaker_id'] = 'KB'
                basic_sport_event_item['bookmaker_name'] = 'kingsbet'
                basic_sport_event_item['sport_name'] = ''
                basic_sport_event_item['sport_name_original'] = sport
                basic_sport_event_item['country_name'] = ''
                basic_sport_event_item['country_name_original'] = ''
                basic_sport_event_item['primary_category'] = primary_category
                basic_sport_event_item['primary_category_original'] = primary_category_original
                basic_sport_event_item['secondary_category'] = secondary_category
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

    def create_dict_from_list(self, list):
        dict = {}
        for item in list:
            dict[str(item['id'])] = item['name']
        return dict
