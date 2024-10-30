import scrapy
import json
import base64
from protofiles.synottip import protofile_categories_pb2, protofile_sport_double_category_pb2, protofile_sport_single_category_pb2
from google.protobuf.json_format import MessageToJson
import datetime
import re

from betscraper.items import BasicSportEventItem


class SpiderSynottipSpider(scrapy.Spider):
    name = "spider_synottip"
    allowed_domains = ["sport.synottip.cz"]
    # start_urls = ["https://sport.synottip.cz/"]

    custom_settings = {
        'FEEDS': {'data/data_synottip.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'CONCURRENT_REQUESTS': 32, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32, # default 8
        'ITEM_PIPELINES': {
            "betscraper.pipelines.UnifySportNamesPipeline": 400,
            "betscraper.pipelines.UnifyCountryNamesPipeline": 410,
            "betscraper.pipelines.UnifySportDetailsPipeline": 420,
            "betscraper.pipelines.UpdateNonDrawBetsPipeline": 500,
        },
        }
    
    def start_requests(self):
        url = "https://sport.synottip.cz/WebServices/Api/SportsBettingService.svc/GetWebStandardCategories"
        payload = json.dumps({
            "LanguageID": 12,
            "Token": "47556bba7e2ecae0a31c38d6e017bcbb",
        })
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
        }
        yield scrapy.Request(url, method = 'POST', body = payload, headers = headers, callback = self.parse)

    def parse(self, response):
        response_json = json.loads(response.text)
        decoded_bytes = base64.b64decode(response_json['ReturnValue'])
        message = protofile_categories_pb2.Root()
        message.ParseFromString(decoded_bytes)
        message_json = json.loads(MessageToJson(message))
        url = "https://sport.synottip.cz/WebServices/Api/SportsBettingService.svc/GetWebStandardEvents"
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
        }
        for category in message_json['data']['categories']:
            payload = json.dumps({
                "LanguageID": 12,
                "Token": "47556bba7e2ecae0a31c38d6e017bcbb",
                "CategoryID": category['category']['id'],
                "Top": 9999
            })
            yield response.follow(url, method = 'POST', body = payload, headers = headers, callback = self.parse_sport)

    def parse_sport(self, response):
        response_json = json.loads(response.text)
        decoded_bytes = base64.b64decode(response_json['ReturnValue'])
        try: # this "try" is due to categories call also contains some special items without categories
            try:
                message = protofile_sport_double_category_pb2.SportRoot_d()
                message.ParseFromString(decoded_bytes)
                message_json = json.loads(MessageToJson(message))
                sport = message_json['data']['dataSport']['sport']['sportName']
                sport_id = message_json['data']['dataSport']['sport']['sportId']
                for category in message_json['data']['dataSport']['category']:
                    primary_category_original = category['categoryInfo']['categoryName']
                    primary_category = primary_category_original.replace(' amatéři', '').replace(' klubové', '').replace(' mládežnické', '')
                    for category_event in category['categoryEvents']:
                        secondary_category_original = category_event['eventsInfo']['eventsCategory']
                        secondary_category = secondary_category_original.replace(' 2', '').split(', ')[0].split(' (')[0].strip()
                        for event in category_event['eventsInfo']['events']:
                            yield self.prepare_event_item(sport, sport_id, primary_category, secondary_category, primary_category_original, secondary_category_original, event)
            except:
                message = protofile_sport_single_category_pb2.SportRoot_s() # seems that single category protofile is only for esports
                message.ParseFromString(decoded_bytes)
                message_json = json.loads(MessageToJson(message))
                sport = message_json['data']['dataSport']['sport']['sportName']
                sport_id = message_json['data']['dataSport']['sport']['sportId']
                for category in message_json['data']['dataSport']['category']:
                    secondary_category_original = category['eventsInfo']['eventsCategory']
                    primary_category_original = secondary_category_original
                    primary_category = primary_category_original.replace(' amatéři', '').replace(' klubové', '').replace(' mládežnické', '')
                    secondary_category = secondary_category_original.replace(' 2', '').split(', ')[0].split(' (')[0].strip()
                    for event in category['eventsInfo']['events']:
                        yield self.prepare_event_item(sport, sport_id, primary_category, secondary_category, primary_category_original, secondary_category_original, event)
        except:
            pass

    def prepare_event_item(self, sport, sport_id, primary_category, secondary_category, primary_category_original, secondary_category_original, event):
        if event['betDetails']['bet']['betsName'] in ['Zápas', 'Vítěz zápasu', 'Vítěz (včetně extra směn)', 'Vítěz (včetně prodloužení)', 'Vítěz (včetně super over)']:
            event_id = event['eventId']
            event_xx = event['eventXx']
            bet_id = event['betDetails']['bet']['betsInfo']['betId']
            event_url = f"https://sport.synottip.cz/zapasy/{sport_id}/{event_id}c{event_xx}/{bet_id}?categoryId={sport_id}"
            event_startTime = datetime.datetime.fromtimestamp(int(event['eventTime']['datetime'])/1000)
            participants = event['eventName'].split(' - ')
            participant_1 = participants[0]
            participant_2 = participants[1]
            participants_gender = ''
            if any('ženy' in string for string in [primary_category_original, secondary_category_original]):
                participants_gender = 'zeny'
            # elif any('muži' in string for string in [primary_category_original, secondary_category_original]):
            #     participants_gender = 'muzi'
            participants_age = ''
            participant_1_hasAge = re.search(r'U\d{2}', participant_1)
            participant_2_hasAge = re.search(r'U\d{2}', participant_2)
            if participant_1_hasAge and participant_2_hasAge and (participant_1_hasAge.group(0) == participant_2_hasAge.group(0)):
                participants_age = participant_1_hasAge.group(0)
            bet_1 = bet_0 = bet_2 = bet_10 = bet_02 = bet_12 = bet_11 = bet_22 = -1
            for odd in event['betDetails']['bet']['betsInfo']['odds']:
                if odd['oddName'] == '1':
                    bet_1 = odd['oddNumber']
                elif odd['oddName'] == '0':
                    bet_0 = odd['oddNumber']
                elif odd['oddName'] == '2':
                    bet_2 = odd['oddNumber']
            # muze se hodit v budoucnu
            # secondary_category = ' '.join([word for word in secondary_category.split() if not re.search(r'\d', word)])
            sport_detail_original = primary_category
            basic_sport_event_item = BasicSportEventItem()
            basic_sport_event_item['bookmaker_id'] = 'ST'
            basic_sport_event_item['bookmaker_name'] = 'synottip'
            basic_sport_event_item['sport_name'] = ''
            basic_sport_event_item['sport_name_original'] = sport
            basic_sport_event_item['sport_detail'] = ''
            basic_sport_event_item['sport_detail_original'] = sport_detail_original
            basic_sport_event_item['country_name'] = ''
            basic_sport_event_item['country_name_original'] = ''
            basic_sport_event_item['primary_category'] = primary_category
            basic_sport_event_item['primary_category_original'] = primary_category_original
            basic_sport_event_item['secondary_category'] = secondary_category
            basic_sport_event_item['secondary_category_original'] = secondary_category_original
            basic_sport_event_item['event_startTime'] = event_startTime
            basic_sport_event_item['participant_home'] = participant_1
            basic_sport_event_item['participant_away'] = participant_2
            basic_sport_event_item['participant_home_list'] = ()
            basic_sport_event_item['participant_away_list'] = ()
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
            return basic_sport_event_item