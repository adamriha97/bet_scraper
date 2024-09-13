from curl_cffi import requests
import json

url = "https://www.tipsport.cz/rest/offer/v2/offer?limit=9999"

payload = json.dumps({})
headers = {
  'Cookie': 'JSESSIONID=qiOdMFFMc7vEwk6TZaxP6jcwvX0jcMEYOwVTIALR.czp-wt2',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload, impersonate='chrome')

print(response.text)
