import scrapy
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from betscraper.items import BasicSportEventItem


class SpiderForbetSpider(scrapy.Spider):
    name = "spider_forbet"
    allowed_domains = ["www.iforbet.cz"]
    # start_urls = ["https://www.iforbet.cz"]

    custom_settings = {
        'FEEDS': {'data/data_forbet.json': {'format': 'json', 'overwrite': True}},
        'ITEM_PIPELINES': {
            "betscraper.pipelines.UnifySportNamesPipeline": 400,
            "betscraper.pipelines.UpdateNonDrawBetsPipeline": 500,
        },
        }
    
    def start_requests(self):
        url = 'https://www.iforbet.cz/api/web/v1/offer/full_offer'
        body = json.dumps({
            "offerMode": "prematch",
            "lang": "cs"
        })
        headers = {
            'Content-Type': 'application/json'
        }
        yield scrapy.Request(url=url, headers=headers, body=body, method="POST", callback = self.parse)

    def parse(self, response):
        response_json = json.loads(response.text)
        first_market_ids = set()
        for sport_market_list in response_json['data']['market_list'].values():
            first_market_id = next(iter(sport_market_list))
            first_market_ids.add(first_market_id)
        for market in response_json['data']['markets'].values():
            if str(market['marketId']) in first_market_ids:
                event_json = response_json['data']['event'][market['eventId']]
                tournament_json = response_json['data']['tournament'][event_json['tournamentId']]
                category_json = response_json['data']['category'][str(tournament_json['categoryId'])]
                sport_json = response_json['data']['sport'][str(category_json['sportId'])]
                if str(market['marketId']) == next(iter(response_json['data']['market_list'][str(category_json['sportId'])])):
                    sport = sport_json['name']
                    event_url = f'https://www.iforbet.cz/prematch/event/{market["eventId"]}'
                    event_startTime = datetime.fromisoformat(event_json['startTs'].replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Prague"))
                    participant_1 = response_json['data']['competitors'][str(event_json['competitors'][0])]['name']
                    participant_2 = response_json['data']['competitors'][str(event_json['competitors'][1])]['name']
                    # odds_dict = {} # maybe useless
                    odds_list = []
                    for odd in market['odds'].values():
                        # odds_dict[odd['outcomeId']] = odd['odds'] # maybe useless
                        odds_list.append(odd['odds'])
                    bet_1 = bet_0 = bet_2 = bet_10 = bet_02 = bet_12 = bet_11 = bet_22 = -1
                    if len(odds_list) == 2:
                        bet_1 = odds_list[0]
                        bet_2 = odds_list[1]
                    elif len(odds_list) == 6:
                        bet_1 = odds_list[3]
                        bet_0 = odds_list[4]
                        bet_2 = odds_list[5]
                        bet_10 = odds_list[0]
                        bet_12 = odds_list[1]
                        bet_02 = odds_list[2]
                    elif len(odds_list) == 3: # only future proof, now useless
                        bet_1 = odds_list[0]
                        bet_0 = odds_list[1]
                        bet_2 = odds_list[2]
                    basic_sport_event_item = BasicSportEventItem()
                    basic_sport_event_item['bookmaker_id'] = 'FB'
                    basic_sport_event_item['bookmaker_name'] = 'forbet'
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