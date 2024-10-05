from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from betscraper.spiders import spider_betano, spider_betx, spider_forbet, spider_fortuna, spider_kingsbet, spider_merkur, spider_sazka, spider_synottip, spider_tipsport
# from betscraper.spiders import spider_livescore


settings = Settings()
settings.setmodule('betscraper.settings', priority='project')
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
# process.crawl(spider_livescore.SpiderLivescoreSpider)

process.start()
