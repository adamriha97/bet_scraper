from curl_cffi import requests
import json
import time


start_time = time.time()


url = 'https://www.fbet.cz/api/web/v1/offer/event_detail'
headers = {
    'Content-Type': 'application/json'
}

with open(f"betscraper/data/data_forbet.json", 'r') as file:
    data = json.load(file)

i = 0
for item in data[:30]:
    event_url = item['event_url']
    # print(f"Event: {event_url}")
    body = json.dumps({
        "offerMode": "prematch",
        "lang": "cs",
        "id_event": event_url.split('/')[-1]
    })
    response = requests.request(
        method = 'POST',
        url = url,
        headers = headers,
        data = body,
        impersonate = 'chrome'
    )
    i += 1
    print(f"Call {i}: {response.status_code}")


end_time = time.time()
print(end_time - start_time)