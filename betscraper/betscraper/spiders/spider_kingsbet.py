import scrapy
import json
from datetime import datetime
from zoneinfo import ZoneInfo


class SpiderKingsbetSpider(scrapy.Spider):
    name = "spider_kingsbet"
    allowed_domains = ["www.kingsbet.cz", 'sb2frontend-altenar2.biahosted.com']
    start_urls = ["https://sb2frontend-altenar2.biahosted.com/api/widget/GetSportMenu?culture=cs-CZ&timezoneOffset=-120&integration=kingsbet&deviceType=1&numFormat=en-GB&countryCode=CZ&period=0"] # https://www.kingsbet.cz/

    custom_settings = {
        'FEEDS': {'data_kingsbet.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'CONCURRENT_REQUESTS': 64, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 64, # default 8
        }

    def parse(self, response):
        response_json = json.loads(response.text)
        for sport in response_json['sports']:
            join_category_id_list = '%2C'.join([str(i) for i in sport["catIds"]])
            url = f'https://sb2frontend-altenar2.biahosted.com/api/widget/GetEvents?culture=cs-CZ&timezoneOffset=-120&integration=kingsbet&deviceType=1&numFormat=en-GB&countryCode=CZ&eventCount=0&sportId=0&catIds={join_category_id_list}'
            yield response.follow(url, callback = self.parse_sport)

    def parse_sport(self, response):
        response_json = json.loads(response.text)
        sports_dict = {}
        for sport_item in response_json['sports']:
            sports_dict[str(sport_item['id'])] = sport_item['name']
        competitors_dict = {}
        for competitor_item in response_json['competitors']:
            competitors_dict[str(competitor_item['id'])] = competitor_item['name']
        markets_dict = {}
        for market_item in response_json['markets']:
            markets_dict[str(market_item['id'])] = {'name': market_item['name'], 'oddIds': market_item['oddIds']}
        odds_dict = {}
        for odd_item in response_json['odds']:
            odds_dict[str(odd_item['id'])] = odd_item['price']
        for event in response_json['events']:
            sport = sports_dict[str(event['sportId'])]
            event_url = f'https://www.kingsbet.cz/sport#/sport/{event["sportId"]}/category/{event["catId"]}/championship/{event["champId"]}/event/{event["id"]}'
            event_startTime = datetime.fromisoformat(event['startDate'].replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Prague"))
            participant_1 = competitors_dict[str(event['competitorIds'][0])]
            participant_2 = competitors_dict[str(event['competitorIds'][1])]
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
            if not (bet_1 == bet_0 == bet_2 == bet_10 == bet_02 == bet_12 == bet_11 == bet_22 == -1):
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
