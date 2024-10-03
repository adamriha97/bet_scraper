from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from betscraper.spiders import spider_betano, spider_betx, spider_forbet, spider_fortuna, spider_kingsbet, spider_merkur, spider_sazka, spider_synottip, spider_tipsport


settings = get_project_settings()
process = CrawlerProcess(settings)

process.crawl(spider_betano.SpiderBetanoSpider)
process.crawl(spider_betx.SpiderBetxSpider)
process.crawl(spider_forbet.SpiderForbetSpider)
process.crawl(spider_fortuna.SpiderFortunaSpider)
process.crawl(spider_kingsbet.SpiderKingsbetSpider)
process.crawl(spider_merkur.SpiderMerkurSpider)
process.crawl(spider_sazka.SpiderSazkaSpider)
process.crawl(spider_synottip.SpiderSynottipSpider)
process.crawl(spider_tipsport.SpiderTipsportSpider)

process.start()



# from twisted.internet import reactor, defer
# from scrapy.crawler import CrawlerRunner
# from scrapy.utils.log import configure_logging
# from scrapy.utils.project import get_project_settings
# from betscraper.spiders import spider_betano, spider_betx, spider_forbet, spider_fortuna, spider_kingsbet, spider_merkur, spider_sazka, spider_synottip, spider_tipsport


# settings = get_project_settings()
# configure_logging(settings)
# runner = CrawlerRunner(settings)

# @defer.inlineCallbacks
# def crawl():
#     yield runner.crawl(spider_betano.SpiderBetanoSpider)
#     yield runner.crawl(spider_betx.SpiderBetxSpider)
#     yield runner.crawl(spider_forbet.SpiderForbetSpider)
#     yield runner.crawl(spider_fortuna.SpiderFortunaSpider)
#     yield runner.crawl(spider_kingsbet.SpiderKingsbetSpider)
#     yield runner.crawl(spider_merkur.SpiderMerkurSpider)
#     yield runner.crawl(spider_sazka.SpiderSazkaSpider)
#     yield runner.crawl(spider_synottip.SpiderSynottipSpider)
#     yield runner.crawl(spider_tipsport.SpiderTipsportSpider)
#     reactor.stop()

# crawl()
# reactor.run()  # the script will block here until the last crawl call is finished



# from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings
# from betscraper.spiders import spider_betano, spider_betx, spider_forbet, spider_fortuna, spider_kingsbet, spider_merkur, spider_sazka, spider_synottip, spider_tipsport


# def crawl(spider):
#     process = CrawlerProcess(get_project_settings())
#     process.crawl(spider)
#     process.start()

# spiders = [
#     spider_betano.SpiderBetanoSpider,
#     spider_betx.SpiderBetxSpider,
#     spider_forbet.SpiderForbetSpider,
#     spider_fortuna.SpiderFortunaSpider,
#     spider_kingsbet.SpiderKingsbetSpider,
#     spider_merkur.SpiderMerkurSpider,
#     spider_sazka.SpiderSazkaSpider,
#     spider_synottip.SpiderSynottipSpider,
#     spider_tipsport.SpiderTipsportSpider
# ]

# for spider in spiders:
#     crawl(spider)
