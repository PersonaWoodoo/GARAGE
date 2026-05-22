from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========== ГЛАВНОЕ МЕНЮ (снизу) ==========
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🚗 Мой гараж", callback_data="my_garage")],
    [InlineKeyboardButton(text="💰 Баланс", callback_data="balance"),
     InlineKeyboardButton(text="💳 Пополнить", callback_data="deposit_menu")],
    [InlineKeyboardButton(text="🏆 Топ лидеров", callback_data="top"),
     InlineKeyboardButton(text="💸 Вывести", callback_data="withdraw_menu")],
    [InlineKeyboardButton(text="🎁 Контейнеры", callback_data="containers"),
     InlineKeyboardButton(text="🏪 Рынок", callback_data="market")],
    [InlineKeyboardButton(text="🔄 Обмен", callback_data="exchange_menu"),
     InlineKeyboardButton(text="⚡ Торги", callback_data="auctions")]
])

# ========== ВАЛЮТЫ ДЛЯ ПОПОЛНЕНИЯ ==========
currencies_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💎 GRAM", callback_data="currency_GRAM")],
    [InlineKeyboardButton(text="💰 USDT (TRC20)", callback_data="currency_USDT")],
    [InlineKeyboardButton(text="💵 BTC", callback_data="currency_BTC")],
    [InlineKeyboardButton(text="🪙 ETH", callback_data="currency_ETH")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
])

# ========== ПОДТВЕРЖДЕНИЕ ВЫВОДА ==========
def withdraw_confirm_keyboard(operation_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, подтвердить", callback_data=f"withdraw_confirm_{operation_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="withdraw_cancel")]
    ])

# ========== АДМИН ПАНЕЛЬ (платежи) ==========
admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Добавить машину", callback_data="admin_add_car")],
    [InlineKeyboardButton(text="📋 Список машин", callback_data="admin_list_cars")],
    [InlineKeyboardButton(text="💰 Пополнения (📥)", callback_data="admin_deposits")],
    [InlineKeyboardButton(text="💸 Выводы (📤)", callback_data="admin_withdrawals")],
    [InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings")],
    [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")]
])

def admin_deposits_keyboard(deposits):
    keyboard = []
    for d in deposits:
        keyboard.append([InlineKeyboardButton(
            text=f"#{d[1]} | {d[4]} | {d[5]}💰 | @{d[3]}",
            callback_data=f"admin_deposit_{d[1]}"
        )])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def admin_withdrawals_keyboard(withdrawals):
    keyboard = []
    for w in withdrawals:
        keyboard.append([InlineKeyboardButton(
            text=f"#{w[1]} | {w[4]} | {w[5]}💰 | @{w[3]}",
            callback_data=f"admin_withdraw_{w[1]}"
        )])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def admin_action_keyboard(operation_id, type_):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{type_}_{operation_id}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{type_}_{operation_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
    ])

# ========== ГАРАЖ (было) ==========
def garage_keyboard(page, total_pages, car_id=None):
    keyboard = []
    if car_id:
        keyboard.append([InlineKeyboardButton(text="💸 Продать", callback_data=f"sell_{car_id}")])
        keyboard.append([InlineKeyboardButton(text="🔄 Предложить обмен", callback_data=f"offer_exchange_{car_id}")])
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"garage_page_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="none"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"garage_page_{page+1}"))
    keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ========== КОНТЕЙНЕРЫ ==========
containers_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📦 Обычный (100 монет)", callback_data="open_container_обычный")],
    [InlineKeyboardButton(text="💎 Эпический (500 монет)", callback_data="open_container_эпический")],
    [InlineKeyboardButton(text="👑 Легендарный (2000 монет)", callback_data="open_container_легендарный")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
])

# ========== РЫНОК ==========
def market_keyboard(cars):
    keyboard = []
    for car in cars[:5]:
        keyboard.append([InlineKeyboardButton(
            text=f"🚗 {car[1]} - {car[3]}💰",
            callback_data=f"buy_{car[0]}"
        )])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ========== ОБМЕН ==========
def exchange_keyboard(users):
    keyboard = []
    for user in users[:5]:
        keyboard.append([InlineKeyboardButton(
            text=f"👤 @{user[1] or 'anon'} (машин: {len(eval(user[2]))})",
            callback_data=f"exchange_user_{user[0]}"
        )])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ========== ТОРГИ ==========
auctions_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Создать торг", callback_data="create_auction")],
    [InlineKeyboardButton(text="📋 Активные торги", callback_data="active_auctions")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
])

confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
     InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no")]
])

back_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
])
