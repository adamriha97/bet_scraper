import scrapy
import json


class SpiderSazkaSpider(scrapy.Spider):
    name = "spider_sazka"
    allowed_domains = ["www.sazka.cz"]
    start_urls = ["https://sg-content-engage-prod.sazka.cz/content-service/api/v1/q/drilldown-tree?drilldownNodeIds=2&eventState=OPEN_EVENT"] # https://www.sazka.cz/kurzove-sazky/

    custom_settings = {
        'FEEDS': {'data_sazka.json': {'format': 'json', 'overwrite': True}},
        'DOWNLOADER_MIDDLEWARES': {
            'betscraper.middlewares.ScrapeOpsFakeUserAgentMiddleware': 400,
            'betscraper.middlewares.ScrapeOpsFakeBrowserHeaderAgentMiddleware': 300,
            'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550, 
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None, 
        }
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
            yield {
                'name': name,
                'id_value': id_value,
            }
