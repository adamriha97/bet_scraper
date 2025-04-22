# from playwright.sync_api import sync_playwright

from camoufox.sync_api import Camoufox
from camoufox.async_api import AsyncCamoufox
import time
from browserforge.fingerprints import Screen
import asyncio

def get_cookies_from_url(url):
    # with sync_playwright() as p:
    #     browser = p.chromium.launch(headless=True)
    constrains = Screen(max_width=1920, max_height=1080)
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
        # time.sleep(5)
        # page.wait_for_load_state()
        # cookies = context.cookies()
        # browser.close()
        # return cookies
        page.wait_for_load_state(state='load')
        cookies = context.cookies()
        for index in range(100):
            try:
                time.sleep(0.1)
                cookies = context.cookies()
                for cookie in cookies:
                    if cookie['name'] == 'JSESSIONID':
                        return cookies
                print(index)
            except:
                pass
        return cookies

async def async_get_cookies_from_url(url):
    # with sync_playwright() as p:
    #     browser = p.chromium.launch(headless=True)
    constrains = Screen(max_width=1920, max_height=1080)
    async with AsyncCamoufox(
        os="windows",
        screen=constrains,
        humanize=True,
        headless=True,
        geoip=True,
        locale="cs-CZ"
    ) as browser:
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        # time.sleep(5)
        # page.wait_for_load_state()
        # cookies = context.cookies()
        # browser.close()
        # return cookies
        await page.wait_for_load_state(state='load')
        cookies = await context.cookies()
        for index in range(100):
            try:
                time.sleep(0.1)
                cookies = await context.cookies()
                for cookie in cookies:
                    if cookie['name'] == 'JSESSIONID':
                        return cookies
                print(index)
            except:
                pass
        return cookies
        

url = 'https://www.tipsport.cz/informace'
# cookies = get_cookies_from_url(url)
# for cookie in cookies:
#     if cookie['name'] == 'JSESSIONID':
#         print(f"{cookie['name']}: {cookie['value']}")

for i in range(2):
    # cookies = get_cookies_from_url(url)
    cookies = asyncio.run(async_get_cookies_from_url(url))
    for cookie in cookies:
        if cookie['name'] == 'JSESSIONID':
            print(f"{i+1} -> {cookie['name']}: {cookie['value']}")
