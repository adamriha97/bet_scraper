from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from betscraper.spiders import spider_betano_detail, spider_betx_detail, spider_forbet_detail, spider_fortuna_detail, spider_kingsbet_detail, spider_merkur_detail, spider_sazka_detail, spider_synottip_detail, spider_tipsport_detail
# from betscraper.spiders import spider_livescore
import json
import sys


spider_to_run = sys.argv[1]

settings = Settings()
settings.setmodule('betscraper.settings', priority='project')
process = CrawlerProcess(settings)

with open('betscraper/data/lists_for_detail_spiders_dict.json', 'r') as json_file:
    lists_for_detail_spiders_dict = json.load(json_file)

if spider_to_run in ('forbet', 'all'):
    if 'forbet' in lists_for_detail_spiders_dict.keys():
        process.crawl(spider_forbet_detail.SpiderForbetDetailSpider, arg_data = lists_for_detail_spiders_dict['forbet']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://www.fbet.cz/prematch/event/MA50936435')
if spider_to_run in ('tipsport', 'all'):
    if 'tipsport' in lists_for_detail_spiders_dict.keys():
        process.crawl(spider_tipsport_detail.SpiderTipsportDetailSpider, arg_data = lists_for_detail_spiders_dict['tipsport']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://www.tipsport.cz/kurzy/zapas/fotbal-teplice-slavia-praha/6215185')
if spider_to_run in ('rest', 'all'):
    if 'betano' in lists_for_detail_spiders_dict.keys():
        process.crawl(spider_betano_detail.SpiderBetanoDetailSpider, arg_data = lists_for_detail_spiders_dict['betano']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://www.betano.cz/zapas-sance/teplice-sk-slavia-praha/58204893/')
    if 'betx' in lists_for_detail_spiders_dict.keys():
        process.crawl(spider_betx_detail.SpiderBetxDetailSpider, arg_data = lists_for_detail_spiders_dict['betx']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://bet-x.cz/cs/sports-betting/offer/soccer?match=50936435')
    if 'fortuna' in lists_for_detail_spiders_dict.keys():
        process.crawl(spider_fortuna_detail.SpiderFortunaDetailSpider, arg_data = lists_for_detail_spiders_dict['fortuna']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://www.ifortuna.cz/sazeni/fotbal/1-cesko/teplice-slavia-praha-MCZ149614999')
    if 'kingsbet' in lists_for_detail_spiders_dict.keys():
        process.crawl(spider_kingsbet_detail.SpiderKingsbetDetailSpider, arg_data = lists_for_detail_spiders_dict['kingsbet']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://www.kingsbet.cz/sport?page=event&eventId=10301025')
    if 'merkur' in lists_for_detail_spiders_dict.keys():
        process.crawl(spider_merkur_detail.SpiderMerkurDetailSpider, arg_data = lists_for_detail_spiders_dict['merkur']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://www.merkurxtip.cz/sazeni/online/fotbal/S/1-liga/2334015/special/teplice-v-slavia-prague/130050705')
    if 'sazka' in lists_for_detail_spiders_dict.keys():
        process.crawl(spider_sazka_detail.SpiderSazkaDetailSpider, arg_data = lists_for_detail_spiders_dict['sazka']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://www.sazka.cz/kurzove-sazky/sports/event/1818260')
    if 'synottip' in lists_for_detail_spiders_dict.keys():
        process.crawl(spider_synottip_detail.SpiderSynottipDetailSpider, arg_data = lists_for_detail_spiders_dict['synottip']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://sport.synottip.cz/zapasy/12cx13cxx27/2416017cxx27/241943424?categoryId=12cx13cxx27')

process.start()
