from curl_cffi import requests
import json
import time


start_time = time.time()


url = 'https://www.fbet.cz/api/web/v1/offer/event_detail'
headers = {
    'Content-Type': 'application/json'
}
headers_firefox = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0',
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'en-US,en;q=0.5',
  'Accept-Encoding': 'gzip, deflate, br, zstd',
  'Referer': 'https://www.fbet.cz/',
  'Content-Type': 'application/json',
  'Origin': 'https://www.fbet.cz',
  'Alt-Used': 'www.fbet.cz',
  'Connection': 'keep-alive',
  'Cookie': '_gcl_au=1.1.675517902.1740140404; session=f6d8976393e44200895fd0f7b6128df1; _ga_DHFYPKZ39W=GS1.1.1740140406.1.1.1740140584.5.0.1694069719; _ga=GA1.1.1291982174.1740140407; _fbp=fb.1.1740140413341.409797168624629274; udid=01952873-6efd-79c5-a9b7-8536bf9c30e7; CookieConsent={stamp:^%^27IoCqV1gczaFr2zXygzZGes7TvshQm6JuOsd98z84WPcfZKXCRNrIIA==^%^27^%^2Cnecessary:true^%^2Cpreferences:true^%^2Cstatistics:true^%^2Cmarketing:true^%^2Cmethod:^%^27explicit^%^27^%^2Cver:1^%^2Cutc:1740140437823^%^2Cregion:^%^27cz^%^27}; _sp_srt_ses.0631=*; _sp_srt_id.0631=23711998-085f-43cb-82e9-f9a0b8171d49.1740140529.1.1740140583..eb0fa23d-2d72-4fa8-8a3d-3ed6252716f1....0; session=f6d8976393e44200895fd0f7b6128df1',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'TE': 'trailers'
}
headers_brave = {
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'cs-CZ,cs;q=0.5',
  'content-type': 'application/json',
  'origin': 'https://www.fbet.cz',
  'priority': 'u=1, i',
  'referer': 'https://www.fbet.cz/',
  'sec-ch-ua': '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'sec-gpc': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
  'Cookie': 'session=bd317a1e4e6f41c1ac069243c196763a' # bd317a1e4e6f41c1ac069243c196763a f6d8976393e44200895fd0f7b6128df1
}
headers_edge = {
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'cs,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
  'content-type': 'application/json',
  'origin': 'https://www.fbet.cz',
  'priority': 'u=1, i',
  'referer': 'https://www.fbet.cz/',
  'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
  'Cookie': 'session=fd22816b09e2478b9d89fe60c4172f8a' # f6d8976393e44200895fd0f7b6128df1 fd22816b09e2478b9d89fe60c4172f8a
}

proxy_http_url = 'http://78.80.228.150:80'
proxy_https_url = 'http://78.80.228.150:80'

mail = 'ellynn58@edny.net' # tilditeal@edny.net
mail_psw = 'llynn58@E' # ilditeal@T1
username = 'test_oxylabs_vKkVQ'
password = 'oxylabs1_proxy+fB'
proxy = 'dc.oxylabs.io:8000'
proxies = {
   "https": ('https://user-%s:%s@%s' % (username, password, proxy))
}

with open(f"betscraper/data/data_forbet.json", 'r') as file:
    data = json.load(file)

i = 0
for item in data[:40]:
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
        impersonate = 'chrome', # chrome safari edge101
        # proxies = proxies,
        # proxies = {"http": proxy_http_url, "https": proxy_https_url},
        # proxies = {"https": "http://localhost:3128"},
        # proxy = 'http://90.182.147.170:4145',
    )
    i += 1
    print(f"Call {i}: {response.status_code}")
    try:
      response_json = json.loads(response.text)
      print(str(response_json)[:100])
    except:
       print(f'No response due to: {response.status_code}')


end_time = time.time()
print(end_time - start_time)