import scrapy
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import re

from betscraper.items import BasicSportEventItem


class SpiderSazkaSpider(scrapy.Spider):
    name = "spider_sazka"
    allowed_domains = ["www.sazka.cz", "sg-content-engage-prod.sazka.cz"]
    start_urls = ["https://sg-content-engage-prod.sazka.cz/content-service/api/v1/q/drilldown-tree?drilldownNodeIds=2&eventState=OPEN_EVENT"] # https://www.sazka.cz/kurzove-sazky/

    custom_settings = {
        'FEEDS': {'data/data_sazka.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'CONCURRENT_REQUESTS': 64, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 64, # default 8
        'ITEM_PIPELINES': {
            "betscraper.pipelines.DropDuplicatesPipeline": 350,
            "betscraper.pipelines.UnifySportNamesPipeline": 400,
            "betscraper.pipelines.UpdateNonDrawBetsPipeline": 500,
        },
        }

    def parse(self, response):
        response_json = json.loads(response.text)
        # Soccer je v not_interested, jelikoz pro nej bereme vsechny kategorie zvlast - najednou je to moc zapasu a api GET call vraci error
        not_interested = ['Soccer', 'Sazka Specials', 'Cycling', 'Formula 1', 'Golf', 'Motor Racing', 'Politics', 'Alpine Skiing', 'Biathlon', 'Ski Jumping']
        sports_dict = {node["name"]: node["id"] for node in response_json["data"]["drilldownNodes"][0]["drilldownNodes"] if node["name"] not in not_interested}
        soccer_node = None
        for node in response_json["data"]["drilldownNodes"][0]["drilldownNodes"]:
            if node["name"] == "Soccer":
                soccer_node = node
                break
        soccer_competitions_dict = {}
        if soccer_node:
            soccer_competitions_dict = {node["name"]: node["id"] for node in soccer_node["drilldownNodes"]}
        ids_for_urls_dict = {**sports_dict, **soccer_competitions_dict}
        headers = {
            'x-accept-language': 'cs-CZ',
        }
        for name, id_value in ids_for_urls_dict.items():
            url = f'https://sg-content-engage-prod.sazka.cz/content-service/api/v1/q/time-band-event-list?maxMarkets=1&marketSortsIncluded=--%2CCS%2CDC%2CDN%2CHH%2CHL%2CMH%2CMR%2CWH&marketGroupTypesIncluded=CUSTOM_GROUP%2CMONEYLINE%2CROLLING_SPREAD%2CROLLING_TOTAL%2CSTATIC_SPREAD%2CSTATIC_TOTAL&allowedEventSorts=MTCH&includeChildMarkets=true&prioritisePrimaryMarkets=true&drilldownTagIds={id_value}&maxTotalItems=1000&maxEventsPerCompetition=30&maxCompetitionsPerSportPerBand=1000'
            yield response.follow(url, method = 'GET', headers = headers, callback = self.parse_sport)

    def parse_sport(self, response):
        response_json = json.loads(response.text)
        for time_band in response_json['data']['timeBandEvents']:
            for event in time_band['events']:
                try:
                    sport = event['category']['name']
                    primary_category_original = event['class']['name']
                    secondary_category_original = event['type']['name']
                    country_name = primary_category_original
                    event_url = f'https://www.sazka.cz/kurzove-sazky/sports/event/{event["id"]}'
                    event_startTime = datetime.fromisoformat(event['startTime'].replace("Z", "+00:00")).replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo('Europe/Prague'))
                    participant_1 = event['teams'][0]['name']
                    participant_2 = event['teams'][1]['name']
                    participants_gender = ''
                    if 'ženy' in secondary_category_original:
                        participants_gender = 'zeny'
                    elif 'muži' in secondary_category_original:
                        participants_gender = 'muzi'
                    participants_age = ''
                    hasAge = re.search(r'U\d{2}', secondary_category_original)
                    if hasAge:
                        participants_age = hasAge.group(0)
                    bet_1 = bet_0 = bet_2 = bet_10 = bet_02 = bet_12 = bet_11 = bet_22 = -1
                    for bet in event['markets'][0]['outcomes']:
                        if bet["name"] == participant_1:
                            bet_1 = bet['prices'][0]['decimal']
                        elif bet["name"] == participant_2:
                            bet_2 = bet['prices'][0]['decimal']
                        elif bet["name"] == 'Remíza': # in en version: Draw
                            bet_0 = bet['prices'][0]['decimal']
                    basic_sport_event_item = BasicSportEventItem()
                    basic_sport_event_item['bookmaker_id'] = 'SA'
                    basic_sport_event_item['bookmaker_name'] = 'sazka'
                    basic_sport_event_item['sport_name'] = ''
                    basic_sport_event_item['sport_name_original'] = sport
                    basic_sport_event_item['country_name'] = country_name
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
                except:
                    continue