import scrapy
import json
import datetime
import re

from betscraper.items import BasicSportEventItem


class SpiderBetanoSpider(scrapy.Spider):
    name = "spider_betano"
    allowed_domains = ["www.betano.cz"]
    start_urls = ["https://www.betano.cz/api/"] # https://www.betano.cz

    custom_settings = {
        'FEEDS': {'data/data_betano.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'CONCURRENT_REQUESTS': 32, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32, # default 8
        'ITEM_PIPELINES': {
            "betscraper.pipelines.UnifySportNamesPipeline": 400,
            "betscraper.pipelines.UnifyCountryNamesPipeline": 410,
            "betscraper.pipelines.UpdateNonDrawBetsPipeline": 500,
        },
        }
    
    def parse(self, response):
        response_json = json.loads(response.text)
        not_interested = ['formule-1', 'zimni-sporty', 'zabava', 'cyklistika', 'golf', 'motorsport', 'surfing', 'speedway', 'politika']
        for sport in response_json["structureComponents"]["sports"]["data"]:
            if sport["url"].split('/')[2] not in not_interested:
                url = 'https://www.betano.cz/api' + sport["url"] + 'nadchazejici-zapasy-dnes/?sort=Leagues&req=la,s,stnf,c,mb'
                yield response.follow(url, callback = self.parse_sport)

    def parse_sport(self, response):
        response_json = json.loads(response.text)
        try:
            if response_json["errorCode"] == 301:
                pass
        except:
            sport = response.url.split('/')[5]
            for league in response_json["data"]["blocks"]:
                for event in league["events"]:
                    primary_category_original = event["regionName"]
                    secondary_category_original = event["leagueName"]
                    event_url = f'https://www.betano.cz{event["url"]}'
                    event_startTime = datetime.datetime.fromtimestamp(event["startTime"]/1000)
                    participant_1 = event["participants"][0]["name"]
                    participant_2 = event["participants"][1]["name"]
                    participants_gender = ''
                    if '(Ž)' in secondary_category_original:
                        participants_gender = 'zeny'
                    # elif 'muži' in primary_category_original:
                    #     participants_gender = 'muzi'
                    participants_age = ''
                    hasAge = re.search(r'U\d{2}', secondary_category_original)
                    if hasAge:
                        participants_age = hasAge.group(0)
                    # pridavam alternativu, jelikoz nektere bety se nedotahovali z duvodu odlisnosti nazvu participantu (smiseny tenis mel prohozene jmena hracu)
                    participants_alternative = event['name'].split(' - ')
                    participant_1_alternative = participants_alternative[0]
                    participant_2_alternative = participants_alternative[1]
                    bet_1 = bet_0 = bet_2 = bet_10 = bet_02 = bet_12 = bet_11 = bet_22 = -1
                    for market in event['markets']:
                        if market["name"].startswith(("Výsledek", "Vítěz")):
                            for selection in market["selections"]:
                                if selection["name"] in ['0', 'Remíza']:
                                    bet_0 = selection["price"]
                                elif selection["name"] in ['1', participant_1, participant_1_alternative]:
                                    bet_1 = selection["price"]
                                elif selection["name"] in ['2', participant_2, participant_2_alternative]:
                                    bet_2 = selection["price"]
                    primary_category = primary_category_original
                    secondary_category = secondary_category_original.replace(' (Ž)', '').replace(' Masters', '').replace(' 2', '').split(' - ')[0].split(',')[0]
                    if not (bet_1 == bet_0 == bet_2 == bet_10 == bet_02 == bet_12 == bet_11 == bet_22 == -1):
                        basic_sport_event_item = BasicSportEventItem()
                        basic_sport_event_item['bookmaker_id'] = 'BE'
                        basic_sport_event_item['bookmaker_name'] = 'betano'
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