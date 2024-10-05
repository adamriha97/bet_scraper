import json
import pandas as pd


with open('data/data_betano.json', 'r') as file:
    data_betano = json.load(file)
    df1 = pd.DataFrame(data_betano)
with open('data/data_fortuna.json', 'r') as file:
    data_fortuna = json.load(file)
    df2 = pd.DataFrame(data_fortuna)
with open('data/data_tipsport.json', 'r') as file:
    data_tipsport = json.load(file)
    df3 = pd.DataFrame(data_tipsport)
with open('data/data_sazka.json', 'r') as file:
    data_sazka = json.load(file)
    df4 = pd.DataFrame(data_sazka)
with open('data/data_merkur.json', 'r') as file:
    data_merkur = json.load(file)
    df5 = pd.DataFrame(data_merkur)
with open('data/data_betx.json', 'r') as file:
    data_betx = json.load(file)
    df6 = pd.DataFrame(data_betx)
with open('data/data_forbet.json', 'r') as file:
    data_forbet = json.load(file)
    df7 = pd.DataFrame(data_forbet)
with open('data/data_kingsbet.json', 'r') as file:
    data_kingsbet = json.load(file)
    df8 = pd.DataFrame(data_kingsbet)
with open('data/data_synottip.json', 'r') as file:
    data_synottip = json.load(file)
    df9 = pd.DataFrame(data_synottip)

dataframes = [df1, df2, df3, df4, df5, df6, df7, df8, df9]
df = pd.concat(dataframes, axis=0)
df.reset_index(drop=True, inplace=True)

print(df[df['sport_name'] == 'other'])