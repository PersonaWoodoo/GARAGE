import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8912979982:AAHlltBsKhCkqSqU4yqQpNtr_zWDRCOGZpw")  # Твой токен бота
ADMIN_ID = 8478884644  # Твой ID

# Редкости и их эмодзи/цвета
RARITIES = {
    "обычная": {"emoji": "⚪", "color": "#808080", "price_multiplier": 1.0},
    "улучшенная": {"emoji": "🟢", "color": "#00FF00", "price_multiplier": 1.5},
    "редкая": {"emoji": "🔵", "color": "#0088FF", "price_multiplier": 2.5},
    "эпическая": {"emoji": "🟣", "color": "#AA00FF", "price_multiplier": 5.0},
    "легендарная": {"emoji": "🟡", "color": "#FFD700", "price_multiplier": 10.0},
    "уникальная": {"emoji": "🌈", "color": "#FF00FF", "price_multiplier": 25.0},
}
