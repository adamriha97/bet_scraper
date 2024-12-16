import scrapy
import json
import os
import copy


class SpiderMerkurDetailSpider(scrapy.Spider):
    name = "spider_merkur_detail"
    allowed_domains = ["www.merkurxtip.cz", 'sb.merkurxtip.cz']
    start_urls = ["https://sb.merkurxtip.cz/restapi/offer/cs/ttg_lang?desktopVersion=1.37.2.5&locale=cs"]

    custom_settings = {
        'FEEDS': {'data/data_merkur_detail.json': {'format': 'json', 'overwrite': True}},
        'CONCURRENT_REQUESTS': 32, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32, # default 8
        'DOWNLOADER_MIDDLEWARES': {
            'betscraper.middlewares.ScrapeOpsFakeUserAgentMiddleware': 400,
            'betscraper.middlewares.ScrapeOpsFakeBrowserHeaderAgentMiddleware': 300,
            'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550, 
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None, 
        },
        }
    
    def __init__(self, arg_sport_name = None, arg_events_limit = 9999, arg_event_url = None, *args, **kwargs):
        super(SpiderMerkurDetailSpider, self).__init__(*args, **kwargs)
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

    def parse(self, response):
        response_json = json.loads(response.text)

        # self.betMap_dict = {item['code']: item['caption'] for item in response_json['betMap'].values()} # toto byla puvodni verze s nepresnymi nazvy betuuuuuuuuuuuuuuuuuuuuuuuuuuu
        # self.betPickMap_dict = {item['betPickCode']: {'caption': item['caption'], 'label': item['label']} for item in response_json['betPickMap'].values()}

        self.betPickMap_newdict = response_json['betPickMap']
        self.betPickGroupMap_newdict = {f"{str(tip_type)}_{item['sport']}": item['name'] for item in response_json['betPickGroupMap'].values() if item['tipTypes'] for tip_type in item['tipTypes']}
        if self.arg_sport_name == None and self.arg_event_url == None:
            list_of_items = self.data[:self.arg_events_limit]
        elif self.arg_event_url == None:
            list_of_items = [item for item in self.data if item['sport_name'] == self.arg_sport_name][:self.arg_events_limit]
        else:
            list_of_items = [{'sport_name': self.arg_sport_name, 'event_url': self.arg_event_url}]
        for item in list_of_items:
            sport_name = item['sport_name']
            event_url = item['event_url']
            url = f"https://sb.merkurxtip.cz/restapi/offer/cs/match/{event_url.split('/')[-1]}?annex=19&desktopVersion=1.37.2.5"
            yield scrapy.Request(url = url, callback = self.parse_event, cb_kwargs=dict(sport_name = sport_name, event_url = event_url))

    def parse_event(self, response, sport_name, event_url):
        try:
            response_json = json.loads(response.text)
            try:
                translator = copy.deepcopy(self.full_translator[sport_name])
                template = copy.deepcopy(self.full_template[sport_name])
            except:
                translator = copy.deepcopy(self.full_translator['other'])
                template = copy.deepcopy(self.full_template['other'])
            for bet in response_json['betMap'].values():
                for sv_name, bet_detail in bet.items():
                    try:
                        
                        # market_name = self.betMap_dict[bet_detail['bc']] # toto byla puvodni verze s nepresnymi nazvy betuuuuuuuuuuuuuuuuuuuuuuuuuuu
                        # selection_name = self.betPickMap_dict[bet_detail['bpc']]['caption']
                        # if market_name == 'KAŽDÝ TÝM DÁ GÓL':
                        #     market_name = market_name + self.betPickMap_dict[bet_detail['bpc']]['label']

                        tip_type = f"{str(bet_detail['tt'])}_{response_json['sport']}"
                        market_name = self.betPickGroupMap_newdict[tip_type]
                        selection_name = self.betPickMap_newdict[tip_type]['caption']
                    except:
                        continue
                    if sv_name == 'NULL':
                        bet_name = ' '.join([market_name, selection_name])
                    else:
                        detail_name = sv_name.split('=')[-1]
                        bet_name = ' '.join(' '.join([market_name, detail_name, selection_name]).replace('{!goalnr}', '').split())
                    try:
                        translator_result = translator[bet_name]
                        if template[translator_result['name']][translator_result['option']] < bet_detail['ov']:
                            template[translator_result['name']][translator_result['option']] = bet_detail['ov']
                    except:
                        pass
                    yield { #############################################################################################################
                        'bet_name': bet_name,
                        'value': bet_detail['ov']
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
