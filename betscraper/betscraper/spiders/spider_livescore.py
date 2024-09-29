import scrapy
from datetime import datetime
import pytz


class SpiderLivescoreSpider(scrapy.Spider):
    name = "spider_livescore"
    allowed_domains = ["www.livescore.cz"]
    start_urls = ["https://www.livescore.cz/others/"] # https://www.livescore.cz/

    custom_settings = {
        'FEEDS': {'data_livescore.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'CONCURRENT_REQUESTS': 256, # default 16
        'CONCURRENT_REQUESTS_PER_DOMAIN': 256, # default 8
        'DOWNLOAD_DELAY': 0,
        }

    def parse(self, response):
        for sport in (response.css('p.menu a') + response.css('ul.other-sports-menu a')):
            href = sport.css('::attr(href)').get()
            if href != '/others/':
                for day in range(8):
                    url = f"https://www.livescore.cz{href}?d={day}"
                    yield response.follow(
                        url, 
                        callback = self.parse_sport, 
                        cb_kwargs=dict(sport_name = sport.css('::text').get(), day_number = day)
                    )
    
    def parse_sport(self, response, sport_name, day_number):
        full_leagues = response.css('div#score-data h4::text').getall()
        for match in response.css('div#score-data a.sched'):
            number_of_leagues_after = len(match.css('a ~ h4'))
            full_league = full_leagues[-1-number_of_leagues_after]
            url = f"https://www.livescore.cz{match.css('::attr(href)').get()}"
            yield response.follow(
                url, 
                callback = self.parse_match, 
                cb_kwargs=dict(sport_name = sport_name, day_number = day_number, full_league = full_league)
            )

    def parse_match(self, response, sport_name, day_number, full_league):
        sport = sport_name
        event_url = response.url
        country = full_league.split(': ')[0]
        league_detail = full_league.split(': ')[1].split(' - ')
        league = league_detail[0]
        participants = response.css('h3 a.web-link-external ::text').getall()
        participant_1 = participants[0]
        participant_2 = participants[1]
        participants_url = response.css('h3 a.web-link-external ::attr(href)').getall()
        participant_1_url = participants_url[0]
        participant_2_url = participants_url[1]
        date_str = response.css('div.detail ::text').get()
        date_format = "%d.%m.%Y %H:%M"
        date_obj = datetime.strptime(date_str, date_format)
        event_startTime = pytz.timezone('Europe/Prague').localize(date_obj)
        yield {
            'sport': sport,
            'event_url': event_url,
            'country': country,
            'league': league,
            'league_detail': league_detail,
            'participant_1': participant_1,
            'participant_1_url': participant_1_url,
            'participant_2': participant_2,
            'participant_2_url': participant_2_url,
            'event_startTime': event_startTime,
        }
