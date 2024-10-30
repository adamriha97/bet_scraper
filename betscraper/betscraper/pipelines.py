# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

import os
import json
from unidecode import unidecode


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
            self.translator_reverse = json.load(file)
        self.translator = {}
        for translator_country_name, translator_original_list in self.translator_reverse.items():
            for list_item in translator_original_list:
                self.translator[list_item] = translator_country_name

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        try:
            adapter['country_name'] = self.translator[adapter.get('primary_category')]
            adapter['country_name_original'] = adapter.get('primary_category')
        except:
            try:
                adapter['country_name'] = self.translator[adapter.get('secondary_category')]
                adapter['country_name_original'] = adapter.get('secondary_category')
            except:
                adapter['country_name'] = 'other'
                adapter['country_name_original'] = 'other'
        return item

class UnifySportDetailsPipeline:
    def __init__(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        sports_detail_dict_path = os.path.join(script_dir, 'files/sports_detail_dict.json')
        with open(sports_detail_dict_path, 'r') as file:
            self.translator_reverse = json.load(file)
        self.translator = {}
        for translator_sport_detail_name, translator_original_list in self.translator_reverse.items():
            for list_item in translator_original_list:
                self.translator[list_item] = translator_sport_detail_name

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        try:
            adapter['sport_detail'] = self.translator[adapter.get('sport_detail_original')]
        except:
            adapter['sport_detail'] = 'other'
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

class PopulateParticipantListsPipeline:
    def create_tuple(self, participant, bookmaker_name = 'default'):
        if ',' in participant: # kdyz carka, tak prohod
            parts = participant.split(',', 1)
            participant = parts[1] + parts[0]
        participant = participant.replace('.', ' ') # vymen tecky za mezery
        participant = " ".join(word for word in participant.split() if len(word) > 1) # odstran jednopismenna slova
        if bookmaker_name == 'tipsport': # kdyz tipsport (ne u dvouher), tak odstran posledni slovo
            participant = " ".join(participant.split()[:-1])
        participant = participant.replace('-', ' ').replace("'", " ") # vymen pomlcky a apostrofy za mezery
        participant = unidecode(participant.lower()) # asi na libovolne urovni dat na lower a bez diakritiky
        if bookmaker_name == 'tipsport': # kdyz tipsport, vem vsechny slova, jinak vem posledni slovo
            return tuple(participant.split())
        else:
            return (participant.split()[-1],)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        bookmaker_name = adapter.get('bookmaker_name')
        sport_name = adapter.get('sport_name')
        participant_home = adapter.get('participant_home')
        participant_away = adapter.get('participant_away')
        participants = {'home': participant_home, 'away': participant_away}
        for participant_status, participant_name in participants.items():
            if sport_name in ['tenis', 'stolni-tenis', 'sipky', 'box', 'bojove-sporty', 'snooker', 'padel', 'badminton', 'squash', 'sachy']: # sports with people
                if '/' in participant_name: # people, doubles
                    participant_members = participant_name.split('/', 1)
                    member_1 = self.create_tuple(participant = participant_members[0])[0]
                    member_2 = self.create_tuple(participant = participant_members[1])[0]
                    adapter[f'participant_{participant_status}_list'] = (member_1 + member_2, member_2 + member_1)
                else: # people, singles
                    adapter[f'participant_{participant_status}_list'] = self.create_tuple(participant = participant_name, bookmaker_name = bookmaker_name)
            else: # sports with teams
                pass
        return item
