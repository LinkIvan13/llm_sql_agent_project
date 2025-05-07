# -*- coding: utf-8 -*-
import sqlite3
from typing import Optional, List, Tuple


def get_connection(db_path: str = "db/products.db") -> sqlite3.Connection:
    """Создаёт соединение с SQLite-базой данных."""
    return sqlite3.connect(db_path)

def add_product(name: str, price: float, category: str, description: str,
                    image_bytes: Optional[bytes] = None) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, category, description, image) VALUES (?, ?, ?, ?, ?)",
            (name.strip(), price, category.strip(), description.strip(), image_bytes)
        )
        conn.commit()
        conn.close()



def get_all_products() -> List[Tuple]:
    """Возвращает все товары из базы данных."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, category, description, image FROM products")
    products = cursor.fetchall()
    conn.close()
    return products


def update_product(product_id: int, name: str, price: float, category: str,
                   description: Optional[str], image_bytes: Optional[bytes]) -> None:
    """Обновляет все поля товара, включая изображение."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET name = ?, price = ?, category = ?, description = ?, image = ?
        WHERE id = ?
    """, (name.strip(), price, category.strip(), description.strip(), image_bytes, product_id))
    conn.commit()
    conn.close()




def delete_product(product_id: int) -> None:
    """Удаляет товар по ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def log_query(user_query: str, sql_query: str, result: str) -> None:
    """Сохраняет информацию о выполненном запросе в историю."""
    conn = get_connection()
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
    cursor.execute(
        "INSERT INTO query_history (user_query, sql_query, result) VALUES (?, ?, ?)",
        (user_query, sql_query, result)
    )
    conn.commit()
    conn.close()


def get_query_history(limit: int = 50) -> List[Tuple]:
    """Возвращает историю запросов (по умолчанию — последние 50)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, user_query, sql_query, result
        FROM query_history
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    history = cursor.fetchall()
    conn.close()
    return history

def init_telegram_logs():
    """Создаёт таблицу логов Telegram-запросов, если она не существует."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telegram_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            username TEXT,
            user_query TEXT,
            result TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_telegram_query(user_id: int, username: str, query: str, result: str):
    """Сохраняет лог запроса Telegram-пользователя."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO telegram_logs (user_id, username, user_query, result)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, query, result))
    conn.commit()
    conn.close()