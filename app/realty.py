import sqlite3
import requests
from app.config import token, chat_id


def check_database(offer):
    offer_id = offer["offer_id"]
    with sqlite3.connect('../db/realty.db') as connection:  # подключаемся к bd
        cursor = connection.cursor()
        cursor.execute("""
            SELECT offer_id FROM offers WHERE offer_id = (?)
        """, (offer_id,))  # !
        result = cursor.fetchone()  # показывает что база данных получила
        if result is None:
            cursor.execute("""
                INSERT INTO offers
                VALUES (NULL, :url, :offer_id, :data, :price,
                    :address, :area, :rooms, :floor, :total_floor)
            """, offer)
            connection.commit()  # Соханение данных
            print(f'Объявление {offer_id} добавлено в базу данных')
            send_telegram(offer=offer)

def format_text(offer):
    title = f"{offer['rooms']}, {offer['area']} м2, {offer['floor']}/{offer['total_floor']}"
    data = offer['data'][:-3]

    text = f"""
{offer['price']} ₽
<a href='{offer['url']}'>{title}</a>
{offer['address']}
{data}
    """
    return text


def send_telegram(offer):
    text = format_text(offer)
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }

    response = requests.post(url=url, data=data)
    print(response)


def main():
    offer = {'price': '45000', 'rooms': '1-к квартира'}
    send_telegram(offer=offer)


if __name__ == '__main__':
    main()
