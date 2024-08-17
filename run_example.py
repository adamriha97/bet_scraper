from scrapy import cmdline
from datetime import datetime
import os


def start_crawl():
    os.chdir("/Users/arsalanamin/hustle/github/scrapy_infinite_scroll")
    try:
        print(f"======SCRAPPED AT {datetime.now()}========")

        # EXECUTE COMMAND
        cmdline.execute("scrapy crawl quotes --output data.json".split())
    except Exception as e:
        print(f"==========Exception: {e}")


start_crawl()