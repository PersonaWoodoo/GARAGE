import sqlite3
import json

conn = sqlite3.connect("car_game.db", check_same_thread=False)
cursor = conn.cursor()

# Таблица пользователей (была)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER DEFAULT 1000,
    garage TEXT DEFAULT '[]'
)
""")

# Таблица машин (была)
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

# ========== НОВЫЕ ТАБЛИЦЫ ДЛЯ ПЛАТЕЖЕЙ ==========

# Таблица заявок на пополнение
cursor.execute("""
CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id TEXT UNIQUE,
    user_id INTEGER,
    username TEXT,
    currency TEXT,
    amount INTEGER,
    amount_with_fee INTEGER,
    status TEXT DEFAULT 'pending',
    screenshot_file_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Таблица заявок на вывод
cursor.execute("""
CREATE TABLE IF NOT EXISTS withdrawals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id TEXT UNIQUE,
    user_id INTEGER,
    username TEXT,
    currency TEXT,
    amount INTEGER,
    amount_after_fee INTEGER,
    fee INTEGER,
    wallet_address TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Таблица для хранения настроек (банк админа)
cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

# Добавляем настройки по умолчанию
cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('bank_username', '@debashev')")
cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('deposit_fee_percent', '10')")
cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('withdraw_fee_percent', '5')")
cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('min_deposit', '50000')")
cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('min_withdraw', '50000')")

conn.commit()

# ========== ОСНОВНЫЕ ФУНКЦИИ ==========

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

# ========== ПЛАТЕЖНЫЕ ФУНКЦИИ ==========

def generate_operation_id():
    """Генерация уникального ID операции"""
    import random
    import string
    while True:
        op_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        cursor.execute("SELECT 1 FROM deposits WHERE operation_id = ? UNION SELECT 1 FROM withdrawals WHERE operation_id = ?", (op_id, op_id))
        if not cursor.fetchone():
            return op_id

def create_deposit_request(user_id, username, currency, amount):
    """Создание заявки на пополнение"""
    fee_percent = int(cursor.execute("SELECT value FROM settings WHERE key = 'deposit_fee_percent'").fetchone()[0])
    amount_with_fee = int(amount * (1 + fee_percent / 100))
    operation_id = generate_operation_id()
    
    cursor.execute("""
        INSERT INTO deposits (operation_id, user_id, username, currency, amount, amount_with_fee, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    """, (operation_id, user_id, username, currency, amount, amount_with_fee))
    conn.commit()
    return operation_id, amount_with_fee

def create_withdraw_request(user_id, username, currency, amount, wallet_address):
    """Создание заявки на вывод"""
    fee_percent = int(cursor.execute("SELECT value FROM settings WHERE key = 'withdraw_fee_percent'").fetchone()[0])
    fee = int(amount * fee_percent / 100)
    amount_after_fee = amount - fee
    operation_id = generate_operation_id()
    
    cursor.execute("""
        INSERT INTO withdrawals (operation_id, user_id, username, currency, amount, amount_after_fee, fee, wallet_address, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (operation_id, user_id, username, currency, amount, amount_after_fee, fee, wallet_address))
    conn.commit()
    return operation_id, amount_after_fee, fee

def get_pending_deposits():
    """Получить все pending заявки на пополнение"""
    cursor.execute("SELECT * FROM deposits WHERE status = 'pending' ORDER BY created_at DESC")
    return cursor.fetchall()

def get_pending_withdrawals():
    """Получить все pending заявки на вывод"""
    cursor.execute("SELECT * FROM withdrawals WHERE status = 'pending' ORDER BY created_at DESC")
    return cursor.fetchall()

def approve_deposit(operation_id):
    """Одобрить пополнение"""
    cursor.execute("SELECT user_id, amount FROM deposits WHERE operation_id = ?", (operation_id,))
    deposit = cursor.fetchone()
    if deposit:
        user_id, amount = deposit
        user = get_user(user_id)
        new_balance = user[2] + amount
        update_user_balance(user_id, new_balance)
        cursor.execute("UPDATE deposits SET status = 'approved' WHERE operation_id = ?", (operation_id,))
        conn.commit()
        return True
    return False

def approve_withdraw(operation_id):
    """Одобрить вывод (административно)"""
    cursor.execute("UPDATE withdrawals SET status = 'approved' WHERE operation_id = ?", (operation_id,))
    conn.commit()
    return True

def reject_request(operation_id, table):
    """Отклонить заявку"""
    cursor.execute(f"UPDATE {table} SET status = 'rejected' WHERE operation_id = ?", (operation_id,))
    conn.commit()

def get_setting(key):
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    return row[0] if row else None

def update_screenshot(operation_id, file_id):
    cursor.execute("UPDATE deposits SET screenshot_file_id = ? WHERE operation_id = ?", (file_id, operation_id))
    conn.commit()
