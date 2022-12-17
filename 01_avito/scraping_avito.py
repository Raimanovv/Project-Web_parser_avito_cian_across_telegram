from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from urllib.parse import unquote
from datetime import datetime
import json
import time

SITE = 'https://www.avito.ru'

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")

# options.add_argument("--headless")

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )


# !!! get_attribute('textContent')
def get_json(url):
    driver.get(url)
    script = driver.find_element(By.XPATH, '/html/body/script[1]')
    jsontext = script.get_attribute('textContent').split(';')[0].split('=')[-1].strip()[1:-1]  # Извлечение JSON из HTML
    jsontext = unquote(jsontext)
    data = json.loads(jsontext)
    time.sleep(2)
    driver.quit()

    return data


def get_offers(data):
    offers = list()

    for key in data:
        if 'single-page' in key:
            items = data[key]['data']['catalog']['items']
            for item in items:
                if item.get('id'):
                    offer = dict()
                    offer['price'] = item['priceDetailed']['value']
                    offer['title'] = item['title']
                    offer['url'] = SITE + item['urlPath']
                    timestamp = datetime.fromtimestamp(item['sortTimeStamp'] / 1000)  # получаем нормальную дату
                    timestamp = datetime.strftime(timestamp, '%d.%m.%Y в %H:%M')  # форматируем дату
                    offer['offer_data'] = timestamp
                    city = item['addressDetailed']['locationName']
                    address = item['geo']['formattedAddress']
                    offer['geo'] = city + ', ' + address
                    offers.append(offer)

    return offers


def main():
    url = "https://www.avito.ru/kazan/kvartiry/sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg?cd=1&s=104&user=1"
    data = get_json(url)
    offers = get_offers(data)
    for offer in offers:
        print(offer)


if __name__ == '__main__':
    main()
