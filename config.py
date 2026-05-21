import os
from dotenv import load_dotenv

# Загружаем .env файл (только для локального запуска)
load_dotenv()

# Пробуем получить токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Если токен не найден (например на BotHost если забыли добавить переменную)
if not BOT_TOKEN:
    # ⚠️ ВСТАВЬ СВОЙ ТОКЕН СЮДА (временно, пока не настроишь переменные в BotHost)
    BOT_TOKEN ="8912979982:AAHlltBsKhCkqSqU4yqQpNtr_zWDRCOGZpw"  # ← Замени на свой токен!
    print("⚠️ ВНИМАНИЕ: Используется токен из config.py, а не из переменных окружения!")
    print("⚠️ Рекомендуется добавить переменную BOT_TOKEN в настройках BotHost")

# Твой ID администратора
ADMIN_ID = 8478884644

# Редкости и их параметры
RARITIES = {
    "обычная": {"emoji": "⚪", "color": "#808080", "price_multiplier": 1.0, "chance": 50},
    "улучшенная": {"emoji": "🟢", "color": "#00FF00", "price_multiplier": 1.5, "chance": 25},
    "редкая": {"emoji": "🔵", "color": "#0088FF", "price_multiplier": 2.5, "chance": 15},
    "эпическая": {"emoji": "🟣", "color": "#AA00FF", "price_multiplier": 5.0, "chance": 7},
    "легендарная": {"emoji": "🟡", "color": "#FFD700", "price_multiplier": 10.0, "chance": 2.5},
    "уникальная": {"emoji": "🌈", "color": "#FF00FF", "price_multiplier": 25.0, "chance": 0.5}
}

# Типы контейнеров
CONTAINERS = {
    "обычный": {
        "price": 100,
        "emoji": "📦",
        "name": "Обычный контейнер",
        "rarity_modifier": 1.0  # множитель шансов
    },
    "эпический": {
        "price": 500,
        "emoji": "💎",
        "name": "Эпический контейнер",
        "rarity_modifier": 1.5  # повышает шанс редких
    },
    "легендарный": {
        "price": 2000,
        "emoji": "👑",
        "name": "Легендарный контейнер",
        "rarity_modifier": 2.5  # сильно повышает шанс редких
    }
}

# Проверка при запуске
if not BOT_TOKEN or BOT_TOKEN == "1234567890:ABCdefGHIjklmNOPqrstUVWxyz":
    print("❌ ОШИБКА: Токен бота не настроен!")
    print("✅ Добавь переменную BOT_TOKEN в настройках BotHost")
    print("✅ Или вставь свой токен в config.py вместо заглушки")
    exit(1)

print("✅ Конфигурация загружена успешно")
print(f"🤖 Админ ID: {ADMIN_ID}")
print(f"📊 Доступно редкостей: {len(RARITIES)}")
print(f"🎁 Доступно контейнеров: {len(CONTAINERS)}")
