import scrapy
import json
from scrapy_splash import SplashRequest


lua_script = """
function main(splash, args)  
  splash:go(args.url)

  -- custom rendering script logic...
  
  return splash:html()
end
"""

class SpiderBetanoSpider(scrapy.Spider):
    name = "spider_betano"
    allowed_domains = ["www.betano.cz", "localhost"]
    start_urls = ["https://www.betano.cz/api/"] # "https://www.betano.cz"

    custom_settings = {
        'FEEDS': {'data_betano.json': {'format': 'json', 'overwrite': True}}
        }

    def parse(self, response):
        resp_js = json.loads(response.text)
        for sport in resp_js["structureComponents"]["sports"]["data"]:
            url = 'https://www.betano.cz' + sport["url"] + 'nadchazejici-zapasy-dnes/?sort=StartTime'
            #yield {
            #    'origin-url': url
            #}
            yield SplashRequest(url, callback=self.parse_sport_page, args={"wait": 5}) 
        #url = 'https://www.betano.cz' + resp_js["structureComponents"]["sports"]["data"][0]["url"] + 'nadchazejici-zapasy-dnes/?sort=StartTime'
        #yield response.follow(url, callback = self.parse_sport_page)
        #yield scrapy.Request(url, meta={"playwright": True})
        #yield SplashRequest(url, callback=self.parse_sport_page, endpoint="execute", args={"lua_source": lua_script})
        #yield SplashRequest(url, callback=self.parse_sport_page, args={"wait": 15}) 

    def parse_sport_page(self, response):
        yield {
            'url': response.url,
            'text': response.css('h1').get()
        }