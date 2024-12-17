import json


def create_template_and_translator(bookmaker_name):
    bets_dict_path = 'betscraper/betscraper/files/bets_dict.json'
    with open(bets_dict_path, 'r') as file:
        bets_dict = json.load(file)
    full_translator = {}
    full_template = {}
    for sport_name, sport_dict in bets_dict.items():
        full_translator[sport_name] = {}
        full_template[sport_name] = {}
        for bet_name, bet_dict in sport_dict.items():
            original_bet_names = bet_dict['names'][bookmaker_name]
            full_template[sport_name][bet_name] = {}
            for group_name, group_dict in bet_dict['groups'].items():
                full_template[sport_name][bet_name][group_name] = {}
                for option_name, option_dict in group_dict.items():
                    full_template[sport_name][bet_name][group_name][option_name] = -1.0
                    original_option_names = option_dict[bookmaker_name]
                    connections = [f"{obn} {oon}" for obn in original_bet_names for oon in original_option_names]
                    for connection in connections:
                        full_translator[sport_name][connection] = {}
                        full_translator[sport_name][connection]['name'] = bet_name
                        full_translator[sport_name][connection]['group'] = group_name
                        full_translator[sport_name][connection]['option'] = option_name
    with open(f"betscraper/betscraper/files/detail_dicts/template.json", "w", encoding="utf-8") as json_file:
        json.dump(full_template, json_file, indent=4, ensure_ascii=False)  # `indent` is optional for pretty printing
    with open(f"betscraper/betscraper/files/detail_dicts/{bookmaker_name}_translator.json", "w", encoding="utf-8") as json_file:
        json.dump(full_translator, json_file, indent=4, ensure_ascii=False)  # `indent` is optional for pretty printing

bookmaker_names = ['betano', 'betx', 'forbet', 'fortuna', 'kingsbet', 'merkur', 'sazka', 'synottip', 'tipsport']
for bookmaker_name in bookmaker_names:
    create_template_and_translator(bookmaker_name)