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
    
    def __init__(self, *args, **kwargs):
        super(SpiderKingsbetDetailSpider, self).__init__(*args, **kwargs)
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
        for item in self.data[:3]:
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
            for market in response_json['markets']:
                market_name = market['name']
                for odd_id_list in market['desktopOddIds']:
                    for odd_id in odd_id_list:
                        odd_name = odds_dict[str(odd_id)]['name']
                        bet_name = ' '.join([market_name, odd_name])
                        try:
                            translator_result = translator[bet_name]
                            if template[translator_result['name']][translator_result['option']] < odds_dict[str(odd_id)]['price']:
                                template[translator_result['name']][translator_result['option']] = odds_dict[str(odd_id)]['price']
                        except:
                            pass
                        # yield {
                        #     'bet_name': bet_name,
                        #     'value': odds_dict[str(odd_id)]['price']
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
