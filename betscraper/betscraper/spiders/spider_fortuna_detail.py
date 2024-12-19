import scrapy
import json
import os
import copy


class SpiderFortunaDetailSpider(scrapy.Spider):
    name = "spider_fortuna_detail"
    allowed_domains = ["www.ifortuna.cz"]
    # start_urls = ["https://www.ifortuna.cz"]

    custom_settings = {
        'FEEDS': {'data/data_fortuna_detail.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'CONCURRENT_REQUESTS': 64, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 64, # default 8
        }
    
    def __init__(self, arg_data = None, arg_sport_name = None, arg_events_limit = 9999, arg_event_url = None, arg_yieldBetNames = False, *args, **kwargs):
        super(SpiderFortunaDetailSpider, self).__init__(*args, **kwargs)
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
            url = f"{event_url}?market_filter=all"
            yield scrapy.Request(url = url, callback = self.parse, cb_kwargs=dict(sport_name = sport_name, event_url = event_url))

    def parse(self, response, sport_name, event_url):
        try:
            try:
                translator = copy.deepcopy(self.full_translator[sport_name])
                template = copy.deepcopy(self.full_template[sport_name])
            except:
                translator = copy.deepcopy(self.full_translator['other'])
                template = copy.deepcopy(self.full_template['other'])
            main_market = response.css('div.events-table-box--main-market')
            participants = main_market.css('tbody span.market-name ::text').get().replace('\n', '').split(' - ')
            participant_1 = participants[0]
            participant_2 = participants[1]
            main_market_name = main_market.css('thead span.market-sub-name ::text').get().replace('\n', '')
            col_names = main_market.css('thead th.col-odds')
            col_values = main_market.css('tbody td.col-odds')
            for col_name, col_value in zip(col_names, col_values):
                col_name_text = col_name.css('span ::text').get().replace('\n', '').strip()
                col_value_text = col_value.css('span ::text').get()
                bet_name = ' '.join(' '.join([main_market_name, col_name_text]).replace(participant_1, '1').replace(participant_2, '2').replace('Remíza', '0').split())
                try:
                    translator_result = translator[bet_name]
                    if template[translator_result['name']][translator_result['group']][translator_result['option']] < float(col_value_text):
                        template[translator_result['name']][translator_result['group']][translator_result['option']] = float(col_value_text)
                except:
                    pass
                if self.arg_yieldBetNames:
                    yield { #############################################################################################################
                        'bet_name': bet_name,
                        'value': float(col_value_text)
                    }
            markets = response.css('div.market')
            for market in markets:
                market_name = market.css('h3 a ::text').get().replace('\n', '')
                buttons = market.css('div.odds a.odds-button')
                for button in buttons:
                    button_name = button.css('span.odds-name ::text').get().replace('\n', '')
                    value_text = button.css('span.odds-value ::text').get()
                    bet_name = ' '.join(' '.join([market_name, button_name]).replace(participant_1, '1').replace(participant_2, '2').replace('Remíza', '0').split())
                    try:
                        translator_result = translator[bet_name]
                        if template[translator_result['name']][translator_result['group']][translator_result['option']] < float(value_text):
                            template[translator_result['name']][translator_result['group']][translator_result['option']] = float(value_text)
                    except:
                        pass
                    if self.arg_yieldBetNames:
                        yield { #############################################################################################################
                            'bet_name': bet_name,
                            'value': float(value_text)
                        }
            yield {
                'event_url': event_url,
                'bet_dict': template,
            }
        except:
            yield {
                'event_url': event_url,
            }
