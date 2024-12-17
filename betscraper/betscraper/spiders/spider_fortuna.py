import scrapy
import datetime
import re

from betscraper.items import BasicSportEventItem


class SpiderFortunaSpider(scrapy.Spider):
    name = "spider_fortuna"
    allowed_domains = ["www.ifortuna.cz"]
    start_urls = ["https://www.ifortuna.cz/"]

    custom_settings = {
        'FEEDS': {'data/data_fortuna.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'CONCURRENT_REQUESTS': 64, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 64, # default 8
        'ITEM_PIPELINES': {
            "betscraper.pipelines.DropDuplicatesPipeline": 350,
            "betscraper.pipelines.UnifySportNamesPipeline": 400,
            "betscraper.pipelines.UnifyCountryNamesPipeline": 410,
            "betscraper.pipelines.UnifySportDetailsPipeline": 420,
            "betscraper.pipelines.PopulateParticipantListsPipeline": 600,
        },
        }

    def parse(self, response):
        global sports_dict
        links = response.css('ul#filterbox-ref-sport-tree li a.btn-sport ::attr(href)').getall()
        sports_dict = {sport_item: 1 for sport_item in [link.split('/')[2].split('?')[0].split('-202')[0] for link in links]}
        # pro nektere sporty chci prohledat rovnou vice stranek kvuli efektivite
        sports_dict['fotbal'] = 20
        sports_dict['tenis'] = 5
        sports_dict['hokej'] = 5
        not_interested = ['hotovky', 'favorit-plus', 'fotbal-special', 'tenis-special', 'cyklistika', 'dostihy', 'f1', 'finance', 'golf', 'motorismus', 'politika', 'stane-se-v-roce', 'zabava']
        for sport, pages in sports_dict.items():
            if sport not in not_interested:
                for page in range(pages):
                    url = f'https://www.ifortuna.cz/bets/ajax/loadmoresport/{sport}?timeTo=&rateFrom=&rateTo=&date=&pageSize=100&page={page}' # 'https://www.ifortuna.cz/bets/ajax/loadmoresport/fotbal?timeTo=&rateFrom=&rateTo=&date=&pageSize=100&page=0'
                    yield response.follow(url, callback = self.parse_sport)
    
    def parse_sport(self, response):
        continue_parse = False
        sport = response.url.split('/')[-1].split('?')[0]
        page_number = int(response.url.split('=')[-1])
        for section in response.css('section.competition-box'):
            secondary_category_original = section.css('section.competition-box ::attr(data-competition-name)').get()
            primary_category_original = secondary_category_original
            primary_category = re.sub(r'\d+\.', '', primary_category_original)
            primary_category = re.sub(r'U\d{2}', '', primary_category)
            for substring in ['-ženy', '-muži', 'Ž-', 'M-', ', dvouhra', ', čtyřhra', ' ()', 'WTA ', 'ATP ', 'ITF ', 'Chall. ']:
                primary_category = primary_category.replace(substring, '')
            primary_category = ' '.join([word for word in primary_category.split() if not re.search(r'\d', word)])
            secondary_category = primary_category
            primary_category = primary_category.split('-')[0].strip()
            if 'esport' in sport:
                sport_detail_original = sport
            else:
                sport_detail_original = primary_category
            for table in section.css('table.events-table'):
                continue_parse = True
                try:
                    if table.css('thead th.col-title span.market-sub-name ::text').get().replace('\n', '').startswith(("Výsledek zápasu", "Vítěz zápasu")):
                        for event in table.css('tbody tr'):
                            try:
                                event_url = f"https://www.ifortuna.cz{event.css('a.event-link ::attr(href)').get()}"
                                event_id = event_url.split('-')[-1]
                                event_startTime = datetime.datetime.fromtimestamp(int(event.css('td.col-date ::attr(data-value)').get())/1000)
                                participants = event.css('div.title-container div.event-name span ::text').get().replace('\n', '').split(' - ')
                                participant_1 = participants[0]
                                participant_2 = participants[1]
                                participants_gender = ''
                                if any(sub in secondary_category_original for sub in ['ženy', 'Ž-']):
                                    participants_gender = 'zeny'
                                # elif any(sub in secondary_category_original for sub in ['muži', 'M-']):
                                #     participants_gender = 'muzi'
                                participants_age = ''
                                participant_1_hasAge = re.search(r'U\d{2}', participant_1)
                                participant_2_hasAge = re.search(r'U\d{2}', participant_2)
                                if participant_1_hasAge and participant_2_hasAge and (participant_1_hasAge.group(0) == participant_2_hasAge.group(0)):
                                    participants_age = participant_1_hasAge.group(0)
                                bet_1 = bet_0 = bet_2 = bet_10 = bet_02 = bet_12 = bet_11 = bet_22 = -1
                                bets = [float(bet) for bet in event.css('span.odds-value ::text').getall()]
                                if len(bets) == 3:
                                    bet_1 = bets[0]
                                    bet_0 = bets[1]
                                    bet_2 = bets[2]
                                elif len(bets) == 2:
                                    bet_11 = bets[0]
                                    bet_22 = bets[1]
                                elif len(bets) in [6, 9]: # 6 -> možnosti 10, 02, 12 # 9 -> chyba na webu (hádám)
                                    bet_1 = bets[0]
                                    bet_0 = bets[1]
                                    bet_2 = bets[2]
                                    bet_10 = bets[3] # toto poradi tipuji, na strankach jsem to nezkontroloval
                                    bet_12 = bets[4] # toto poradi tipuji, na strankach jsem to nezkontroloval
                                    bet_02 = bets[5] # toto poradi tipuji, na strankach jsem to nezkontroloval
                                basic_sport_event_item = BasicSportEventItem()
                                basic_sport_event_item['bookmaker_id'] = 'FO'
                                basic_sport_event_item['bookmaker_name'] = 'fortuna'
                                basic_sport_event_item['sport_name'] = ''
                                basic_sport_event_item['sport_name_original'] = sport
                                basic_sport_event_item['sport_detail'] = ''
                                basic_sport_event_item['sport_detail_original'] = sport_detail_original
                                basic_sport_event_item['country_name'] = ''
                                basic_sport_event_item['country_name_original'] = ''
                                basic_sport_event_item['primary_category'] = primary_category
                                basic_sport_event_item['primary_category_original'] = primary_category_original
                                basic_sport_event_item['secondary_category'] = secondary_category
                                basic_sport_event_item['secondary_category_original'] = secondary_category_original
                                basic_sport_event_item['event_startTime'] = event_startTime
                                basic_sport_event_item['participant_home'] = participant_1
                                basic_sport_event_item['participant_away'] = participant_2
                                basic_sport_event_item['participant_home_list'] = ()
                                basic_sport_event_item['participant_away_list'] = ()
                                basic_sport_event_item['participants_gender'] = participants_gender
                                basic_sport_event_item['participants_age'] = participants_age
                                basic_sport_event_item['bet_1'] = bet_1
                                basic_sport_event_item['bet_0'] = bet_0
                                basic_sport_event_item['bet_2'] = bet_2
                                basic_sport_event_item['bet_10'] = bet_10
                                basic_sport_event_item['bet_02'] = bet_02
                                basic_sport_event_item['bet_12'] = bet_12
                                basic_sport_event_item['bet_11'] = bet_11
                                basic_sport_event_item['bet_22'] = bet_22
                                basic_sport_event_item['event_id'] = basic_sport_event_item['bookmaker_id'] + '_' + event_id
                                basic_sport_event_item['event_url'] = event_url
                                yield basic_sport_event_item
                            except:
                                pass
                except:
                    pass
        if sports_dict[sport] > (page_number + 1):
            continue_parse = False
        if continue_parse:
            parts_url = response.url.split('=')
            parts_url[-1] = str(int(parts_url[-1]) + 1)
            next_url = '='.join(parts_url)
            yield response.follow(next_url, callback = self.parse_sport)