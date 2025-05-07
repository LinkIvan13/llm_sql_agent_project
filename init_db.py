import sqlite3
import os

DB_PATH = "db/products.db"


def initialize_products_table():
    """Создаёт таблицу products с колонкой image_url и тестовыми данными (однократно)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL,
        category TEXT,
        description TEXT,
        image_url TEXT
    )
    ''')



    # Проверим, есть ли уже записи
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    if count == 0:
        products = [
            ("Кофемашина", 19999.99, "Техника", "Автоматическая кофемашина с капучинатором", "https://example.com/coffee.jpg"),
            ("Смартфон", 45999.00, "Электроника", "Смартфон с OLED-дисплеем и 5G", "https://example.com/smartphone.jpg"),
            ("Книга по Python", 899.50, "Книги", "Пошаговое руководство по Python", "https://example.com/python_book.jpg"),
            ("Ноутбук", 89999.00, "Электроника", "Лёгкий ноутбук с 16 ГБ ОЗУ и SSD", "https://example.com/laptop.jpg"),
            ("Фен", 2999.90, "Бытовая техника", "Компактный фен с ионизацией", "")
        ]

        cursor.executemany('''
        INSERT INTO products (name, price, category, description, image_url)
        VALUES (?, ?, ?, ?, ?)
        ''', products)

        print("✅ Таблица products создана и заполнена тестовыми данными.")
    else:
        print("ℹ️ Таблица products уже содержит данные. Пропускаем заполнение.")

    conn.commit()
    conn.close()


def add_image_column():
    conn = sqlite3.connect("db/products.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(products)")
    columns = [col[1] for col in cursor.fetchall()]
    if "image" not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN image BLOB")
        print("✅ Колонка image (BLOB) добавлена.")
    else:
        print("ℹ️ Колонка image уже существует.")
    conn.commit()
    conn.close()




def initialize_query_history_table():
    """Создаёт таблицу query_history (если отсутствует)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS query_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        user_query TEXT,
        sql_query TEXT,
        result TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Таблица query_history готова.")


def main():
    initialize_products_table()
    add_image_column()
    initialize_query_history_table()


if __name__ == "__main__":
    main()

