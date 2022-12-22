import sqlite3
import json
import time
from datetime import datetime
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from app.realty import check_database

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")

options.add_argument("--headless")

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)


def driver_func():
    driver = webdriver.Chrome(options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    return driver


driver = webdriver.Chrome(options=options)


# !!! get_attribute('textContent')
def get_json(url):
    driver = driver_func()
    driver.get(url)
    script = driver.find_element(By.XPATH, '/html/body/script[1]')
    jsontext = script.get_attribute('textContent').split(';')[0].split('=')[-1].strip()[1:-1]  # Извлечение JSON из HTML
    jsontext = unquote(jsontext)
    data = json.loads(jsontext)
    time.sleep(2)
    driver.quit()

    return data


def get_offer(item):
    offer = dict()

    offer["url"] = 'https://www.avito.ru' + item['urlPath']
    offer["offer_id"] = item["id"]
    offer["price"] = item['priceDetailed']['value']

    timestamp = datetime.fromtimestamp(item['sortTimeStamp'] / 1000)  # получаем нормальную дату
    timestamp = datetime.strftime(timestamp, '%d-%m-%Y в %H:%M:%S')  # форматируем дату
    offer["data"] = timestamp

    city = item['addressDetailed']['locationName']
    address = item['geo']['formattedAddress']
    offer["address"] = city + ', ' + address

    title = item['title'].split(', ')
    area = float(title[1].replace(' м²', '').replace(',', '.'))
    rooms = title[0]

    floor_info = title[2].replace(' эт.', '').split('/')
    floor = floor_info[0]
    total_floor = floor_info[-1]

    offer["area"] = area
    offer["rooms"] = rooms
    offer["floor"] = floor
    offer["total_floor"] = total_floor

    return offer


def get_offers(data):
    offers = list()

    for key in data:
        if 'single-page' in key:
            items = data[key]['data']['catalog']['items']
            items = reversed(items)
            for item in items:
                if "item" in item["type"]:
                    offer = get_offer(item)
                    check_database(offer)


def main():
    url = "https://www.avito.ru/kazan/kvartiry/sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg?cd=1&s=104&user=1"
    data = get_json(url)
    offers = get_offers(data)


if __name__ == '__main__':
    while True:
        main()
        time.sleep(20)
