import subprocess
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from betscraper.spiders import spider_betano, spider_betx, spider_forbet, spider_fortuna, spider_kingsbet, spider_merkur, spider_sazka, spider_synottip, spider_tipsport

import json
import pandas as pd
from datetime import datetime, timedelta
import os

from betscraper.spiders import spider_betano_detail, spider_betx_detail, spider_forbet_detail, spider_fortuna_detail, spider_kingsbet_detail, spider_merkur_detail, spider_sazka_detail, spider_synottip_detail, spider_tipsport_detail

import numpy as np


# FUNCTIONS
def crawler_func(bookmaker_names):
    settings = Settings()
    settings.setmodule('betscraper.settings', priority='project')
    process = CrawlerProcess(settings)

    if 'betano' in bookmaker_names:
        process.crawl(spider_betano.SpiderBetanoSpider)
    if 'betx' in bookmaker_names:
        process.crawl(spider_betx.SpiderBetxSpider)
    if 'forbet' in bookmaker_names:
        process.crawl(spider_forbet.SpiderForbetSpider)
    if 'fortuna' in bookmaker_names:
        process.crawl(spider_fortuna.SpiderFortunaSpider)
    if 'kingsbet' in bookmaker_names:
        process.crawl(spider_kingsbet.SpiderKingsbetSpider)
    if 'merkur' in bookmaker_names:
        process.crawl(spider_merkur.SpiderMerkurSpider)
    if 'sazka' in bookmaker_names:
        process.crawl(spider_sazka.SpiderSazkaSpider)
    if 'synottip' in bookmaker_names:
        process.crawl(spider_synottip.SpiderSynottipSpider)
    if 'tipsport' in bookmaker_names:
        process.crawl(spider_tipsport.SpiderTipsportSpider)
    
    process.start()

def create_dataframes_dict(bookmaker_names):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    dataframes_dict = {}
    for bookmaker_name in bookmaker_names:
        try:
            file_path = os.path.join(script_dir, f"../data/data_{bookmaker_name}.json")
            with open(file_path, 'r') as file:
                data = json.load(file)
            df = pd.DataFrame(data)[[
                'bookmaker_id',
                'bookmaker_name',
                'sport_name',
                'sport_detail',
                'country_name',
                'event_startTime',
                'participant_home_list',
                'participant_away_list',
                'participants_gender',
                'participants_age',
                'bet_1',
                'bet_0',
                'bet_2',
                'bet_10',
                'bet_02',
                'bet_12',
                'bet_11',
                'bet_22',
                'event_id',
                'event_url'
            ]].apply(lambda col: col.map(lambda x: tuple(x) if isinstance(x, list) else x)).drop_duplicates()
            df['event_startTime'] = pd.to_datetime(df['event_startTime'])
            df['bet_list'] = tuple(zip(df['bet_1'], df['bet_0'], df['bet_2'], df['bet_10'], df['bet_02'], df['bet_12'], df['bet_11'], df['bet_22']))
            dataframes_dict[bookmaker_name] = df.loc[df['sport_name'] != 'special'].reset_index(drop = True)
        except:
            pass
    return dataframes_dict

def filter_only_close_days(number_of_days, dataframes_dict):
    number_of_days = int(number_of_days)
    today = datetime.now()
    start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = (today + timedelta(days = number_of_days)).replace(hour=23, minute=59, second=59)
    for bookmaker_name in dataframes_dict.keys():
        dataframes_dict[bookmaker_name] = dataframes_dict[bookmaker_name][
            (dataframes_dict[bookmaker_name]['event_startTime'] >= start_date) &
            (dataframes_dict[bookmaker_name]['event_startTime'] <= end_date)
        ]
    return dataframes_dict

def clean_participant_names(dataframes_dict, printIndexDrops = False):
    for bookmaker_name, df in dataframes_dict.items():
        indexes_to_drop = set()
        df['participant_home_list_smaller'] = None
        df['participant_away_list_smaller'] = None
        for idx, row in df.iterrows():
            match_df = df[
                (df['sport_name'] == row['sport_name']) &
                df['sport_detail'].apply(lambda x: x == row['sport_detail'] or x == 'other' or row['sport_detail'] == 'other') &
                df['country_name'].apply(lambda x: x == row['country_name'] or x == 'other' or row['country_name'] == 'other') &
                (df['event_startTime'] == row['event_startTime']) &
                df['participant_home_list'].apply(lambda x: bool(set(x) & set(row['participant_home_list']))) &
                df['participant_away_list'].apply(lambda x: bool(set(x) & set(row['participant_away_list']))) &
                (df['participants_gender'] == row['participants_gender']) &
                (df['participants_age'] == row['participants_age']) &
                (df['event_url'] != row['event_url'])
            ]
            if len(match_df) > 0:
                delete_home_list = tuple(set(item for sublist in match_df['participant_home_list'] for item in sublist))
                delete_away_list = tuple(set(item for sublist in match_df['participant_away_list'] for item in sublist))
                home_list = tuple([word for word in row['participant_home_list'] if word not in delete_home_list])
                away_list = tuple([word for word in row['participant_away_list'] if word not in delete_away_list])
                if home_list and away_list:
                    df.at[idx, 'participant_home_list_smaller'] = home_list
                    df.at[idx, 'participant_away_list_smaller'] = away_list
                else:
                    indexes_to_drop.add(idx)
        if printIndexDrops:
            print(bookmaker_name, indexes_to_drop)
        df.drop(index = indexes_to_drop, inplace = True)
        df['participant_home_list'] = df.apply(lambda row: row['participant_home_list_smaller'] if row['participant_home_list_smaller'] is not None else row['participant_home_list'], axis=1)
        df['participant_away_list'] = df.apply(lambda row: row['participant_away_list_smaller'] if row['participant_away_list_smaller'] is not None else row['participant_away_list'], axis=1)
        df.drop('participant_home_list_smaller', axis=1, inplace=True)
        df.drop('participant_away_list_smaller', axis=1, inplace=True)
        df.reset_index(drop = True, inplace = True)
    return dataframes_dict

def create_events_table(dataframes_dict, dropBets = True):
    df_all = pd.concat(dataframes_dict.values(), axis=0).reset_index(drop=True)
    bookmaker_names = dataframes_dict.keys()
    
    events = pd.DataFrame(columns=[
        'events_id',
        'bookmaker_list',
        'sport_name',
        'sport_detail',
        'country_name',
        'event_startTime',
        'participant_home_list',
        'participant_away_list',
        'participants_gender',
        'participants_age',
        'bet_dict',
        'event_id_dict',
        'event_url_dict'
    ])
    errors = []
        
    for idx, row in df_all.iterrows():

        url_events = events[events['event_url_dict'].apply(lambda x: row['event_url'] in x.values())]
        if url_events.empty: # url tohoto zapasu jeste neni v tabulce events
            isError = False

            sport_detail = row['sport_detail']
            country_name = row['country_name']
            participant_home_list = row['participant_home_list']
            participant_away_list = row['participant_away_list']
            bet_dict = {item: tuple() for item in bookmaker_names}
            bet_dict[row['bookmaker_name']] = row['bet_list']
            event_id_dict = {item: None for item in bookmaker_names}
            event_id_dict[row['bookmaker_name']] = row['event_id']
            event_url_dict = {item: None for item in bookmaker_names}
            event_url_dict[row['bookmaker_name']] = row['event_url']

            bookmaker_search_dict = {item: False for item in bookmaker_names}
            bookmaker_search_dict[row['bookmaker_name']] = True
            not_searched_bookmakers_list = [key for key, value in bookmaker_search_dict.items() if value is False]

            while not_searched_bookmakers_list:
                bookmaker_name_searching = not_searched_bookmakers_list[0]
                bookmaker_df_searching = dataframes_dict[bookmaker_name_searching]
                match_df = bookmaker_df_searching[
                    (bookmaker_df_searching['sport_name'] == row['sport_name']) &
                    bookmaker_df_searching['sport_detail'].apply(lambda x: x == sport_detail or x == 'other' or sport_detail == 'other') &
                    bookmaker_df_searching['country_name'].apply(lambda x: x == country_name or x == 'other' or country_name == 'other') &
                    (bookmaker_df_searching['event_startTime'] == row['event_startTime']) &
                    bookmaker_df_searching['participant_home_list'].apply(lambda x: bool(set(x) & set(participant_home_list))) &
                    bookmaker_df_searching['participant_away_list'].apply(lambda x: bool(set(x) & set(participant_away_list))) &
                    (bookmaker_df_searching['participants_gender'] == row['participants_gender']) &
                    (bookmaker_df_searching['participants_age'] == row['participants_age'])
                ]
                if len(match_df) == 0: # v prohledavane tabulce nemame shodu
                    bookmaker_search_dict[bookmaker_name_searching] = True
                    not_searched_bookmakers_list = [key for key, value in bookmaker_search_dict.items() if value is False]
                elif len(match_df) == 1: # v prohledavane tabulce mame prave jednu shodu
                    match = match_df.iloc[0]
                    if sport_detail == 'other':
                        sport_detail = match['sport_detail']
                    if country_name == 'other':
                        country_name = match['country_name']
                    participant_home_list = tuple(set(participant_home_list + match['participant_home_list']))
                    participant_away_list = tuple(set(participant_away_list + match['participant_away_list']))
                    bet_dict[bookmaker_name_searching] = match['bet_list']
                    event_id_dict[bookmaker_name_searching] = match['event_id']
                    event_url_dict[bookmaker_name_searching] = match['event_url']
                    bookmaker_search_dict = {key: (value is not None) for key, value in event_url_dict.items()}
                    not_searched_bookmakers_list = [key for key, value in bookmaker_search_dict.items() if value is False]
                else: # v prohledavane tabulce mame vice nez jednu shodu -> error
                    error_dict = {
                        'sport_name': row['sport_name'],
                        'sport_detail': sport_detail,
                        'country_name': country_name,
                        'event_startTime': row['event_startTime'],
                        'participant_home_list': participant_home_list,
                        'participant_away_list': participant_away_list,
                        'participants_gender': row['participants_gender'],
                        'participants_age': row['participants_age'],
                        'event_id_dict': event_id_dict,
                        'event_url_dict': event_url_dict,
                        'match_df': match_df
                    }
                    errors.append(error_dict)

                    isError = True
                    event_url_dict[bookmaker_name_searching] = 'error'
                    bookmaker_search_dict[bookmaker_name_searching] = True
                    not_searched_bookmakers_list = [key for key, value in bookmaker_search_dict.items() if value is False]
                    for error_idx, error_row in match_df.iterrows():
                        new_error_row = {
                            'events_id': 'error',
                            'bookmaker_list': ('error',),
                            'sport_name': error_row['sport_name'],
                            'sport_detail': error_row['sport_detail'],
                            'country_name': error_row['country_name'],
                            'event_startTime': error_row['event_startTime'],
                            'participant_home_list': error_row['participant_home_list'],
                            'participant_away_list': error_row['participant_away_list'],
                            'participants_gender': error_row['participants_gender'],
                            'participants_age': error_row['participants_age'],
                            'bet_dict': {item: tuple() for item in bookmaker_names},
                            'event_id_dict': {item: None for item in bookmaker_names},
                            'event_url_dict': {item: None for item in bookmaker_names}
                        }
                        new_error_row['bet_dict'][bookmaker_name_searching] = error_row['bet_list']
                        new_error_row['event_id_dict'][bookmaker_name_searching] = error_row['event_id']
                        new_error_row['event_url_dict'][bookmaker_name_searching] = error_row['event_url']
                        new_error_row_df = pd.DataFrame([new_error_row])
                        events = pd.concat([events, new_error_row_df], ignore_index=True)
            if isError:
                bookmaker_list = ('error',)
            else:
                bookmaker_list = tuple([key for key, value in event_url_dict.items() if value is not None])
            events_id = '_'.join([item for item in event_id_dict.values() if item is not None])
            new_row = {
                'events_id': events_id,
                'bookmaker_list': bookmaker_list,
                'sport_name': row['sport_name'],
                'sport_detail': sport_detail,
                'country_name': country_name,
                'event_startTime': row['event_startTime'],
                'participant_home_list': participant_home_list,
                'participant_away_list': participant_away_list,
                'participants_gender': row['participants_gender'],
                'participants_age': row['participants_age'],
                'bet_dict': bet_dict,
                'event_id_dict': event_id_dict,
                'event_url_dict': event_url_dict
            }
            new_row_df = pd.DataFrame([new_row])
            # events = pd.concat([events, new_row_df], ignore_index=True)
            dfs_to_concat = [df for df in [events, new_row_df] if not df.empty and not df.isna().all().all()]
            events = pd.concat(dfs_to_concat, ignore_index=True)
    
    if dropBets:
        events.drop('bet_dict', axis=1, inplace=True)
        events.reset_index(drop = True, inplace = True)
    return events

def crawler_detail_func(bookmaker_names, events):
    settings = Settings()
    settings.setmodule('betscraper.settings', priority='project')
    process = CrawlerProcess(settings)

    lists_for_detail_spiders_dict = {}
    for bookmaker_name in bookmaker_names:
        lists_for_detail_spiders_dict[bookmaker_name] = []
    for sport_name, event_url_dict in zip(events['sport_name'], events['event_url_dict']):
        for bookmaker_name, event_url in event_url_dict.items():
            if event_url is not None and bookmaker_name in bookmaker_names:
                lists_for_detail_spiders_dict[bookmaker_name].append({
                    'sport_name': sport_name,
                    'event_url': event_url
                })
    
    if 'betano' in bookmaker_names:
        process.crawl(spider_betano_detail.SpiderBetanoDetailSpider, arg_data = lists_for_detail_spiders_dict['betano']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://www.betano.cz/zapas-sance/teplice-sk-slavia-praha/58204893/')
    if 'betx' in bookmaker_names:
        process.crawl(spider_betx_detail.SpiderBetxDetailSpider, arg_data = lists_for_detail_spiders_dict['betx']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://bet-x.cz/cs/sports-betting/offer/soccer?match=50936435')
    if 'forbet' in bookmaker_names:
        process.crawl(spider_forbet_detail.SpiderForbetDetailSpider, arg_data = lists_for_detail_spiders_dict['forbet']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://www.fbet.cz/prematch/event/MA50936435')
    if 'fortuna' in bookmaker_names:
        process.crawl(spider_fortuna_detail.SpiderFortunaDetailSpider, arg_data = lists_for_detail_spiders_dict['fortuna']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://www.ifortuna.cz/sazeni/fotbal/1-cesko/teplice-slavia-praha-MCZ149614999')
    if 'kingsbet' in bookmaker_names:
        process.crawl(spider_kingsbet_detail.SpiderKingsbetDetailSpider, arg_data = lists_for_detail_spiders_dict['kingsbet']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://www.kingsbet.cz/sport?page=event&eventId=10301025')
    if 'merkur' in bookmaker_names:
        process.crawl(spider_merkur_detail.SpiderMerkurDetailSpider, arg_data = lists_for_detail_spiders_dict['merkur']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://www.merkurxtip.cz/sazeni/online/fotbal/S/1-liga/2334015/special/teplice-v-slavia-prague/130050705')
    if 'sazka' in bookmaker_names:
        process.crawl(spider_sazka_detail.SpiderSazkaDetailSpider, arg_data = lists_for_detail_spiders_dict['sazka']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://www.sazka.cz/kurzove-sazky/sports/event/1818260')
    if 'synottip' in bookmaker_names:
        process.crawl(spider_synottip_detail.SpiderSynottipDetailSpider, arg_data = lists_for_detail_spiders_dict['synottip']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://sport.synottip.cz/zapasy/12cx13cxx27/2416017cxx27/241943424?categoryId=12cx13cxx27')
    if 'tipsport' in bookmaker_names:
        process.crawl(spider_tipsport_detail.SpiderTipsportDetailSpider, arg_data = lists_for_detail_spiders_dict['tipsport']) #, arg_sport_name = sport_name, arg_events_limit = events_limit) #, arg_event_url = 'https://www.tipsport.cz/kurzy/zapas/fotbal-teplice-slavia-praha/6215185')

    process.start()

def create_lists_for_detail_spiders_dict(bookmaker_names, events):
    lists_for_detail_spiders_dict = {}
    for bookmaker_name in bookmaker_names:
        lists_for_detail_spiders_dict[bookmaker_name] = []
    for sport_name, event_url_dict in zip(events['sport_name'], events['event_url_dict']):
        for bookmaker_name, event_url in event_url_dict.items():
            if event_url is not None and bookmaker_name in bookmaker_names:
                lists_for_detail_spiders_dict[bookmaker_name].append({
                    'sport_name': sport_name,
                    'event_url': event_url
                })
    lists_for_detail_spiders_dict = {bn: bn_list for bn, bn_list in lists_for_detail_spiders_dict.items() if bn_list}
    with open('betscraper/data/lists_for_detail_spiders_dict.json', 'w') as json_file:
        json.dump(lists_for_detail_spiders_dict, json_file)
    return lists_for_detail_spiders_dict

def create_detail_dict(bookmaker_names):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    detail_dict = {}
    for bookmaker_name in bookmaker_names:
        file_path = os.path.join(script_dir, f"../data/data_{bookmaker_name}_detail.json")
        with open(file_path, 'r') as file:
            data = json.load(file)
        for item in data:
            try:
                detail_dict[item['event_url']] = item['bet_dict']
            except:
                pass
    return detail_dict

def create_all_bets_df(events, detail_dict):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    template_path = os.path.join(script_dir, 'betscraper/files/detail_dicts/template.json')
    with open(template_path, 'r') as file:
        full_template = json.load(file)
    
    all_bets_df = pd.DataFrame(columns=[
        'events_id',
        'sport_name',
        'event_startTime',
        'event_url_dict',
        'bet_name',
        'group_name',
        'option_names'
    ])

    for idx, row in events.iterrows():
        new_row = {
            'events_id': row['events_id'],
            'sport_name': row['sport_name'],
            'event_startTime': row['event_startTime'],
            'event_url_dict': row['event_url_dict']
        }
        try:
            template = full_template[row['sport_name']]
        except:
            template = full_template['other']
        for bet_name, group_dict in template.items():
            new_row['bet_name'] = bet_name
            for group_name, option_dict in group_dict.items():
                new_row['group_name'] = group_name
                new_row['option_names'] = tuple(option_dict.keys())
                new_row['bet_values_dict'] = {}
                for bookmaker_name, event_url in row['event_url_dict'].items():
                    try:
                        new_row['bet_values_dict'][bookmaker_name] = tuple(detail_dict[event_url][bet_name][group_name].values())
                    except:
                        new_row['bet_values_dict'][bookmaker_name] = tuple(option_dict.values())
                new_row_df = pd.DataFrame([new_row])
                dfs_to_concat = [df for df in [all_bets_df, new_row_df] if not df.empty and not df.isna().all().all()]
                all_bets_df = pd.concat(dfs_to_concat, ignore_index=True)
    
    # odstranit nepotrebne sazky (ty, ktere maji u maximalnich hodnot sazek nejakou hodnotu mensi nez 1) a doplnit maximalni, prumerne a ferove hodnoty sazek
    all_bets_df['bet_values_max'] = all_bets_df['bet_values_dict'].apply(lambda x: tuple(max(values) for values in zip(*[t for t in x.values() if t])))
    all_bets_df = all_bets_df[all_bets_df["bet_values_max"].apply(lambda x: min(x) > 1)].reset_index(drop=True)
    all_bets_df['bet_values_mean'] = all_bets_df['bet_values_dict'].apply(lambda x: tuple(float(np.mean([y for y in values if y >= 1])) for values in zip(*[t for t in x.values() if t])))
    all_bets_df['bet_values_fair'] = all_bets_df['bet_values_mean'].apply(lambda x: tuple(b*sum(1/y for y in x) for b in x))
    return all_bets_df

def create_bet_amounts_min_dict_for_sb(values_tuple, bm_option_names):
    indexed_values_tuple = list(enumerate(values_tuple))
    sorted_indexed_values_tuple = sorted(indexed_values_tuple, key=lambda x: x[1])
    sorted_values_tuple = tuple(value for index, value in sorted_indexed_values_tuple)
    original_indices = tuple(index for index, value in sorted_indexed_values_tuple)
    if len(values_tuple) == 2:
        for b_1 in range(5, 10001, 5):
            for b_2 in range(5, b_1 + 1, 5):
                bet_amount = b_1 + b_2
                min_win = min(b_1 * sorted_values_tuple[0], b_2 * sorted_values_tuple[1])
                if min_win > bet_amount:
                    bets = (b_1, b_2)
                    result_list = [None] * len(bets)
                    for index, number in zip(original_indices, bets):
                        result_list[index] = number
                    return {bm_option_names[i]: result_list[i] for i in range(len(bm_option_names))}
        return {bm_option_names[i]: 0 for i in range(len(bm_option_names))}
    if len(values_tuple) == 3:
        for b_1 in range(5, 10001, 5):
            for b_2 in range(5, b_1 + 1, 5):
                for b_3 in range(5, b_2 + 1, 5):
                    bet_amount = b_1 + b_2 + b_3
                    min_win = min(b_1 * sorted_values_tuple[0], b_2 * sorted_values_tuple[1], b_3 * sorted_values_tuple[2])
                    if min_win > bet_amount:
                        bets = (b_1, b_2, b_3)
                        result_list = [None] * len(bets)
                        for index, number in zip(original_indices, bets):
                            result_list[index] = number
                        return {bm_option_names[i]: result_list[i] for i in range(len(bm_option_names))}
        return {bm_option_names[i]: 0 for i in range(len(bm_option_names))}

def create_sure_bets_df(all_bets_df):
    sure_bets_df = pd.DataFrame(columns=[
        'events_id',
        'sport_name',
        'event_startTime',
        'bet_name',
        'group_name',
        'option_names',
        'event_url_dict',
        'bet_values_dict',
        'bet_amounts_100_dict',
        'bet_amounts_min_dict',
        'sure_bet_result',
    ])

    for idx, row in all_bets_df[all_bets_df["bet_values_max"].apply(lambda t: sum(1/x for x in t) < 1)].reset_index(drop=True).iterrows():
        new_row = {
            'events_id': row['events_id'],
            'sport_name': row['sport_name'],
            'event_startTime': row['event_startTime'],
            'bet_name': row['bet_name'],
            'group_name': row['group_name'],
            'option_names': row['option_names']
        }
        if len(row['option_names']) == 2:
            for name_1, values_1 in row['bet_values_dict'].items():
                for name_2, values_2 in row['bet_values_dict'].items():
                    values_tuple = (values_1[0], values_2[1])
                    sure_bet_result = 1 / sum(1/x for x in [1 if v < 1 else v for v in values_tuple])
                    if sure_bet_result > 1:
                        bm_option_names = (f"{name_1}_{row['option_names'][0]}", f"{name_2}_{row['option_names'][1]}")
                        new_row['event_url_dict'] = {
                            name_1: row['event_url_dict'][name_1],
                            name_2: row['event_url_dict'][name_2],
                        }
                        new_row['bet_values_dict'] = {
                            bm_option_names[0]: values_tuple[0],
                            bm_option_names[1]: values_tuple[1],
                        }
                        new_row['bet_amounts_100_dict'] = {
                            bm_option_names[0]: 100 * sure_bet_result / values_tuple[0],
                            bm_option_names[1]: 100 * sure_bet_result / values_tuple[1],
                        }
                        new_row['bet_amounts_min_dict'] = create_bet_amounts_min_dict_for_sb(values_tuple, bm_option_names)
                        new_row['sure_bet_result'] = sure_bet_result
                        new_row_df = pd.DataFrame([new_row])
                        dfs_to_concat = [df for df in [sure_bets_df, new_row_df] if not df.empty and not df.isna().all().all()]
                        sure_bets_df = pd.concat(dfs_to_concat, ignore_index=True)
        if len(row['option_names']) == 3:
            for name_1, values_1 in row['bet_values_dict'].items():
                for name_2, values_2 in row['bet_values_dict'].items():
                    for name_3, values_3 in row['bet_values_dict'].items():
                        values_tuple = (values_1[0], values_2[1], values_3[2])
                        sure_bet_result = 1 / sum(1/x for x in [1 if v < 1 else v for v in values_tuple])
                        if sure_bet_result > 1:
                            bm_option_names = (f"{name_1}_{row['option_names'][0]}", f"{name_2}_{row['option_names'][1]}", f"{name_3}_{row['option_names'][2]}")
                            new_row['event_url_dict'] = {
                                name_1: row['event_url_dict'][name_1],
                                name_2: row['event_url_dict'][name_2],
                                name_3: row['event_url_dict'][name_3],
                            }
                            new_row['bet_values_dict'] = {
                                bm_option_names[0]: values_tuple[0],
                                bm_option_names[1]: values_tuple[1],
                                bm_option_names[2]: values_tuple[2],
                            }
                            new_row['bet_amounts_100_dict'] = {
                                bm_option_names[0]: 100 * sure_bet_result / values_tuple[0],
                                bm_option_names[1]: 100 * sure_bet_result / values_tuple[1],
                                bm_option_names[2]: 100 * sure_bet_result / values_tuple[2],
                            }
                            new_row['bet_amounts_min_dict'] = create_bet_amounts_min_dict_for_sb(values_tuple, bm_option_names)
                            new_row['sure_bet_result'] = sure_bet_result
                            new_row_df = pd.DataFrame([new_row])
                            dfs_to_concat = [df for df in [sure_bets_df, new_row_df] if not df.empty and not df.isna().all().all()]
                            sure_bets_df = pd.concat(dfs_to_concat, ignore_index=True)
    return sure_bets_df

def create_value_bets_df(all_bets_df):
    value_bets_df = pd.DataFrame(columns=[
        'events_id',
        'sport_name',
        'event_startTime',
        'bet_name',
        'group_name',
        'option_names',
        'bookmaker_name',
        'event_url',
        'option_name',
        'bet_value',
        'bet_value_fair',
        'value_bet_result',
    ])

    for idx, row in all_bets_df[all_bets_df.apply(lambda row: any(a > b for a, b in zip(row["bet_values_max"], row["bet_values_fair"])), axis=1)].reset_index(drop=True).iterrows():
        new_row = {
            'events_id': row['events_id'],
            'sport_name': row['sport_name'],
            'event_startTime': row['event_startTime'],
            'bet_name': row['bet_name'],
            'group_name': row['group_name'],
            'option_names': row['option_names']
        }
        for bookmaker_name, bet_values in row['bet_values_dict'].items():
            new_row['bookmaker_name'] = bookmaker_name
            new_row['event_url'] = row['event_url_dict'][bookmaker_name]
            for option_index, (bet_value, bet_value_fair) in enumerate(zip(bet_values, row['bet_values_fair'])):
                if bet_value > bet_value_fair:
                    new_row['option_name'] = row['option_names'][option_index]
                    new_row['bet_value'] = bet_value
                    new_row['bet_value_fair'] = bet_value_fair
                    new_row['value_bet_result'] = (bet_value - 1) / (bet_value_fair - 1)
                    new_row_df = pd.DataFrame([new_row])
                    dfs_to_concat = [df for df in [value_bets_df, new_row_df] if not df.empty and not df.isna().all().all()]
                    value_bets_df = pd.concat(dfs_to_concat, ignore_index=True)
    return value_bets_df

# MAIN
if __name__ == '__main__':
    # # nastavit bookmakery, ktere chci pouzivat
    # bookmaker_names = ['betano', 'betx', 'forbet', 'fortuna', 'kingsbet', 'merkur', 'sazka', 'synottip', 'tipsport']

    # # crawler
    # # crawler_func(bookmaker_names)
    # subprocess.run([f"{sys.executable}", "betscraper/crawler.py"])

    # # nahrat puvodni data o eventech do dataframu
    # dataframes_dict = create_dataframes_dict(bookmaker_names)

    # # upravit seznam bookmakeru po tom, jaka data se podari stahnout
    # bookmaker_names = [bn for bn, df in dataframes_dict.items() if not df.empty]

    # # vyfiltrovat pouze omezeny pocet dnu nasledujicihc po dnu stazeni dat
    # number_of_days = 1
    # dataframes_dict = filter_only_close_days(number_of_days, dataframes_dict)

    # # vycistit slova navic v listech obsahujicich jmena jednotlivych tymu
    # printIndexDrops = False
    # dataframes_dict = clean_participant_names(dataframes_dict, printIndexDrops)

    # # vytvorit spojenou tabulku pro vsechny puvodni eventy
    # dropBets = True
    # events = create_events_table(dataframes_dict, dropBets)

    # # oddelit eventy s errorem
    # # events_with_error = events[events['bookmaker_list'].apply(lambda x: 'error' in x)]
    # events = events[~events['bookmaker_list'].apply(lambda x: 'error' in x)]

    # # oddelit eventy, ktere se na nic nenapoji
    # # events_singlies = events[events['bookmaker_list'].apply(lambda x: len(x) == 1)]
    # events = events[~events['bookmaker_list'].apply(lambda x: len(x) == 1)]

    # # nechat pouze eventy se startem za urcity pocet minut
    # number_of_minutes = 5
    # now_plus_minutes = datetime.now() + timedelta(minutes = number_of_minutes)
    # events = events[events['event_startTime'] >= now_plus_minutes]

    # # # nechat pouze eventy, ktere se odehraji do urciteho poctu hodin
    # # number_of_hours = 12
    # # now_plus_hours = datetime.now() + timedelta(hours = number_of_hours)
    # # events = events[events['event_startTime'] <= now_plus_hours]ˇ

    # # ulozit tabulku events
    # events.to_csv('betscraper/data/events.csv', index=False)
    # events.to_pickle('betscraper/data/events.pkl')

    ### USEK PRO TESTOVANI
    events = pd.read_pickle('betscraper/data/events.pkl')
    bookmaker_names = ['betano', 'betx', 'forbet', 'fortuna', 'kingsbet', 'merkur', 'sazka', 'synottip', 'tipsport']
    dataframes_dict = create_dataframes_dict(bookmaker_names)
    bookmaker_names = [bn for bn, df in dataframes_dict.items() if not df.empty]
    ### USEK PRO TESTOVANI

    # rozdeleni dataframu s eventy na dataframy o danem poctu radku
    events_sorted = events.sort_values(by='event_startTime').reset_index(drop=True)
    chunk_size = 100
    events_100_list = [events_sorted.iloc[i:i + chunk_size] for i in range(0, len(events_sorted), chunk_size)]

    original_bookamker_names = bookmaker_names
    for events_100_list_position, events in enumerate(events_100_list):
        for stage in ('events_stage', 'sb_confirmation_stage'):
            ### FIRST STAGE - SMALLER EVENTS DATAFRAMES
            print(f"FIRST STAGE - SMALLER EVENTS DATAFRAMES - table {events_100_list_position + 1}/{len(events_100_list)}")

            # vytvorit lists_for_detail_spiders_dict
            lists_for_detail_spiders_dict = create_lists_for_detail_spiders_dict(original_bookamker_names, events)
            bookmaker_names = list(lists_for_detail_spiders_dict.keys())

            # crawler detail
            if 'forbet' in bookmaker_names:
                subprocess.run([f"{sys.executable}", "betscraper/crawler_detail_subp.py", 'forbet'])
            if 'tipsport' in bookmaker_names:
                subprocess.run([f"{sys.executable}", "betscraper/crawler_detail_subp.py", 'tipsport'])
            if [item for item in bookmaker_names if item not in ['forbet', 'tipsport']]:
                subprocess.run([f"{sys.executable}", "betscraper/crawler_detail_subp.py", 'rest'])

            # nahrat detail data do spolecneho detail_dict
            detail_dict = create_detail_dict(bookmaker_names)

            # vytvorit dataframe vsech sazek, ktere jsem byl schopen vytahnout pomoci detail spideru
            all_bets_df = create_all_bets_df(events, detail_dict)
            # all_bets_df.to_csv('betscraper/data/all_bets_df.csv', index=False)
            # all_bets_df.to_pickle('betscraper/data/all_bets_df.pkl')

            # vytvorit tabulku pro sure bets
            sure_bets_df = create_sure_bets_df(all_bets_df)
            # sure_bets_df.to_csv('betscraper/data/sure_bets_df.csv', index=False)
            # sure_bets_df.to_pickle('betscraper/data/sure_bets_df.pkl')

            # vytvorit tabulku pro value bets
            value_bets_df = create_value_bets_df(all_bets_df)
            value_bets_df.to_csv('betscraper/data/value_bets_df.csv', index=False)
            value_bets_df.to_pickle('betscraper/data/value_bets_df.pkl')

            ### SECOND STAGE - SURE BETS VERIFICATION
            print(f"SECOND STAGE - SURE BETS VERIFICATION - table {events_100_list_position + 1}/{len(events_100_list)}")

            # vytvorit filtrovany events dataframe z eventu z posledniho ulozeneho a nove vytvoreneho sure bets dataframu
            try:
                sure_bets_df_old = pd.read_pickle('betscraper/data/sure_bets_df.pkl')
                sb_combined_df = pd.concat([sure_bets_df_old, sure_bets_df])
            except:
                sb_combined_df = sure_bets_df
            sb_future_df = sb_combined_df[sb_combined_df['event_startTime'] > datetime.now()]
            events_id_list = sb_future_df['events_id'].unique().tolist()
            events_filtered = events_sorted[events_sorted['events_id'].isin(events_id_list)]

            if events_filtered.empty:
                print('NO SURE BETS EVENTS TO SEARCH AND VERIFY')
            else:
                print('SEARCHING AND VERIFYING SURE BETS EVENTS')

                # vytvorit lists_for_detail_spiders_dict
                lists_for_detail_spiders_dict = create_lists_for_detail_spiders_dict(original_bookamker_names, events_filtered)
                bookmaker_names = list(lists_for_detail_spiders_dict.keys())

                # crawler detail
                if 'forbet' in bookmaker_names:
                    subprocess.run([f"{sys.executable}", "betscraper/crawler_detail_subp.py", 'forbet'])
                if 'tipsport' in bookmaker_names:
                    subprocess.run([f"{sys.executable}", "betscraper/crawler_detail_subp.py", 'tipsport'])
                if [item for item in bookmaker_names if item not in ['forbet', 'tipsport']]:
                    subprocess.run([f"{sys.executable}", "betscraper/crawler_detail_subp.py", 'rest'])

                # nahrat detail data do spolecneho detail_dict
                detail_dict = create_detail_dict(bookmaker_names)

                # vytvorit dataframe vsech sazek, ktere jsem byl schopen vytahnout pomoci detail spideru
                all_bets_df = create_all_bets_df(events_filtered, detail_dict)
                # all_bets_df.to_csv('betscraper/data/all_bets_df.csv', index=False)
                # all_bets_df.to_pickle('betscraper/data/all_bets_df.pkl')

                # vytvorit tabulku pro sure bets
                sure_bets_df = create_sure_bets_df(all_bets_df)
                sure_bets_df.to_csv('betscraper/data/sure_bets_df.csv', index=False)
                sure_bets_df.to_pickle('betscraper/data/sure_bets_df.pkl')
