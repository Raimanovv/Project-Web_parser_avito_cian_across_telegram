import sqlite3


def main():
    connection = sqlite3.connect('realty.db')
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            offer_id INTEGER,
            data TEXT,
            price INTEGER,
            address TEXT,
            area INT,
            rooms TEXT,
            floor INTEGER,
            total_floor INTEGER            
        )
    """)
    connection.close()


if __name__ == '__main__':
    main()
