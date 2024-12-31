from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from betscraper.spiders import spider_betano, spider_betx, spider_forbet, spider_fortuna, spider_kingsbet, spider_merkur, spider_sazka, spider_synottip, spider_tipsport
from betscraper.spiders import spider_betano_detail, spider_betx_detail, spider_forbet_detail, spider_fortuna_detail, spider_kingsbet_detail, spider_merkur_detail, spider_sazka_detail, spider_synottip_detail, spider_tipsport_detail
# from betscraper.spiders import spider_livescore
import json

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

# from twisted.internet.asyncioreactor import AsyncioSelectorReactor as reactor

# from scrapy.utils.reactor import install_reactor

# install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")

from twisted.internet import asyncioreactor
asyncioreactor.install()
from twisted.internet import reactor

settings = Settings()
settings.setmodule('betscraper.settings', priority='project')
# process = CrawlerProcess(settings)

runner = CrawlerRunner(settings)
runner.crawl(spider_betano.SpiderBetanoSpider)
runner.crawl(spider_betx.SpiderBetxSpider)
d = runner.join()

d.addBoth(lambda _: reactor.stop())

reactor.run()  # the script will block here until all crawling jobs are finished