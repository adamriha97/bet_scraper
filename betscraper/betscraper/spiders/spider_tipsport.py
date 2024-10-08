import scrapy
import json
from curl_cffi import requests
from datetime import datetime

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
            "betscraper.pipelines.UnifySportNamesPipeline": 400,
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
                for match_item in competition_item['matches']:
                    if match_item['matchType'] == 'MATCH':
                        sport = match_item['nameSuperSport']
                        event_url = f"https://www.tipsport.cz{match_item['matchUrl']}"
                        event_startTime = datetime.fromisoformat(match_item['datetimeClosed'])
                        participant_1 = match_item['participantHome']
                        participant_2 = match_item['participantVisiting']
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
                        basic_sport_event_item = BasicSportEventItem()
                        basic_sport_event_item['bookmaker_id'] = 'TS'
                        basic_sport_event_item['bookmaker_name'] = 'tipsport'
                        basic_sport_event_item['sport_name'] = ''
                        basic_sport_event_item['sport_name_original'] = sport
                        basic_sport_event_item['event_url'] = event_url
                        basic_sport_event_item['event_startTime'] = event_startTime
                        basic_sport_event_item['participant_home'] = participant_1
                        basic_sport_event_item['participant_away'] = participant_2
                        basic_sport_event_item['bet_1'] = bet_1
                        basic_sport_event_item['bet_0'] = bet_0
                        basic_sport_event_item['bet_2'] = bet_2
                        basic_sport_event_item['bet_10'] = bet_10
                        basic_sport_event_item['bet_02'] = bet_02
                        basic_sport_event_item['bet_12'] = bet_12
                        basic_sport_event_item['bet_11'] = bet_11
                        basic_sport_event_item['bet_22'] = bet_22
                        yield basic_sport_event_item