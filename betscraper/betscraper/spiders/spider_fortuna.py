import scrapy
import datetime


class SpiderFortunaSpider(scrapy.Spider):
    name = "spider_fortuna"
    allowed_domains = ["www.ifortuna.cz"]
    start_urls = ["https://www.ifortuna.cz/"]

    custom_settings = {
        'FEEDS': {'data_fortuna.json': {'format': 'json', 'overwrite': True}},
        'DOWNLOADER_MIDDLEWARES': {
            'betscraper.middlewares.ScrapeOpsFakeUserAgentMiddleware': 400,
            'betscraper.middlewares.ScrapeOpsFakeBrowserHeaderAgentMiddleware': 300,
            'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550, 
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None, 
        }
        }

    def parse(self, response):
        links = response.css('ul#filterbox-ref-sport-tree li a.btn-sport ::attr(href)').getall()
        sports = [link.split('/')[2].split('?')[0].split('-202')[0] for link in links]
        not_interested = ['hotovky', 'favorit-plus', 'fotbal-special', 'tenis-special', 'cyklistika', 'dostihy', 'f1', 'finance', 'golf', 'motorismus', 'politika', 'stane-se-v-roce', 'zabava']
        for sport in sports:
            if sport not in not_interested:
                url = 'https://www.ifortuna.cz/bets/ajax/loadmoresport/' + sport + '?timeTo=&rateFrom=&rateTo=&date=&pageSize=100&page=0'
        #url = 'https://www.ifortuna.cz/bets/ajax/loadmoresport/fotbal?timeTo=&rateFrom=&rateTo=&date=&pageSize=100&page=0'
                yield response.follow(url, callback = self.parse_sport)
    
    def parse_sport(self, response):
        continue_parse = False
        sport = response.url.split('/')[-1].split('?')[0]
        for table in response.css('table.events-table'):
            for event in table.css('tbody tr'):
                try:
                    event_url = event.css('a.event-link ::attr(href)').get()
                    event_startTime = datetime.datetime.fromtimestamp(int(event.css('td.col-date ::attr(data-value)').get())/1000)
                    participants = event.css('div.title-container div.event-name span ::text').get().replace('\n', '').split(' - ')
                    participant_1 = participants[0]
                    participant_2 = participants[1]
                    bet_1 = bet_0 = bet_2 = -1
                    bets = event.css('span.odds-value ::text').getall()
                    if len(bets) == 2:
                        bet_1 = bets[0]
                        bet_2 = bets[1]
                    elif len(bets) == 3:
                        bet_1 = bets[0]
                        bet_0 = bets[1]
                        bet_2 = bets[2]
                    yield {
                        'sport': sport,
                        'event_url': event_url,
                        'event_startTime': event_startTime,
                        'participant_1': participant_1,
                        'participant_2': participant_2,
                        'bet_1': bet_1,
                        'bet_0': bet_0,
                        'bet_2': bet_2
                    }
                    continue_parse = True
                except:
                    pass
        if continue_parse:
            parts_url = response.url.split('=')
            parts_url[-1] = str(int(parts_url[-1]) + 1)
            next_url = '='.join(parts_url)
            yield response.follow(next_url, callback = self.parse_sport)