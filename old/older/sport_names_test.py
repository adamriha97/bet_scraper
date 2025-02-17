import json
import pandas as pd


# Load the JSON data (assuming the file is saved locally as 'data.json')
with open('data/data_livescore.json', 'r') as file:
    data = json.load(file)

# Convert the JSON data into a pandas DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
# print(df)

# Extract the 'sport' column and get distinct values
distinct_sports = df['sport'].unique().tolist()

# Print the list of distinct values
# print(distinct_sports)

# Create the dictionary where the key is the sport name and the value is a list containing the sport name
sports_dict = {sport: [sport] for sport in distinct_sports}

# Save the dictionary as a JSON file
# with open('sports_dict_add.json', 'w') as json_file:
#     json.dump(sports_dict, json_file, indent=4)

# Save the dictionary as a JSON file with UTF-8 encoding
with open('sports_dict_add.json', 'w', encoding='utf-8') as json_file:
    json.dump(sports_dict, json_file, ensure_ascii=False, indent=4)

# Optional: Print the dictionary to verify the output
print(sports_dict)