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
    
    def __init__(self, *args, **kwargs):
        super(SpiderBetanoDetailSpider, self).__init__(*args, **kwargs)
        with open('data/data_betano.json', 'r') as file:
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
        for item in self.data[:3]:
            sport_name = item['sport_name']
            event_url = item['event_url']
            url = f"https://www.betano.cz/api/zapas-sance/{'/'.join(event_url.split('/')[4:])}?bt=99&req=la,t,s,stnf,c,mb,mbl"
            yield scrapy.Request(url = url, callback = self.parse, cb_kwargs=dict(sport_name = sport_name, event_url = event_url))

    def parse(self, response, sport_name, event_url):
        response_json = json.loads(response.text)
        try:
            if response_json["errorCode"] == 302:
                pass
            yield {
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
                for market in response_json['data']['event']['markets']:
                    market_name = market['name']
                    for selection in market['selections']:
                        selection_name = selection['name']
                        bet_name = ' '.join([market_name, selection_name]).replace(participant_1, '1').replace(participant_2, '2').replace('Remíza', '0')
                        try:
                            translator_result = translator[bet_name]
                            if template[translator_result['name']][translator_result['option']] < selection['price']:
                                template[translator_result['name']][translator_result['option']] = selection['price']
                        except:
                            pass
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
                                        if template[translator_result['name']][translator_result['option']] < selection['price']:
                                            template[translator_result['name']][translator_result['option']] = selection['price']
                                    except:
                                        pass
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
