from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from urllib.parse import unquote
from datetime import datetime
import json
import time
import sqlite3

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


def check_database(item):
    offer_id = item['id']
    with sqlite3.connect('../db/realty.db') as connection:
        cursor = connection.cursor()
        cursor.execute("""
                SELECT offer_id FROM offers WHERE offer_id = (?)
            """, (offer_id,))  # !
        result = cursor.fetchone()  # показывает что база данных получила
        if result is None:
            offer = get_offer(item)
            cursor.execute("""
                    INSERT INTO offers
                    VALUES (NULL, :url, :offer_id, :data, :price, 
                        :address, :area, :rooms, :floor, :total_floor)
                """, offer)
            connection.commit()  # Сохранение данных
            print(f'Объявление {offer_id} добавлено в базу данных')


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
                if "item" in item["type"]:
                    check_database(item)


def main():
    url = "https://www.avito.ru/kazan/kvartiry/sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg?cd=1&s=104&user=1"
    data = get_json(url)
    offers = get_offers(data)


if __name__ == '__main__':
    main()
