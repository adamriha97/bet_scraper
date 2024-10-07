import scrapy
import json
import base64
from protofiles.synottip import protofile_categories_pb2, protofile_sport_double_category_pb2, protofile_sport_single_category_pb2
from google.protobuf.json_format import MessageToJson
import datetime

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
        # 'ITEM_PIPELINES': {
        #     "betscraper.pipelines.UnifySportNamesPipeline": 400,
        # },
        'DOWNLOAD_DELAY': 3,
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
        # for category in message_json['data']['categories']:
        #     payload = json.dumps({
        #         "LanguageID": 12,
        #         "Token": "47556bba7e2ecae0a31c38d6e017bcbb",
        #         "CategoryID": category['category']['id'],
        #         "Top": 9999
        #     })
        #     yield response.follow(url, method = 'POST', body = payload, headers = headers, callback = self.parse_sport)

        payload = json.dumps({
            "LanguageID": 12,
            "Token": "47556bba7e2ecae0a31c38d6e017bcbb",
            "CategoryID": "87",
            "Top": 9999
        })
        yield response.follow(url, method = 'POST', body = payload, headers = headers, callback = self.parse_sport)

    def parse_sport(self, response):
        response_json = json.loads(response.text)
        decoded_bytes = base64.b64decode(response_json['ReturnValue'])
        try:
            message = protofile_sport_double_category_pb2.SportRoot_d()
            message.ParseFromString(decoded_bytes)
            message_json = json.loads(MessageToJson(message))

            # print('***************************************************************************')
            # # print(message_json)
            # yield {
            #     'json': message_json
            # }
            # print('***************************************************************************')

            sport = message_json['data']['dataSport']['sport']['sportName']
            sport_id = message_json['data']['dataSport']['sport']['sportId']
            for category in message_json['data']['dataSport']['category']:
                for category_event in category['categoryEvents']:
                    for event in category_event['eventsInfo']['events']:
                        if event['betDetails']['bet']['betsName'] in ['Zápas', 'Vítěz zápasu', 'Vítěz (včetně extra směn)']:
                            yield self.prepare_event_item(sport, sport_id, event)
        except:
            message = protofile_sport_single_category_pb2.SportRoot_s()
            message.ParseFromString(decoded_bytes)
            message_json = json.loads(MessageToJson(message))
            sport = message_json['data']['dataSport']['sport']['sportName']
            sport_id = message_json['data']['dataSport']['sport']['sportId']
            for category in message_json['data']['dataSport']['category']:
                for event in category['eventsInfo']['events']:
                    if event['betDetails']['bet']['betsName'] in ['Zápas', 'Vítěz zápasu']:
                        yield self.prepare_event_item(sport, sport_id, event)
        
        ############################################################################################################################

        # sport = message_json['data']['dataSport']['sport']['sportName']
        # sport_id = message_json['data']['dataSport']['sport']['sportId']

        # print('***************************************************************************')
        # print(response_json['ReturnValue'])
        # print('***************************************************************************')
        # print('')
        # print('***************************************************************************')

        # for event in message_json['data']['dataSport']['category']['categoryEvents']['eventsInfo']['events']:
        #     if event['betDetails']['bet']['betsName'] in ['Zápas', 'Vítěz zápasu']:
        #         event_id = event['eventId']
        #         event_xx = event['eventXx']
        #         bet_id = event['betDetails']['bet']['betsInfo']['betId']
        #         event_url = f"https://sport.synottip.cz/zapasy/{sport_id}/{event_id}c{event_xx}/{bet_id}?categoryId={sport_id}"
        #         event_startTime = datetime.datetime.fromtimestamp(int(event['eventTime']['datetime'])/1000)
        #         participants = event['eventName'].split(' - ')
        #         participant_1 = participants[0]
        #         participant_2 = participants[1]
        #         bet_1 = bet_0 = bet_2 = bet_10 = bet_02 = bet_12 = bet_11 = bet_22 = -1
        #         for odd in event['betDetails']['bet']['betsInfo']['odds']:
        #             if odd['oddName'] == '1':
        #                 bet_1 = odd['oddNumber']
        #             elif odd['oddName'] == '0':
        #                 bet_0 = odd['oddNumber']
        #             elif odd['oddName'] == '2':
        #                 bet_2 = odd['oddNumber']
        #         # not a perfect solution because bet_0 can be locked or not available on the site but still relevant option
        #         if (bet_0 == -1) and (not (bet_1 == bet_2 == -1)):
        #             bet_11 = bet_1
        #             bet_1 = -1
        #             bet_22 = bet_2
        #             bet_2 = -1
        #         basic_sport_event_item = BasicSportEventItem()
        #         basic_sport_event_item['bookmaker_id'] = 'ST'
        #         basic_sport_event_item['bookmaker_name'] = 'synottip'
        #         basic_sport_event_item['sport_name'] = ''
        #         basic_sport_event_item['sport_name_original'] = sport
        #         basic_sport_event_item['event_url'] = event_url
        #         basic_sport_event_item['event_startTime'] = event_startTime
        #         basic_sport_event_item['participant_home'] = participant_1
        #         basic_sport_event_item['participant_away'] = participant_2
        #         basic_sport_event_item['bet_1'] = bet_1
        #         basic_sport_event_item['bet_0'] = bet_0
        #         basic_sport_event_item['bet_2'] = bet_2
        #         basic_sport_event_item['bet_10'] = bet_10
        #         basic_sport_event_item['bet_02'] = bet_02
        #         basic_sport_event_item['bet_12'] = bet_12
        #         basic_sport_event_item['bet_11'] = bet_11
        #         basic_sport_event_item['bet_22'] = bet_22
        #         yield basic_sport_event_item

    def prepare_event_item(self, sport, sport_id, event):
        event_id = event['eventId']
        event_xx = event['eventXx']
        bet_id = event['betDetails']['bet']['betsInfo']['betId']
        event_url = f"https://sport.synottip.cz/zapasy/{sport_id}/{event_id}c{event_xx}/{bet_id}?categoryId={sport_id}"
        event_startTime = datetime.datetime.fromtimestamp(int(event['eventTime']['datetime'])/1000)
        participants = event['eventName'].split(' - ')
        participant_1 = participants[0]
        participant_2 = participants[1]
        bet_1 = bet_0 = bet_2 = bet_10 = bet_02 = bet_12 = bet_11 = bet_22 = -1
        for odd in event['betDetails']['bet']['betsInfo']['odds']:
            if odd['oddName'] == '1':
                bet_1 = odd['oddNumber']
            elif odd['oddName'] == '0':
                bet_0 = odd['oddNumber']
            elif odd['oddName'] == '2':
                bet_2 = odd['oddNumber']
        # not a perfect solution because bet_0 can be locked or not available on the site but still relevant option
        if (bet_0 == -1) and (not (bet_1 == bet_2 == -1)):
            bet_11 = bet_1
            bet_1 = -1
            bet_22 = bet_2
            bet_2 = -1
        basic_sport_event_item = BasicSportEventItem()
        basic_sport_event_item['bookmaker_id'] = 'ST'
        basic_sport_event_item['bookmaker_name'] = 'synottip'
        basic_sport_event_item['sport_name'] = ''
        basic_sport_event_item['sport_name_original'] = sport
        basic_sport_event_item['event_url'] = event_url
        basic_sport_event_item['event_startTime'] = event_startTime
        basic_sport_event_item['participant_home'] = participant_1
        basic_sport_event_item['participant_away'] = participant_2
        basic_sport_event_item['bet_1'] = bet_1
        basic_sport_event_item['bet_0'] = bet_0
        basic_sport_event_item['bet_2'] = bet_2
        basic_sport_event_item['bet_10'] = bet_10
        basic_sport_event_item['bet_02'] = bet_02
        basic_sport_event_item['bet_12'] = bet_12
        basic_sport_event_item['bet_11'] = bet_11
        basic_sport_event_item['bet_22'] = bet_22
        return basic_sport_event_item