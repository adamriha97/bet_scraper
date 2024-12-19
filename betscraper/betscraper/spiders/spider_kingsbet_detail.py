import scrapy
import json
import os
import copy


class SpiderKingsbetDetailSpider(scrapy.Spider):
    name = "spider_kingsbet_detail"
    allowed_domains = ["www.kingsbet.cz", 'sb2frontend-altenar2.biahosted.com']
    # start_urls = ["https://www.kingsbet.cz"]

    custom_settings = {
        'FEEDS': {'data/data_kingsbet_detail.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'CONCURRENT_REQUESTS': 32, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32, # default 8
        }
    
    def __init__(self, arg_data = None, arg_sport_name = None, arg_events_limit = 9999, arg_event_url = None, arg_yieldBetNames = False, *args, **kwargs):
        super(SpiderKingsbetDetailSpider, self).__init__(*args, **kwargs)
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
        if self.arg_sport_name == None and self.arg_event_url == None:
            list_of_items = self.data[:self.arg_events_limit]
        elif self.arg_event_url == None:
            list_of_items = [item for item in self.data if item['sport_name'] == self.arg_sport_name][:self.arg_events_limit]
        else:
            list_of_items = [{'sport_name': self.arg_sport_name, 'event_url': self.arg_event_url}]
        for item in list_of_items:
            sport_name = item['sport_name']
            event_url = item['event_url']
            url = f"https://sb2frontend-altenar2.biahosted.com/api/widget/GetEventDetails?culture=cs-CZ&timezoneOffset=-60&integration=kingsbet&deviceType=1&numFormat=en-GB&countryCode=CZ&eventId={event_url.split('=')[-1]}"
            yield scrapy.Request(url = url, callback = self.parse, cb_kwargs=dict(sport_name = sport_name, event_url = event_url))

    def parse(self, response, sport_name, event_url):
        try:
            response_json = json.loads(response.text)
            odds_dict = {str(odd['id']): odd for odd in response_json['odds']}
            try:
                translator = copy.deepcopy(self.full_translator[sport_name])
                template = copy.deepcopy(self.full_template[sport_name])
            except:
                translator = copy.deepcopy(self.full_translator['other'])
                template = copy.deepcopy(self.full_template['other'])
            participant_1 = response_json['competitors'][0]['name']
            participant_2 = response_json['competitors'][1]['name']
            for market in response_json['markets']:
                market_name = market['name']
                for odd_id_list in market['desktopOddIds']:
                    for odd_id in odd_id_list:
                        odd_name = odds_dict[str(odd_id)]['name']
                        bet_name = ' '.join([market_name, odd_name]).replace(participant_1, '1').replace(participant_2, '2')
                        try:
                            translator_result = translator[bet_name]
                            if template[translator_result['name']][translator_result['group']][translator_result['option']] < odds_dict[str(odd_id)]['price']:
                                template[translator_result['name']][translator_result['group']][translator_result['option']] = odds_dict[str(odd_id)]['price']
                        except:
                            pass
                        if self.arg_yieldBetNames:
                            yield { #############################################################################################################
                                'bet_name': bet_name,
                                'value': odds_dict[str(odd_id)]['price']
                            }
            yield {
                'event_url': event_url,
                'bet_dict': template,
            }
        except:
            yield { # toto pak muzu asi smazaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaat
                'event_url': event_url,
                'error': True
            }
