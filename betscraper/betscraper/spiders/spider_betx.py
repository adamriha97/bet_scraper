import scrapy
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from unidecode import unidecode
import re

from betscraper.items import BasicSportEventItem


class SpiderBetxSpider(scrapy.Spider):
    name = "spider_betx"
    allowed_domains = ["bet-x.cz", 'sportapis-cz.betx.bet']
    # start_urls = ["https://sportapis-cz.betx.bet/SportsOfferApi/api/sport/offer/v3/sports/offer?Limit=9999"] # https://bet-x.cz/cs/sports-betting

    custom_settings = {
        'FEEDS': {'data/data_betx.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'ITEM_PIPELINES': {
            "betscraper.pipelines.UnifySportNamesPipeline": 400,
            "betscraper.pipelines.UnifyCountryNamesPipeline": 410,
            "betscraper.pipelines.UpdateNonDrawBetsPipeline": 500,
        },
        }
    
    def start_requests(self):
        url = "https://sportapis-cz.betx.bet/SportsOfferApi/api/sport/offer/v3/sports/offer?Limit=9999"
        headers = {
            'Accept-Language': 'cs',
            # 'LanguageId': 'cs',
        }
        yield scrapy.Request(url, method = 'GET', headers = headers, callback = self.parse)

    def parse(self, response):
        response_json = json.loads(response.text)
        not_interested = ['BETX Superšance', 'Superchance', 'Cycling', 'BetX Chance', 'Horse Racing']
        for section in response_json['Response']:
            sport = section['OriginName'] # used to be Name, but changed to OriginName so I do not need to change sports_dict from en to cs
            if sport not in not_interested:
                for category in section['Categories']:
                    primary_category_original = category['Name']
                    for league in category['Leagues']:
                        secondary_category_original = league['Name']
                        for match in league['Matches']:
                            try:
                                event_url = f'https://bet-x.cz/cs/sports-betting/offer/{unidecode(sport.lower().replace(" ", "-"))}?match={str(match["Id"])}'
                                event_startTime = datetime.fromisoformat(match['MatchStartTime'].replace("Z", "+00:00")).replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo('Europe/Prague'))
                                participant_1 = match['TeamHome']
                                participant_2 = match['TeamAway']
                                participants_gender = ''
                                if any('ženy' in string for string in [primary_category_original, secondary_category_original]):
                                    participants_gender = 'zeny'
                                elif any('muži' in string for string in [primary_category_original, secondary_category_original]):
                                    participants_gender = 'muzi'
                                participants_age = ''
                                hasAge = re.search(r'U\d{2}', secondary_category_original)
                                if hasAge:
                                    participants_age = hasAge.group(0)
                                bet_1 = bet_0 = bet_2 = bet_10 = bet_02 = bet_12 = bet_11 = bet_22 = -1
                                for bet in match['BasicOffer']['Odds']:
                                    if bet["Name"] == '1':
                                        bet_1 = bet["Odd"]
                                    elif bet["Name"] == 'X':
                                        bet_0 = bet["Odd"]
                                    elif bet["Name"] == '2':
                                        bet_2 = bet["Odd"]
                                    elif bet["Name"] == '1X':
                                        bet_10 = bet["Odd"]
                                    elif bet["Name"] == 'X2':
                                        bet_02 = bet["Odd"]
                                    elif bet["Name"] == '12':
                                        bet_12 = bet["Odd"]
                                primary_category = primary_category_original.replace(' Amatéři', '').replace(' mládežnické', '').replace(' klubové', '')
                                secondary_category = secondary_category_original.replace(' 4-hra', '').split(' - ')[0].replace(' tvrdý povrch', '')
                                if (not (bet_1 == bet_0 == bet_2 == bet_10 == bet_02 == bet_12 == bet_11 == bet_22 == -1)) and (participant_2 != None):
                                    basic_sport_event_item = BasicSportEventItem()
                                    basic_sport_event_item['bookmaker_id'] = 'BX'
                                    basic_sport_event_item['bookmaker_name'] = 'betx'
                                    basic_sport_event_item['sport_name'] = ''
                                    basic_sport_event_item['sport_name_original'] = sport
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
                            except:
                                pass
