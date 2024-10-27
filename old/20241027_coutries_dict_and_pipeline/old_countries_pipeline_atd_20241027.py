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
    





import pandas as pd
from unidecode import unidecode

# Read the CSV with the known encoding, e.g., "ISO-8859-1" or "Windows-1250"
df_zeme = pd.read_csv("zeme.csv")
df_zeme_tenis = pd.read_csv("zeme_tenis.csv")


countries_dict = {}

for row in df_zeme.itertuples():
    countries_dict[unidecode(row.stat.lower().replace(' ', '-'))] = [row.stat, row.mesto]


countries_dict['spojene-kralovstvi'].append('Velká Británie')


countries_dict['spojene-kralovstvi']


for row in df_zeme_tenis.itertuples():
    list = row.turnaj.split(' - ')
    try:
        countries_dict[unidecode(list[1].lower().replace(' ', '-'))].append(list[0])
    except:
        print(list)


# Specify the filename
filename = 'countries_dict.json'

# Write the dictionary to a JSON file
with open(filename, 'w') as file:
    json.dump(countries_dict_2, file, ensure_ascii=False, indent=4)  # `indent=4` makes the JSON pretty-printed


countries_dict_file = 'countries_dict.json'
with open(countries_dict_file, 'r') as file:
    countries_dict = json.load(file)


countries_dict_2 = {}

for name, itemlist in countries_dict.items():
    countries_dict_2[name] = [*set(itemlist)]


countries_dict_2






countries_dict_file = 'countries_dict.json'
with open(countries_dict_file, 'r') as file:
    countries_dict = json.load(file)

zeme_pridavna_jmena_file = 'zeme_pridavna_jmena.json'
with open(zeme_pridavna_jmena_file, 'r') as file:
    zeme_pridavna_jmena = json.load(file)


for zeme, zeme_pj in zeme_pridavna_jmena.items():
    for name, itemlist in countries_dict.items():
        if zeme in itemlist:
            itemlist.append(zeme_pj[:-1])


countries_dict_2 = {}

for name, itemlist in countries_dict.items():
    countries_dict_2[name] = [*set(itemlist)]


# Specify the filename
filename = 'countries_dict.json'

# Write the dictionary to a JSON file
with open(filename, 'w') as file:
    json.dump(countries_dict_2, file, ensure_ascii=False, indent=4)  # `indent=4` makes the JSON pretty-printed
