import scrapy
import json
import os
import copy
from curl_cffi import requests


class SpiderTipsportDetailSpider(scrapy.Spider):
    name = "spider_tipsport_detail"
    allowed_domains = ["www.tipsport.cz"]
    # start_urls = ["https://www.tipsport.cz"]

    custom_settings = {
        'FEEDS': {'data/data_tipsport_detail.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            "headless": True, # True False
            "timeout": 600 * 1000,  # 60 seconds
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 600 * 1000,  # 60 seconds
        'DOWNLOADER_MIDDLEWARES': {
            "scrapy.downloadermiddlewares.cookies.CookiesMiddleware": 543,
        },
        }
    
    def __init__(self, arg_sport_name = None, arg_event_url = None, *args, **kwargs):
        super(SpiderTipsportDetailSpider, self).__init__(*args, **kwargs)
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
        url = 'https://www.tipsport.cz/kurzy.xml'
        yield scrapy.Request(url, meta=dict(playwright = True), callback = self.parse)

    def parse(self, response):
        headers = {
            'Cookie': f"JSESSIONID={str(response.headers.getlist('Set-Cookie')).split('JSESSIONID=')[1].split(';')[0]}",
            'Content-Type': 'application/json'
        }
        if self.arg_sport_name == None or self.arg_event_url == None:
            list_of_items = self.data[:3]
        else:
            list_of_items = [{'sport_name': self.arg_sport_name, 'event_url': self.arg_event_url}]
        for item in list_of_items:
            sport_name = item['sport_name']
            event_url = item['event_url']
            url = f"https://www.tipsport.cz/rest/offer/v1/matches/{event_url.split('/')[-1]}/event-tables"
            response_get = requests.request("GET", url, headers=headers, impersonate='chrome')
            response_json = json.loads(response_get.text)
            try:
                try:
                    translator = copy.deepcopy(self.full_translator[sport_name])
                    template = copy.deepcopy(self.full_template[sport_name])
                except:
                    translator = copy.deepcopy(self.full_translator['other'])
                    template = copy.deepcopy(self.full_template['other'])
                for event_table in response_json['eventTables']:
                    if event_table['name'] == 'Výsledek zápasu':
                        participant_1 = event_table['boxes'][0]['cells'][0]['name']
                        participant_2 = event_table['boxes'][0]['cells'][2]['name']
                        break
                    if event_table['name'] in ('Vítěz zápasu', 'Vítěz zápasu do rozhodnutí'):
                        participant_1 = event_table['boxes'][0]['cells'][0]['name']
                        participant_2 = event_table['boxes'][0]['cells'][1]['name']
                        break
                for event_table in response_json['eventTables']:
                    event_table_name = event_table['name']
                    for box in event_table['boxes']:
                        try:
                            box_name = box['name']
                        except:
                            box_name = ''
                        for cell in box['cells']:
                            cell_name = cell['name']
                            bet_name = ' '.join(' '.join([event_table_name, box_name, cell_name]).replace(participant_1, '1').replace(participant_2, '2').replace('Remíza', '0').split())
                            try:
                                translator_result = translator[bet_name]
                                if template[translator_result['name']][translator_result['option']] < cell['odd']:
                                    template[translator_result['name']][translator_result['option']] = cell['odd']
                            except:
                                pass
                            yield { #############################################################################################################
                                'bet_name': bet_name,
                                'value': cell['odd']
                            }
                yield {
                    'event_url': event_url,
                    'bet_dict': template,
                }
            except:
                pass
