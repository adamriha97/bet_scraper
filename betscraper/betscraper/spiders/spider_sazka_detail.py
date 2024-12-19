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
    
    def __init__(self, arg_data = None, arg_sport_name = None, arg_events_limit = 9999, arg_event_url = None, arg_yieldBetNames = False, *args, **kwargs):
        super(SpiderSazkaDetailSpider, self).__init__(*args, **kwargs)
        self.arg_sport_name = arg_sport_name
        self.arg_events_limit = int(arg_events_limit)
        self.arg_event_url = arg_event_url
        self.arg_yieldBetNames = bool(arg_yieldBetNames)
        if arg_data is not None:
            self.data = arg_data
        else:
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
        headers = {
            'x-accept-language': 'cs-CZ',
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
                        if template[translator_result['name']][translator_result['group']][translator_result['option']] < outcome['prices'][0]['decimal']:
                            template[translator_result['name']][translator_result['group']][translator_result['option']] = outcome['prices'][0]['decimal']
                    except:
                        pass
                    if self.arg_yieldBetNames:
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
