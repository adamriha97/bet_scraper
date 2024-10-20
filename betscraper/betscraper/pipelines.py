# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

import os
import json


class BetscraperPipeline:
    def process_item(self, item, spider):
        return item
    
class UnifySportNamesPipeline:
    def __init__(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        sports_dict_path = os.path.join(script_dir, 'files/sports_dict.json')
        with open(sports_dict_path, 'r') as file:
            self.translator = json.load(file)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        bookmaker_name = adapter.get('bookmaker_name')
        sport_name_original = adapter.get('sport_name_original')
        for translator_sport_name, translator_original_list in self.translator[bookmaker_name].items():
            if sport_name_original in translator_original_list:
                adapter['sport_name'] = translator_sport_name
                break
        if adapter.get('sport_name') == '':
            adapter['sport_name'] = 'other'
        return item

class UnifyCountryNamesPipeline:
    def __init__(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        countries_dict_path = os.path.join(script_dir, 'files/countries_dict.json')
        with open(countries_dict_path, 'r') as file:
            self.translator = json.load(file)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        bookmaker_name = adapter.get('bookmaker_name')
        country_name_original = adapter.get('primary_category')
        for translator_country_name, translator_original_list in self.translator[bookmaker_name].items():
            if country_name_original in translator_original_list:
                adapter['country_name'] = translator_country_name
                adapter['country_name_original'] = country_name_original
                break
        if adapter.get('country_name') == '':
            country_name_original = adapter.get('secondary_category')
            for translator_country_name, translator_original_list in self.translator[bookmaker_name].items():
                if country_name_original in translator_original_list:
                    adapter['country_name'] = translator_country_name
                    adapter['country_name_original'] = country_name_original
                    break
        if adapter.get('country_name') == '':
            adapter['country_name'] = 'other'
            adapter['country_name_original'] = 'other'
        return item

class DropDuplicatesPipeline:
    def __init__(self):
        self.items_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        item_tuple = tuple(adapter.asdict().values())
        if item_tuple in self.items_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.items_seen.add(item_tuple)
            return item

class UpdateNonDrawBetsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # not a perfect solution because bet_0 can be locked or not available on the site but still relevant option
        if (adapter.get('bet_0') == -1) and (not (adapter.get('bet_1') == adapter.get('bet_2') == -1)):
            adapter['bet_11'] = adapter.get('bet_1')
            adapter['bet_1'] = -1
            adapter['bet_22'] = adapter.get('bet_2')
            adapter['bet_2'] = -1
        return item
