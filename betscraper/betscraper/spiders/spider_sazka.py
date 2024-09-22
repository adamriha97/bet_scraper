import scrapy
import json
from datetime import datetime
from zoneinfo import ZoneInfo


class SpiderSazkaSpider(scrapy.Spider):
    name = "spider_sazka"
    allowed_domains = ["www.sazka.cz", "sg-content-engage-prod.sazka.cz"]
    start_urls = ["https://sg-content-engage-prod.sazka.cz/content-service/api/v1/q/drilldown-tree?drilldownNodeIds=2&eventState=OPEN_EVENT"] # https://www.sazka.cz/kurzove-sazky/

    custom_settings = {
        'FEEDS': {'data_sazka.json': {'format': 'json', 'overwrite': True}},
        'CONCURRENT_REQUESTS': 64, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 64, # default 8
        'DOWNLOAD_DELAY': 0,
        'DOWNLOADER_MIDDLEWARES': {
            'betscraper.middlewares.ScrapeOpsFakeUserAgentMiddleware': 400,
            'betscraper.middlewares.ScrapeOpsFakeBrowserHeaderAgentMiddleware': 300,
            'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550, 
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None, 
        },
        }

    def parse(self, response):
        response_json = json.loads(response.text)
        # Soccer je v not_interested, jelikoz pro nej bereme vsechny kategorie zvlast - najednou je to moc zapasu a api GET call vraci error
        not_interested = ['Soccer', 'Sazka Specials', 'Cycling', 'Formula 1', 'Golf', 'Motor Racing', 'Politics', 'Alpine Skiing', 'Biathlon', 'Ski Jumping']
        sports_dict = {node["name"]: node["id"] for node in response_json["data"]["drilldownNodes"][0]["drilldownNodes"] if node["name"] not in not_interested}
        soccer_node = None
        for node in response_json["data"]["drilldownNodes"][0]["drilldownNodes"]:
            if node["name"] == "Soccer":
                soccer_node = node
                break
        soccer_competitions_dict = {}
        if soccer_node:
            soccer_competitions_dict = {node["name"]: node["id"] for node in soccer_node["drilldownNodes"]}
        ids_for_urls_dict = {**sports_dict, **soccer_competitions_dict}
        for name, id_value in ids_for_urls_dict.items():
            url = f'https://sg-content-engage-prod.sazka.cz/content-service/api/v1/q/time-band-event-list?maxMarkets=1&marketSortsIncluded=--%2CCS%2CDC%2CDN%2CHH%2CHL%2CMH%2CMR%2CWH&marketGroupTypesIncluded=CUSTOM_GROUP%2CMONEYLINE%2CROLLING_SPREAD%2CROLLING_TOTAL%2CSTATIC_SPREAD%2CSTATIC_TOTAL&allowedEventSorts=MTCH&includeChildMarkets=true&prioritisePrimaryMarkets=true&drilldownTagIds={id_value}&maxTotalItems=1000&maxEventsPerCompetition=30&maxCompetitionsPerSportPerBand=1000'
            yield response.follow(url, callback = self.parse_sport)

    def parse_sport(self, response):
        response_json = json.loads(response.text)
        for time_band in response_json['data']['timeBandEvents']:
            for event in time_band['events']:
                try:
                    sport = event['category']['name']
                    event_url = f'https://www.sazka.cz/kurzove-sazky/sports/event/{event["id"]}'
                    event_startTime = datetime.fromisoformat(event['startTime'].replace("Z", "+00:00")).replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo('Europe/Prague'))
                    participant_1 = event['teams'][0]['name']
                    participant_2 = event['teams'][1]['name']
                    bet_1 = bet_0 = bet_2 = bet_10 = bet_02 = bet_12 = bet_11 = bet_22 = -1
                    for bet in event['markets'][0]['outcomes']:
                        if bet["name"] == participant_1:
                            bet_1 = bet['prices'][0]['decimal']
                        elif bet["name"] == participant_2:
                            bet_2 = bet['prices'][0]['decimal']
                        elif bet["name"] == 'Draw':
                            bet_0 = bet['prices'][0]['decimal']
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
                except:
                    continue