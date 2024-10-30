# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BetscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def serialize_bet(value):
    return round(float(value), 2)

class BasicSportEventItem(scrapy.Item):
    bookmaker_id = scrapy.Field()
    bookmaker_name = scrapy.Field()
    sport_name = scrapy.Field()
    sport_name_original = scrapy.Field()
    sport_detail = scrapy.Field()
    sport_detail_original = scrapy.Field()
    country_name = scrapy.Field()
    country_name_original = scrapy.Field()
    primary_category = scrapy.Field()
    primary_category_original = scrapy.Field()
    secondary_category = scrapy.Field()
    secondary_category_original = scrapy.Field()
    event_startTime = scrapy.Field()
    participant_home = scrapy.Field()
    participant_away = scrapy.Field()
    participant_home_list = scrapy.Field()
    participant_away_list = scrapy.Field()
    participants_gender = scrapy.Field()
    participants_age = scrapy.Field()
    bet_1 = scrapy.Field(serializer = serialize_bet)
    bet_0 = scrapy.Field(serializer = serialize_bet)
    bet_2 = scrapy.Field(serializer = serialize_bet)
    bet_10 = scrapy.Field(serializer = serialize_bet)
    bet_02 = scrapy.Field(serializer = serialize_bet)
    bet_12 = scrapy.Field(serializer = serialize_bet)
    bet_11 = scrapy.Field(serializer = serialize_bet)
    bet_22 = scrapy.Field(serializer = serialize_bet)
    event_url = scrapy.Field()
