import scrapy
import json
from curl_cffi import requests
from datetime import datetime
import re

from betscraper.items import BasicSportEventItem


class SpiderTipsportSpider(scrapy.Spider):
    name = "spider_tipsport"
    allowed_domains = ["www.tipsport.cz"]
    # start_urls = ["https://www.tipsport.cz/kurzy.xml"] # https://www.tipsport.cz/

    custom_settings = {
        'FEEDS': {'data/data_tipsport.json': {'format': 'json', 'overwrite': True}},
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
        'ITEM_PIPELINES': {
            "betscraper.pipelines.DropDuplicatesPipeline": 350,
            "betscraper.pipelines.UnifySportNamesPipeline": 400,
            "betscraper.pipelines.UnifyCountryNamesPipeline": 410,
            "betscraper.pipelines.UpdateNonDrawBetsPipeline": 500,
        },
        }
    
    def start_requests(self):
        url = 'https://www.tipsport.cz/kurzy.xml'
        yield scrapy.Request(url, meta=dict(playwright = True), callback = self.parse)

    def parse(self, response):
        url = "https://www.tipsport.cz/rest/offer/v2/offer?limit=9999"
        headers = {
        'Cookie': f"JSESSIONID={str(response.headers.getlist('Set-Cookie')).split('JSESSIONID=')[1].split(';')[0]}",
        'Content-Type': 'application/json'
        }
        response_post = requests.request("POST", url, headers=headers, data=json.dumps({}), impersonate='chrome')
        response_json = json.loads(response_post.text)
        for sport_item in response_json['offerSuperSports']:
            for competition_item in sport_item['tabs'][0]['offerCompetitionAnnuals']:
                participants_gender = ''
                try:
                    sport_gender = competition_item['sportGender']
                    gender_mapping = {"WOMEN": "zeny", "MEN": ""} # "MEN": "muzi"
                    participants_gender = gender_mapping.get(sport_gender, sport_gender)
                except:
                    pass
                for match_item in competition_item['matches']:
                    if match_item['matchType'] == 'MATCH':
                        sport = match_item['nameSuperSport']
                        primary_category_original = match_item['nameSport']
                        secondary_category_original = match_item['nameCompetition']
                        event_url = f"https://www.tipsport.cz{match_item['matchUrl']}"
                        event_startTime = datetime.fromisoformat(match_item['datetimeClosed'])
                        participant_1 = match_item['participantHome']
                        participant_2 = match_item['participantVisiting']
                        participants_age = ''
                        participant_1_hasAge = re.search(r'U\d{2}', participant_1)
                        participant_2_hasAge = re.search(r'U\d{2}', participant_2)
                        if participant_1_hasAge and participant_2_hasAge and (participant_1_hasAge.group(0) == participant_2_hasAge.group(0)):
                            participants_age = participant_1_hasAge.group(0)
                        bet_1 = bet_0 = bet_2 = bet_10 = bet_02 = bet_12 = bet_11 = bet_22 = -1
                        for opp_row in match_item['oppRows']:
                            for opp_tab in opp_row['oppsTab']:
                                try:
                                    opp_type = opp_tab['type']
                                    opp_odd = opp_tab['odd']
                                    if opp_type == '1':
                                        bet_1 = opp_odd
                                    elif opp_type == '1x':
                                        bet_10 = opp_odd
                                    elif opp_type == 'x':
                                        bet_0 = opp_odd
                                    elif opp_type == 'x2':
                                        bet_02 = opp_odd
                                    elif opp_type == '2':
                                        bet_2 = opp_odd
                                except:
                                    pass
                        primary_category = primary_category_original
                        if sport == 'Tenis':
                            secondary_category = secondary_category_original.split('-')[0]
                            for substring in ['ATP ', 'ITF ', 'WTA ']:
                                secondary_category = secondary_category.replace(substring, '')
                            secondary_category = secondary_category.strip()
                            secondary_category = ' '.join([word for word in secondary_category.split() if not re.search(r'\d', word)])
                        else:
                            secondary_category = secondary_category_original.lower().split('-')[0].split('.')[-1]
                            for substring in [' liga', 'extraliga', ' superliga', ' národní', ' pohár', ' ligový', ' cup', ' tipsport', ' chance', ' maxa', ' challenge']:
                                secondary_category = secondary_category.replace(substring, '')
                            secondary_category = secondary_category.strip()
                            secondary_category = ' '.join([word for word in secondary_category.split() if not re.search(r'\d', word)]) # primárně kvůli U21 atd.
                            if secondary_category[-1] in ['á', 'ý', 'é']:
                                secondary_category = secondary_category[:-1]
                        sport_detail_original = primary_category
                        basic_sport_event_item = BasicSportEventItem()
                        basic_sport_event_item['bookmaker_id'] = 'TS'
                        basic_sport_event_item['bookmaker_name'] = 'tipsport'
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
                        basic_sport_event_item['event_url'] = event_url
                        yield basic_sport_event_item