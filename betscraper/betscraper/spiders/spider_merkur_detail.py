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
    
    def __init__(self, *args, **kwargs):
        super(SpiderMerkurDetailSpider, self).__init__(*args, **kwargs)
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
        self.betMap_dict = {item['code']: item['caption'] for item in response_json['betMap'].values()}
        self.betPickMap_dict = {item['betPickCode']: item['caption'] for item in response_json['betPickMap'].values()}
        for item in self.data[:3]:
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
                    market_name = self.betMap_dict[bet_detail['bc']]
                    selection_name = self.betPickMap_dict[bet_detail['bpc']]
                    if sv_name == 'NULL':
                        bet_name = ' '.join([market_name, selection_name])
                    else:
                        detail_name = sv_name.split('=')[-1]
                        bet_name = ' '.join([market_name, selection_name, detail_name])
                    try:
                        translator_result = translator[bet_name]
                        if template[translator_result['name']][translator_result['option']] < bet_detail['ov']:
                            template[translator_result['name']][translator_result['option']] = bet_detail['ov']
                    except:
                        pass
                    # yield {
                    #     'bet_name': bet_name,
                    #     'value': bet_detail['ov']
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
