import requests
import json

url = "https://www.tipsport.cz/rest/offer/v2/offer?limit=9999"

payload = json.dumps({})
headers = {
  'Cookie': 'JSESSIONID=Seak2Vz4Rfpb1qAOHxbt3RHcZ97007tUc1XxbXis.czp-wt19; APISID=uWp4tWZOpVQPnNJfa3dUCFS4bgygc6GHy4ClQbeHWzE5KH3GQuP4GGKzVprJQUPj; TS01bc392b=01dd7cd28e21013b3558472740e633cf916590181cdc39306599239e05ee16230f6a28b9d7b9fb90a848e48c6500d212f9ae18c8ab; __cf_bm=CnwjahRsk73TtTsD83909CSzzVdypCU3IP7LQ0Ntpi4-1724081961-1.0.1.1-dhHsXGPLsPocQ.EYkGIBj_ObYAfdtb4tNKDgY8t_cYWBRct2Gbz3XvViCYE9L7j_GIymKv8Xj.UNfeVBPNnV4w; TS01c06948=01dd7cd28e384801cfd6f93fa47e5ec2adf083ab4cbbb2ba2051c6532d90d339bb9e8cad98eaac84dd32caa4f50c8e196ea9ea5957; wepc=!xxmMVaFYCpka9tpBewVvwUPykzQbR/b3uzdhspdMK8jRxIK8vQ2pBKbgODFMUeQ2K9W+EX5R8QhlUas=',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
