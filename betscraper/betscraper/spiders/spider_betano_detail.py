import scrapy
import json
import os
import copy


class SpiderBetanoDetailSpider(scrapy.Spider):
    name = "spider_betano_detail"
    allowed_domains = ["www.betano.cz"]
    # start_urls = ["https://www.betano.cz"]

    # with open('data/data_betano.json', 'r') as file:
    #     data = json.load(file)
    #     if isinstance(data, list):
    #         start_urls = [
    #             f"https://www.betano.cz/api/zapas-sance/{'/'.join(item.get('event_url').split('/')[4:])}?bt=99&req=la,t,s,stnf,c,mb,mbl"
    #             for item in data if "event_url" in item
    #         ]
    #         start_urls = start_urls[:1]
    
    custom_settings = {
        'FEEDS': {'data/data_betano_detail.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'CONCURRENT_REQUESTS': 512, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 512, # default 8
        }
    
    def __init__(self, arg_sport_name = None, arg_events_limit = 9999, arg_event_url = None, arg_yieldBetNames = False, *args, **kwargs):
        super(SpiderBetanoDetailSpider, self).__init__(*args, **kwargs)
        self.arg_sport_name = arg_sport_name
        self.arg_events_limit = int(arg_events_limit)
        self.arg_event_url = arg_event_url
        self.arg_yieldBetNames = bool(arg_yieldBetNames)

        with open(f"data/data_{self.name.split('_')[1]}.json", 'r') as file:
            self.data = json.load(file)
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        translator_path = os.path.join(script_dir, f"../files/detail_dicts/{self.name.split('_')[1]}_translator.json")
        with open(translator_path, 'r') as file:
            self.full_translator = json.load(file)
        template_path = os.path.join(script_dir, '../files/detail_dicts/template.json')
        with open(template_path, 'r') as file:
            self.full_template = json.load(file)

    def start_requests(self):
        if self.arg_sport_name == None and self.arg_event_url == None:
            list_of_items = self.data[:self.arg_events_limit]
        elif self.arg_event_url == None:
            list_of_items = [item for item in self.data if item['sport_name'] == self.arg_sport_name][:self.arg_events_limit]
        else:
            list_of_items = [{'sport_name': self.arg_sport_name, 'event_url': self.arg_event_url}]
        for item in list_of_items:
            sport_name = item['sport_name']
            event_url = item['event_url']
            url = f"https://www.betano.cz/api/zapas-sance/{'/'.join(event_url.split('/')[4:])}?bt=99&req=la,t,s,stnf,c,mb,mbl"
            yield scrapy.Request(url = url, callback = self.parse, cb_kwargs=dict(sport_name = sport_name, event_url = event_url))

    def parse(self, response, sport_name, event_url):
        response_json = json.loads(response.text)
        try:
            if response_json["errorCode"] == 302:
                pass
            yield { # s timto neco udelaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaat mozna
                'test': response_json["errorCode"],
                'full_translator': self.full_translator['other'],
                'full_template': self.full_template['other'],
                'sport_name': sport_name,
                'event_url': event_url,
            }
        except:
            call_number = response.url.split('/?bt=')[1].split('&')[0]
            if response_json['data']['markets'][-1]['name'] in ('Vše', 'Všechny příležitosti') or call_number != '99':
                try:
                    translator = copy.deepcopy(self.full_translator[sport_name])
                    template = copy.deepcopy(self.full_template[sport_name])
                except:
                    translator = copy.deepcopy(self.full_translator['other'])
                    template = copy.deepcopy(self.full_template['other'])
                participant_1 = response_json['data']['event']['participants'][0]['name']
                participant_2 = response_json['data']['event']['participants'][1]['name']
                try:
                    markets = response_json['data']['event']['sixPackLayout']['columns'] + response_json['data']['event']['markets']
                except:
                    markets = response_json['data']['event']['markets']
                for market in markets:
                    market_name = market['name']
                    for selection in market['selections']:
                        selection_name = selection['name']
                        bet_name = ' '.join([market_name, selection_name]).replace(participant_1, '1').replace(participant_2, '2').replace('Remíza', '0')
                        try:
                            translator_result = translator[bet_name]
                            if template[translator_result['name']][translator_result['group']][translator_result['option']] < selection['price']:
                                template[translator_result['name']][translator_result['group']][translator_result['option']] = selection['price']
                        except:
                            pass
                        if self.arg_yieldBetNames:
                            yield { #############################################################################################################
                                'bet_name': bet_name,
                                'value': selection['price']
                            }
                    try:
                        table_name = market['tableLayout']['title']
                        for row in market['tableLayout']['rows']:
                            row_name = row['title']
                            for group_selection in row['groupSelections']:
                                for selection in group_selection['selections']:
                                    selection_name = selection['name']
                                    bet_name = ' '.join([table_name, row_name, selection_name]).replace(participant_1, '1').replace(participant_2, '2').replace('Remíza', '0')
                                    try:
                                        translator_result = translator[bet_name]
                                        if template[translator_result['name']][translator_result['group']][translator_result['option']] < selection['price']:
                                            template[translator_result['name']][translator_result['group']][translator_result['option']] = selection['price']
                                    except:
                                        pass
                                    if self.arg_yieldBetNames:
                                        yield { #############################################################################################################
                                            'bet_name': bet_name,
                                            'value': selection['price']
                                        }
                    except:
                        pass
                yield {
                    'event_url': event_url,
                    'bet_dict': template,
                }
            else:
                for index, market_group in enumerate(response_json['data']['markets']):
                    if market_group['name'] in ('Vše', 'Všechny příležitosti'):
                        url = f"https://www.betano.cz/api/zapas-sance/{'/'.join(event_url.split('/')[4:])}?bt={str(index)}&req=la,t,s,stnf,c,mb,mbl"
                        yield scrapy.Request(url = url, callback = self.parse, cb_kwargs=dict(sport_name = sport_name, event_url = event_url))
                        break
