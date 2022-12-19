import sqlite3
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from app.realty import check_database

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
    script = driver.find_element(By.XPATH, '/html/body/script[4]')
    data = script.get_attribute('textContent').split('concat(')[1].strip()[:-2]
    data = json.loads(data)
    time.sleep(2)
    driver.quit()

    return data


def get_offer(item):
    offer = dict()

    offer["url"] = item['fullUrl']
    offer["offer_id"] = item["id"]

    timestamp = datetime.fromtimestamp(item['addedTimestamp'])  # получаем нормальную дату
    timestamp = datetime.strftime(timestamp, '%d-%m-%Y в %H:%M:%S')  # форматируем дату

    offer["data"] = timestamp
    offer["price"] = item['bargainTerms']['priceRur']
    offer["address"] = item['geo']['userInput']
    offer["area"] = item['totalArea']
    if item['roomsCount'] is None:
        offer["rooms"] = item['flatType']
    else:
        offer["rooms"] = item['roomsCount']
    offer["floor"] = item['floorNumber']
    offer["total_floor"] = item['building']['floorsCount']
    #     title = f"{item['roomsCount']}-к, {item['totalArea']} м2, {item['floorNumber']}/{item['building']['floorsCount']} этаж"

    return offer


def get_offers(data):
    offers = list()

    for key in data:
        if 'initialState' in key['key']:
            entities = key['value']['results']['offers']
            for item in entities:
                offer = get_offer(item)
                check_database(offer)


def main():
    url = "https://kazan.cian.ru/cat.php?deal_type=rent&engine_version=2&is_by_homeowner=1&offer_type=flat&region=4777&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room7=1&room9=1&sort=creation_date_desc&type=4"
    data = get_json(url)
    offers = get_offers(data)

    # with open('f.json', 'w', encoding='utf-8') as f:
    #     json.dump(data, f, ensure_ascii=False)


if __name__ == '__main__':
    main()
