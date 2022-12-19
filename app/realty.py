import sqlite3


def check_database(offer):
    offer_id = offer["offer_id"]

    connection = sqlite3.connect('../db/realty.db')  # подключаемся к bd
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

    connection.close()
