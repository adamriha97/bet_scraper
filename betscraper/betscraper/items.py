# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BetscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class BasicSportEventItem(scrapy.Item):
    bookmaker_id = scrapy.Field()
    bookmaker_name = scrapy.Field()
    sport_name = scrapy.Field()
    sport_name_original = scrapy.Field()
    country_name = scrapy.Field()
    primary_category_original = scrapy.Field()
    secondary_category_original = scrapy.Field()
    event_startTime = scrapy.Field()
    participant_home = scrapy.Field()
    participant_away = scrapy.Field()
    participants_gender = scrapy.Field()
    participants_age = scrapy.Field()
    bet_1 = scrapy.Field()
    bet_0 = scrapy.Field()
    bet_2 = scrapy.Field()
    bet_10 = scrapy.Field()
    bet_02 = scrapy.Field()
    bet_12 = scrapy.Field()
    bet_11 = scrapy.Field()
    bet_22 = scrapy.Field()
    event_url = scrapy.Field()
