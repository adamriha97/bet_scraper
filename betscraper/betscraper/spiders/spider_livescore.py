import scrapy


class SpiderLivescoreSpider(scrapy.Spider):
    name = "spider_livescore"
    allowed_domains = ["www.livescore.cz"]
    start_urls = ["https://www.livescore.cz/others/"] # https://www.livescore.cz/

    custom_settings = {
        'FEEDS': {'data_livescore.json': {'format': 'json', 'overwrite': True}},
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        # 'CONCURRENT_REQUESTS': 32, # default 16
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 32, # default 8
        'DOWNLOAD_DELAY': 0,
        }

    def parse(self, response):
        for sport in (response.css('p.menu a') + response.css('ul.other-sports-menu a')):
            href = sport.css('::attr(href)').get()
            if href != '/others/':
                for day in range(8):
                    url = f"https://www.livescore.cz{href}?d={day}"
                    yield response.follow(url, callback = self.parse_sport, cb_kwargs=dict(sport_name = sport.css('::text').get(), day_number = day))
    
    def parse_sport(self, response, sport_name, day_number):
        yield {
            'sport': sport_name,
            'url': response.url,
            'day': day_number
        }
