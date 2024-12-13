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

    def __init__(self, arg_sport_name = None, arg_events_limit = 9999, arg_event_url = None, *args, **kwargs):
        super(SpiderSynottipDetailSpider, self).__init__(*args, **kwargs)
        self.arg_sport_name = arg_sport_name
        self.arg_events_limit = int(arg_events_limit)
        self.arg_event_url = arg_event_url
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
        if self.arg_sport_name == None and self.arg_event_url == None:
            list_of_items = self.data[:self.arg_events_limit]
        elif self.arg_event_url == None:
            list_of_items = [item for item in self.data if item['sport_name'] == self.arg_sport_name][:self.arg_events_limit]
        else:
            list_of_items = [{'sport_name': self.arg_sport_name, 'event_url': self.arg_event_url}]
        for item in list_of_items:
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
                event_dict = message_json['root']['data']['dataSport']['category'][0]['categoryEvents'][0]['eventsInfo']['events'][0]
                for yield_item in self.fill_template_with_bets(event_dict, sport_name, event_url):
                    yield yield_item

                # bet_list = event_dict['betDetails']
                # try: # toto je zde jen pro test, po dodelani mohu odstranit a nechat jen funkci viz nizeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
                #     translator = copy.deepcopy(self.full_translator[sport_name])
                #     template = copy.deepcopy(self.full_template[sport_name])
                # except:
                #     translator = copy.deepcopy(self.full_translator['other'])
                #     template = copy.deepcopy(self.full_template['other'])
                # participants = event_dict['eventName'].split(' - ')
                # participant_1 = participants[0]
                # participant_2 = participants[1]
                # for bet_category in bet_list:
                #     for bet in bet_category['bet']:
                #         for bets_info in bet['betsInfo']:
                #             market_name = bets_info['betName']
                #             for odd in bets_info['odds']:
                #                 odd_name = odd['oddName']
                #                 bet_name = ' '.join(' '.join([market_name, odd_name]).replace(participant_1, '1').replace(participant_2, '2').split())
                #                 try:
                #                     translator_result = translator[bet_name]
                #                     if template[translator_result['name']][translator_result['option']] < odd['oddNumber']:
                #                         template[translator_result['name']][translator_result['option']] = odd['oddNumber']
                #                 except:
                #                     pass
                #                 yield { #############################################################################################################
                #                     'bet_name': bet_name,
                #                     'value': odd['oddNumber']
                #                 }
                # yield {
                #     'event_url': event_url,
                #     'bet_dict': template,
                # }

            except:
                message = protofile_event_single_category_pb2.SportOrigin_e_s() # seems that single category protofile is only for esports
                message.ParseFromString(decoded_bytes)
                message_json = json.loads(MessageToJson(message))
                event_dict = message_json['root']['data']['dataSport']['category'][0]['eventsInfo']['events'][0]
                for yield_item in self.fill_template_with_bets(event_dict, sport_name, event_url):
                    yield yield_item

                # bet_list = event_dict['betDetails']
                # try: # toto je zde jen pro test, po dodelani mohu odstranit a nechat jen funkci viz nizeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
                #     translator = copy.deepcopy(self.full_translator[sport_name])
                #     template = copy.deepcopy(self.full_template[sport_name])
                # except:
                #     translator = copy.deepcopy(self.full_translator['other'])
                #     template = copy.deepcopy(self.full_template['other'])
                # participants = event_dict['eventName'].split(' - ')
                # participant_1 = participants[0]
                # participant_2 = participants[1]
                # for bet_category in bet_list:
                #     for bet in bet_category['bet']:
                #         for bets_info in bet['betsInfo']:
                #             market_name = bets_info['betName']
                #             for odd in bets_info['odds']:
                #                 odd_name = odd['oddName']
                #                 bet_name = ' '.join(' '.join([market_name, odd_name]).replace(participant_1, '1').replace(participant_2, '2').split())
                #                 try:
                #                     translator_result = translator[bet_name]
                #                     if template[translator_result['name']][translator_result['option']] < odd['oddNumber']:
                #                         template[translator_result['name']][translator_result['option']] = odd['oddNumber']
                #                 except:
                #                     pass
                #                 yield { #############################################################################################################
                #                     'bet_name': bet_name,
                #                     'value': odd['oddNumber']
                #                 }
                # yield {
                #     'event_url': event_url,
                #     'bet_dict': template,
                # }

        except:
            yield { # toto pak muzu asi smazaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaat
                'event_url': event_url,
                'error': True
            }

    def fill_template_with_bets(self, event_dict, sport_name, event_url):
        yield_list = []
        bet_list = event_dict['betDetails']
        try:
            translator = copy.deepcopy(self.full_translator[sport_name])
            template = copy.deepcopy(self.full_template[sport_name])
        except:
            translator = copy.deepcopy(self.full_translator['other'])
            template = copy.deepcopy(self.full_template['other'])
        participants = event_dict['eventName'].split(' - ')
        participant_1 = participants[0]
        participant_2 = participants[1]
        for bet_category in bet_list:
            for bet in bet_category['bet']:
                for bets_info in bet['betsInfo']:
                    market_name = bets_info['betName']
                    for odd in bets_info['odds']:
                        odd_name = odd['oddName']
                        bet_name = ' '.join(' '.join([market_name, odd_name]).replace(participant_1, '1').replace(participant_2, '2').split())
                        try:
                            translator_result = translator[bet_name]
                            if template[translator_result['name']][translator_result['option']] < odd['oddNumber']:
                                template[translator_result['name']][translator_result['option']] = odd['oddNumber']
                        except:
                            pass
                        yield_list.append({
                            'bet_name': bet_name,
                            'value': odd['oddNumber']
                        })
        yield_list.append({
            'event_url': event_url,
            'bet_dict': template,
        })
        return yield_list
