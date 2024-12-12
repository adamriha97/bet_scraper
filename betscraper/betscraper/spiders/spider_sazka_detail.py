import scrapy
import json
import os
import copy


class SpiderSazkaDetailSpider(scrapy.Spider):
    name = "spider_sazka_detail"
    allowed_domains = ["www.sazka.cz", "sg-content-engage-prod.sazka.cz"]
    # start_urls = ["https://www.sazka.cz"]

    custom_settings = {
        'FEEDS': {'data/data_sazka_detail.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'CONCURRENT_REQUESTS': 64, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 64, # default 8
        }
    
    def __init__(self, arg_sport_name = None, arg_event_url = None, *args, **kwargs):
        super(SpiderSazkaDetailSpider, self).__init__(*args, **kwargs)
        self.arg_sport_name = arg_sport_name
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
        headers = {
            'x-accept-language': 'cs-CZ',
        }
        if self.arg_sport_name == None or self.arg_event_url == None:
            list_of_items = self.data[:3]
        else:
            list_of_items = [{'sport_name': self.arg_sport_name, 'event_url': self.arg_event_url}]
        for item in list_of_items:
            sport_name = item['sport_name']
            event_url = item['event_url']
            url = f"https://sg-content-engage-prod.sazka.cz/content-service/api/v1/q/events-by-ids?eventIds={event_url.split('/')[-1]}&includeChildMarkets=true&includeCollections=true&includePriceHistory=false&includeCommentary=false&includeIncidents=false&includeRace=false&includeMedia=false&includePools=false&includeNonFixedOdds=false"
            yield scrapy.Request(url = url, method = 'GET', headers = headers, callback = self.parse, cb_kwargs=dict(sport_name = sport_name, event_url = event_url))

    def parse(self, response, sport_name, event_url):
        response_json = json.loads(response.text)
        try:
            try:
                translator = copy.deepcopy(self.full_translator[sport_name])
                template = copy.deepcopy(self.full_template[sport_name])
            except:
                translator = copy.deepcopy(self.full_translator['other'])
                template = copy.deepcopy(self.full_template['other'])
            participant_1 = response_json['data']['events'][0]['teams'][0]['name']
            participant_2 = response_json['data']['events'][0]['teams'][1]['name']
            for market in response_json['data']['events'][0]['markets']:
                market_name = market['name']
                for outcome in market['outcomes']:
                    outcome_name = outcome['name']
                    bet_name = ' '.join([market_name, outcome_name]).replace(participant_1, '1').replace(participant_2, '2').replace('Remíza', '0')
                    try:
                        translator_result = translator[bet_name]
                        if template[translator_result['name']][translator_result['option']] < outcome['prices'][0]['decimal']:
                            template[translator_result['name']][translator_result['option']] = outcome['prices'][0]['decimal']
                    except:
                        pass
                    yield { #############################################################################################################
                        'bet_name': bet_name,
                        'value': outcome['prices'][0]['decimal']
                    }
            yield {
                'event_url': event_url,
                'bet_dict': template,
            }
        except:
            yield { # toto pak asi muzu smazaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaat
                'event_url': event_url,
            }
