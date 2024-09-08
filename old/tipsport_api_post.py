from curl_cffi import requests

url = "https://www.tipsport.cz/rest/offer/v2/offer?limit=75"

payload = "{}"
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
  'Accept': 'application/json',
  'Accept-Language': 'cs,sk;q=0.8,en-US;q=0.5,en;q=0.3',
  'Accept-Encoding': 'gzip, deflate, br, zstd',
  'Referer': 'https://www.tipsport.cz/kurzy/fotbal-16',
  'content-type': 'application/json;charset=utf-8',
  'Origin': 'https://www.tipsport.cz',
  'Connection': 'keep-alive',
  'Cookie': 'cz.tipsport.cookie.language=cs; i1YjbsBF=AzUDRhKPAQAAVrOr7cLUN-h3DIDl8MmiyiPGYb7j_URZfXLDThx0yEfb_8M6AW1RqWycuHvuwH8AAEB3AAAAAA^|1^|0^|5be0e471583fc963fd3dbc26c9a7fcfb8f84f618; ft1NjitDe=dtihxnDn; dRwc3N4Jgh=t80x2o0H54riRvQ8ZYLfzBRDaa2NMytc; cmsref=25.08.2024 20:48https^%^3A^%^2F^%^2Fwww.google.com^%^2F; partnerClickId=18773259983; ticketBuildersPersistenceId=3153a69f-a694-e593-ce23-b423120c3171; cz.tipsport.cookies.nightMode=0; JSESSIONID=bB8Z9ojgN5hMxxpCMdXAqi1mSEbY2ypN6lDJe6fF.czp-wt24; TS01d188af=01dd7cd28ef827abeab54495972b562535770ddeaceea6329bdcd80ce83dddd7b220a369eb5795306b4eb0df4a5b705bcea6961a33; TS01add8cc=01dd7cd28e0fe769157b7c9ea06fe0667006d54c5fd92cece49f2cf5d0ecdae968d069b26877e815fcff2a29ce8cb7481c08a094a6; wepc=^!oiYuBAC8VzbFH6VBewVvwUPykzQbR/m/P4ju+s9wbU8YbrHVHYMTjdV5qUObucZmZlNfzUTt3P4GvRU=; APISID=tIGjdd9Ke04MGpHRVOX6Z4i1ECT1i31C9wnoHDywQK1vUyVKYD70XoBctEcGybIK; TS01c06948=01dd7cd28e5cadfeaa343c7ae44064b2194bad5528baa455a3547d8b80b117dc72bf9c3d76c916597ac2762a5a4f5e1f6ec57ba681; TS01bc392b=01dd7cd28e7351d7f2013978cda9f6c25849f8d392eebc05649814bd6db0325c755d2a5b561a0ada96db28864b91fc6e32f37b7117; f3ad75afc15f7c6f0eb37e4a4782cdc4=df2a30a6fbd1fd30dd59bc6f4ba703dc; TS01dc5e80=01dd7cd28e83250b4d05cb316dc9d4d4871b3158b36bb9dacebbf1672e9014995535a80a1af65f9685ef08789b4a5cb44ac95d4a49; __cf_bm=_DBRuCu99FJ2Qt0TmeUyGQNiO8c7aLJ78ib6X1NGM9Y-1725817056-1.0.1.1-q38tIKB0Uf1I_fQhk49J2H6ddHsdC3a18k4o7nR3hUNquU4UJT2hy9QCoYR8ig0mfpfROd0eUf3IE5jcmlXS9Q; AonI0i5YfE=ogaTaljhk2I9dr3P8I3cqBIntVjcHkcZ; ktlvDW7IG5ClOcxYTbmY=a; ADRUM_BT1=R:39^|i:44823^|e:5^|d:0; ADRUM_BTa=R:39^|g:0c9fa0e5-65da-48da-a5c7-e32e934f24c4^|n:customer1_4b581624-a492-4d32-9fa5-e67de31b5046; SameSite=None; ADRUM_BT1="R:39|i:80434|e:7"; ADRUM_BTa="R:39|g:ffc852a1-8ab9-4c99-8ebd-49dca94bd405|n:customer1_4b581624-a492-4d32-9fa5-e67de31b5046"; SameSite=None; TS01c06948=01dd7cd28e66529bccea6da860d6ec8733ac5c272e42fb2d9e9ca153a66f576dab67af6f57ee2ea8e6392700921493377063bf2a5e; wepc=!NqeRAPrPlKV6zmPiHj2H8OAThFsVNaVK3CgdpUhe0IlEU2MhX+4V2teHHgrdavJKGPxGQA21JR4KPLg=',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'Priority': 'u=4'
}

response = requests.request("POST", url, headers=headers, data=payload, impersonate='chrome')

print(response.text)
