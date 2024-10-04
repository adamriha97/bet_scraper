import scrapy
import json
import datetime


class SpiderBetanoSpider(scrapy.Spider):
    name = "spider_betano"
    allowed_domains = ["www.betano.cz"]
    start_urls = ["https://www.betano.cz/api/"] # https://www.betano.cz

    custom_settings = {
        'FEEDS': {'data/data_betano.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'CONCURRENT_REQUESTS': 32, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32, # default 8
        }
    
    def parse(self, response):
        response_json = json.loads(response.text)
        not_interested = ['formule-1', 'zimni-sporty', 'zabava', 'cyklistika', 'golf', 'motorsport', 'surfing', 'speedway', 'politika']
        for sport in response_json["structureComponents"]["sports"]["data"]:
            if sport["url"].split('/')[2] not in not_interested:
                url = 'https://www.betano.cz/api' + sport["url"] + 'nadchazejici-zapasy-dnes/?sort=Leagues&req=la,s,stnf,c,mb'
                yield response.follow(url, callback = self.parse_sport)

    def parse_sport(self, response):
        response_json = json.loads(response.text)
        try:
            if response_json["errorCode"] == 301:
                pass
        except:
            sport = response.url.split('/')[5]
            for league in response_json["data"]["blocks"]:
                for event in league["events"]:
                    event_url = f'https://www.betano.cz{event["url"]}'
                    event_startTime = datetime.datetime.fromtimestamp(event["startTime"]/1000)
                    participant_1 = event["participants"][0]["name"]
                    participant_2 = event["participants"][1]["name"]
                    bet_1 = bet_0 = bet_2 = bet_10 = bet_02 = bet_12 = bet_11 = bet_22 = -1
                    for market in event['markets']:
                        if market["name"].startswith(("Výsledek", "Vítěz")):
                            for selection in market["selections"]:
                                if selection["name"] == '0':
                                    bet_0 = selection["price"]
                                elif selection["name"] in ['1', participant_1]:
                                    bet_1 = selection["price"]
                                elif selection["name"] in ['2', participant_2]:
                                    bet_2 = selection["price"]
                    # not a perfect solution because bet_0 can be locked or not available on the site but still relevant option
                    if (bet_0 == -1) and (not (bet_1 == bet_2 == -1)):
                        bet_11 = bet_1
                        bet_1 = -1
                        bet_22 = bet_2
                        bet_2 = -1
                    if not (bet_1 == bet_0 == bet_2 == bet_10 == bet_02 == bet_12 == bet_11 == bet_22 == -1):
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