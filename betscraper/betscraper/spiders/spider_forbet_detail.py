import scrapy
import json
import os
import copy


class SpiderForbetDetailSpider(scrapy.Spider):
    name = "spider_forbet_detail"
    allowed_domains = ["www.fbet.cz"]
    # start_urls = ["https://www.fbet.cz"]

    custom_settings = {
        'FEEDS': {'data/data_forbet_detail.json': {'format': 'json', 'overwrite': True}},
        'CONCURRENT_REQUESTS': 32, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32, # default 8
        'DOWNLOADER_MIDDLEWARES': {
            'betscraper.middlewares.ScrapeOpsFakeUserAgentMiddleware': 400,
        },
        }
    
    def __init__(self, arg_sport_name = None, arg_events_limit = 9999, arg_event_url = None, *args, **kwargs):
        super(SpiderForbetDetailSpider, self).__init__(*args, **kwargs)
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
        url = 'https://www.fbet.cz/api/web/v1/offer/full_offer'
        body = json.dumps({
            "offerMode": "prematch",
            "lang": "cs"
        })
        headers = {
            'Content-Type': 'application/json'
        }
        yield scrapy.Request(url=url, headers=headers, body=body, method="POST", callback = self.parse)

    def parse(self, response):
        self.response_json_full_offer = json.loads(response.text)
        url = 'https://www.fbet.cz/api/web/v1/offer/event_detail'
        headers = {
            'Content-Type': 'application/json'
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
            body = json.dumps({
                "offerMode": "prematch",
                "lang": "cs",
                "id_event": event_url.split('/')[-1]
            })
            yield scrapy.Request(
                url = url,
                headers = headers,
                body = body,
                method = "POST",
                callback = self.parse_event,
                cb_kwargs=dict(sport_name = sport_name, event_url = event_url)
            )

    def parse_event(self, response, sport_name, event_url):
        try:
            response_json = json.loads(response.text)
            tournament_json = self.response_json_full_offer['data']['tournament'][response_json['data']['tournamentId']]
            category_json = self.response_json_full_offer['data']['category'][str(tournament_json['categoryId'])]
            market_list = self.response_json_full_offer['data']['market_list'][str(category_json['sportId'])]
            try:
                translator = copy.deepcopy(self.full_translator[sport_name])
                template = copy.deepcopy(self.full_template[sport_name])
            except:
                translator = copy.deepcopy(self.full_translator['other'])
                template = copy.deepcopy(self.full_template['other'])
            for market in response_json['data']['markets'].values():
                market_dict = market_list[str(market['marketId'])]
                market_name = market_dict['name']
                try:
                    specifier_name = market['specifiers'].split('=')[-1]
                except:
                    specifier_name = ''
                for odd in market['odds'].values():
                    outcome_name = market_dict['outcome'][str(odd['outcomeId'])]['short']
                    bet_name = ' '.join(' '.join([market_name, specifier_name, outcome_name]).replace('{$competitor1}', '1').replace('{$competitor2}', '2').replace('{total}', '').replace('{hcp}', '').replace('{!goalnr}', '').replace('{!setnr}', '').replace('{!periodnr}', '').split())
                    try:
                        translator_result = translator[bet_name]
                        if template[translator_result['name']][translator_result['option']] < odd['odds']:
                            template[translator_result['name']][translator_result['option']] = odd['odds']
                    except:
                        pass
                    yield { #############################################################################################################
                        'bet_name': bet_name,
                        'value': odd['odds']
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
