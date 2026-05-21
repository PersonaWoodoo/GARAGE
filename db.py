import sqlite3

conn = sqlite3.connect("car_game.db", check_same_thread=False)
cursor = conn.cursor()

# Таблица пользователей
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER DEFAULT 1000,
    garage TEXT DEFAULT '[]'
)
""")

# Таблица машин (админ добавляет)
cursor.execute("""
CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    rarity TEXT,
    price INTEGER,
    description TEXT,
    photo_file_id TEXT
)
""")

# Таблица контейнеров
cursor.execute("""
CREATE TABLE IF NOT EXISTS containers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price INTEGER,
    rarity_distribution TEXT  -- JSON строка
)
""")

conn.commit()

def get_user(user_id, username=""):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        return (user_id, username, 1000, "[]")
    return user

def update_user_garage(user_id, garage_json):
    cursor.execute("UPDATE users SET garage = ? WHERE user_id = ?", (garage_json, user_id))
    conn.commit()

def update_user_balance(user_id, new_balance):
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()

def add_car(name, rarity, price, description, photo_file_id):
    cursor.execute("INSERT INTO cars (name, rarity, price, description, photo_file_id) VALUES (?, ?, ?, ?, ?)",
                   (name, rarity, price, description, photo_file_id))
    conn.commit()

def get_all_cars():
    cursor.execute("SELECT * FROM cars")
    return cursor.fetchall()
