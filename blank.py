from playwright.sync_api import sync_playwright


def get_cookies(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)
        try:
            cookies = context.cookies()
            for cookie in cookies:
                try:
                    if cookie['name'] == 'JSESSIONID':
                        print(cookie['value'])
                except:
                    pass
        except:
            pass
        browser.close()
url = 'https://www.tipsport.cz/kurzy.xml'
get_cookies(url)