# from playwright.sync_api import sync_playwright
from camoufox.sync_api import Camoufox
import time
from browserforge.fingerprints import Screen

constrains = Screen(max_width=1920, max_height=1080)
def get_cookies_from_url(url):
    # with sync_playwright() as p:
    #     browser = p.chromium.launch(headless=True)
    with Camoufox(
        os="windows",
        screen=constrains,
        humanize=True,
        headless=True,
        geoip=True,
        locale="cs-CZ"
    ) as browser:
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)
        time.sleep(5)
        page.wait_for_load_state()
        cookies = context.cookies()
        browser.close()
        return cookies

url = 'https://www.tipsport.cz/'
# cookies = get_cookies_from_url(url)
# for cookie in cookies:
#     if cookie['name'] == 'JSESSIONID':
#         print(f"{cookie['name']}: {cookie['value']}")

for i in range(10):
    cookies = get_cookies_from_url(url)
    for cookie in cookies:
        if cookie['name'] == 'JSESSIONID':
            print(f"{i+1} -> {cookie['name']}: {cookie['value']}")
