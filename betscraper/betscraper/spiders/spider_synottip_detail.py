import scrapy
import json
import os
import copy
import base64
from protofiles.synottip import protofile_event_double_category_pb2, protofile_event_single_category_pb2
from google.protobuf.json_format import MessageToJson


class SpiderSynottipDetailSpider(scrapy.Spider):
    name = "spider_synottip_detail"
    allowed_domains = ["sport.synottip.cz"]
    # start_urls = ["https://sport.synottip.cz"]

    custom_settings = {
        'FEEDS': {'data/data_synottip_detail.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'CONCURRENT_REQUESTS': 32, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32, # default 8
        }

    def __init__(self, *args, **kwargs):
        super(SpiderSynottipDetailSpider, self).__init__(*args, **kwargs)
        with open(f"data/data_{self.name.split('_')[1]}.json", 'r') as file:
            self.data = json.load(file)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        bets_dict_path = os.path.join(script_dir, '../files/bets_dict.json')
        with open(bets_dict_path, 'r') as file:
            bets_dict = json.load(file)
        self.full_translator = {}
        self.full_template = {}
        for sport_name, bet_name_dict in bets_dict.items():
            self.full_translator[sport_name] = {}
            self.full_template[sport_name] = {}
            for bet_name, bet_option_dict in bet_name_dict.items():
                self.full_template[sport_name][bet_name] = {}
                for bet_option, bookmaker_bets_names_dict in bet_option_dict.items():
                    self.full_template[sport_name][bet_name][bet_option] = -1.0
                    for bookmaker_bets_name in bookmaker_bets_names_dict[self.name.split('_')[1]]:
                        self.full_translator[sport_name][bookmaker_bets_name] = {}
                        self.full_translator[sport_name][bookmaker_bets_name]['name'] = bet_name
                        self.full_translator[sport_name][bookmaker_bets_name]['option'] = bet_option

    def start_requests(self):
        url = "https://sport.synottip.cz/WebServices/Api/SportsBettingService.svc/GetWebStandardEventExt"
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
        }
        for item in self.data[:3]:
            sport_name = item['sport_name']
            event_url = item['event_url']
            payload = json.dumps({
                "LanguageID": 12,
                "Token": "47556bba7e2ecae0a31c38d6e017bcbb",
                "UseLongPolling": True,
                "EventID": int(event_url.split('/')[5].split('c')[0]),
            })
            yield scrapy.Request(
                url,
                method = 'POST',
                body = payload,
                headers = headers,
                callback = self.parse,
                cb_kwargs=dict(sport_name = sport_name, event_url = event_url)
            )

    def parse(self, response, sport_name, event_url):
        try:
            response_json = json.loads(response.text)
            decoded_bytes = base64.b64decode(response_json['ReturnValue'])
            try:
                message = protofile_event_double_category_pb2.SportOrigin_e_d()
                message.ParseFromString(decoded_bytes)
                message_json = json.loads(MessageToJson(message))
                bet_list = message_json['root']['data']['dataSport']['category'][0]['categoryEvents'][0]['eventsInfo']['events'][0]['betDetails']
                # yield self.fill_template_with_bets(bet_list, sport_name, event_url)

                try: # toto je zde jen pro test, po dodelani mohu odstranit a nechat jen funkci viz nizeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
                    translator = copy.deepcopy(self.full_translator[sport_name])
                    template = copy.deepcopy(self.full_template[sport_name])
                except:
                    translator = copy.deepcopy(self.full_translator['other'])
                    template = copy.deepcopy(self.full_template['other'])
                for bet_category in bet_list:
                    for bet in bet_category['bet']:
                        for bets_info in bet['betsInfo']:
                            market_name = bets_info['betName']
                            for odd in bets_info['odds']:
                                odd_name = odd['oddName']
                                bet_name = ' '.join([market_name, odd_name])
                                try:
                                    translator_result = translator[bet_name]
                                    if template[translator_result['name']][translator_result['option']] < odd['oddNumber']:
                                        template[translator_result['name']][translator_result['option']] = odd['oddNumber']
                                except:
                                    pass
                                # yield {
                                #     'bet_name': bet_name,
                                #     'value': odd['oddNumber']
                                # }
                yield {
                    'event_url': event_url,
                    'bet_dict': template,
                }

            except:
                message = protofile_event_single_category_pb2.SportOrigin_e_s() # seems that single category protofile is only for esports
                message.ParseFromString(decoded_bytes)
                message_json = json.loads(MessageToJson(message))
                bet_list = message_json['root']['data']['dataSport']['category'][0]['eventsInfo']['events'][0]['betDetails']
                # yield self.fill_template_with_bets(bet_list, sport_name, event_url)

                try: # toto je zde jen pro test, po dodelani mohu odstranit a nechat jen funkci viz nizeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
                    translator = copy.deepcopy(self.full_translator[sport_name])
                    template = copy.deepcopy(self.full_template[sport_name])
                except:
                    translator = copy.deepcopy(self.full_translator['other'])
                    template = copy.deepcopy(self.full_template['other'])
                for bet_category in bet_list:
                    for bet in bet_category['bet']:
                        for bets_info in bet['betsInfo']:
                            market_name = bets_info['betName']
                            for odd in bets_info['odds']:
                                odd_name = odd['oddName']
                                bet_name = ' '.join([market_name, odd_name])
                                try:
                                    translator_result = translator[bet_name]
                                    if template[translator_result['name']][translator_result['option']] < odd['oddNumber']:
                                        template[translator_result['name']][translator_result['option']] = odd['oddNumber']
                                except:
                                    pass
                                # yield {
                                #     'bet_name': bet_name,
                                #     'value': odd['oddNumber']
                                # }
                yield {
                    'event_url': event_url,
                    'bet_dict': template,
                }

        except:
            yield { # toto pak muzu asi smazaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaat
                'event_url': event_url,
                'error': True
            }

    def fill_template_with_bets(self, bet_list, sport_name, event_url):
        try:
            translator = copy.deepcopy(self.full_translator[sport_name])
            template = copy.deepcopy(self.full_template[sport_name])
        except:
            translator = copy.deepcopy(self.full_translator['other'])
            template = copy.deepcopy(self.full_template['other'])
        for bet_category in bet_list:
            for bet in bet_category['bet']:
                for bets_info in bet['betsInfo']:
                    market_name = bets_info['betName']
                    for odd in bets_info['odds']:
                        odd_name = odd['oddName']
                        bet_name = ' '.join([market_name, odd_name])
                        try:
                            translator_result = translator[bet_name]
                            if template[translator_result['name']][translator_result['option']] < odd['oddNumber']:
                                template[translator_result['name']][translator_result['option']] = odd['oddNumber']
                        except:
                            pass
                        # yield {
                        #     'bet_name': bet_name,
                        #     'value': odd['oddNumber']
                        # }
        return {
            'event_url': event_url,
            'bet_dict': template,
        }
