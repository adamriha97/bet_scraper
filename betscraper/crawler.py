from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from betscraper.spiders import spider_betano, spider_betx, spider_forbet, spider_fortuna, spider_kingsbet, spider_merkur, spider_sazka, spider_synottip, spider_tipsport


process = CrawlerProcess(get_project_settings())

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