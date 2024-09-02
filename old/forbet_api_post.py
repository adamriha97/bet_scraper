import requests
import json

url = "https://www.iforbet.cz/api/web/v1/offer/full_offer"

payload = json.dumps({
#   "offerMode": "prematch",
#   "lang": "cs"
})
headers = {
#   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
