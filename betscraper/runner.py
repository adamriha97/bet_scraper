from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from betscraper.spiders import spider_betano, spider_betx, spider_forbet, spider_fortuna, spider_kingsbet, spider_merkur, spider_sazka, spider_synottip, spider_tipsport
# from betscraper.spiders import spider_livescore
from twisted.internet import asyncioreactor
asyncioreactor.install()
from twisted.internet import reactor
from twisted.internet import defer


settings = Settings()
settings.setmodule('betscraper.settings', priority='project')
runner = CrawlerRunner(settings)

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(spider_betano.SpiderBetanoSpider)
    reactor.stop()

crawl()
reactor.run()


# settings = Settings()
# settings.setmodule('betscraper.settings', priority='project')
# runner = CrawlerRunner(settings)

# runner.crawl(spider_betano.SpiderBetanoSpider)
# runner.crawl(spider_betx.SpiderBetxSpider)
# d = runner.join()

# d.addBoth(lambda _: reactor.stop())

# reactor.run()