# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import os
import json


class BetscraperPipeline:
    def process_item(self, item, spider):
        return item
    
class UnifySportNamesPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        sports_dict_path = os.path.join(script_dir, 'files/sports_dict.json')
        with open(sports_dict_path, 'r') as file:
            translator = json.load(file)
        
        bookmaker_name = adapter.get('bookmaker_name')
        sport_name_original = adapter.get('sport_name_original')
        for translator_sport_name, translator_original_list in translator[bookmaker_name].items():
            if sport_name_original in translator_original_list:
                adapter['sport_name'] = translator_sport_name
                break
        if adapter.get('sport_name') == '':
            adapter['sport_name'] = 'other'
        return item
