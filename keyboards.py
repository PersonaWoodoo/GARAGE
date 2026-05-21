from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚗 Мой гараж")],
        [KeyboardButton(text="💰 Баланс"), KeyboardButton(text="🎁 Контейнеры")],
        [KeyboardButton(text="🏪 Рынок"), KeyboardButton(text="📦 Обмен машин")]
    ],
    resize_keyboard=True
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить машину")],
        [KeyboardButton(text="📋 Список машин")],
        [KeyboardButton(text="🔙 В главное меню")]
    ],
    resize_keyboard=True
)

rarity_buttons = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⚪ Обычная", callback_data="rarity_обычная")],
    [InlineKeyboardButton(text="🟢 Улучшенная", callback_data="rarity_улучшенная")],
    [InlineKeyboardButton(text="🔵 Редкая", callback_data="rarity_редкая")],
    [InlineKeyboardButton(text="🟣 Эпическая", callback_data="rarity_эпическая")],
    [InlineKeyboardButton(text="🟡 Легендарная", callback_data="rarity_легендарная")],
    [InlineKeyboardButton(text="🌈 Уникальная", callback_data="rarity_уникальная")]
])
