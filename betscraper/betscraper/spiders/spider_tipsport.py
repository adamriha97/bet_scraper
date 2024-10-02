import scrapy
import json
from curl_cffi import requests
from datetime import datetime


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
                        # not a perfect solution because bet_0 can be locked or not available on the site but still relevant option
                        if (bet_0 == -1) and (not (bet_1 == bet_2 == -1)):
                            bet_11 = bet_1
                            bet_1 = -1
                            bet_22 = bet_2
                            bet_2 = -1
                        yield {
                            'sport': sport,
                            'event_url': event_url,
                            'event_startTime': event_startTime,
                            'participant_1': participant_1,
                            'participant_2': participant_2,
                            'bet_1': bet_1,
                            'bet_0': bet_0,
                            'bet_2': bet_2,
                            'bet_10': bet_10,
                            'bet_02': bet_02,
                            'bet_12': bet_12,
                            'bet_11': bet_11,
                            'bet_22': bet_22,
                        }