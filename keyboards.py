from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========== ГЛАВНОЕ МЕНЮ (снизу) ==========
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🚗 Мой гараж", callback_data="my_garage")],
    [InlineKeyboardButton(text="💰 Баланс", callback_data="balance"),
     InlineKeyboardButton(text="🏆 Топ лидеров", callback_data="top")],
    [InlineKeyboardButton(text="🎁 Контейнеры", callback_data="containers"),
     InlineKeyboardButton(text="🏪 Рынок", callback_data="market")],
    [InlineKeyboardButton(text="🔄 Обмен машинами", callback_data="exchange_menu"),
     InlineKeyboardButton(text="⚡ Торги", callback_data="auctions")]
])

# ========== ГАРАЖ (пагинация) ==========
def garage_keyboard(page, total_pages, car_id=None):
    keyboard = []
    
    # Информация о машине (если выбрана)
    if car_id:
        keyboard.append([InlineKeyboardButton(text="💸 Продать", callback_data=f"sell_{car_id}")])
        keyboard.append([InlineKeyboardButton(text="🔄 Предложить обмен", callback_data=f"offer_exchange_{car_id}")])
    
    # Пагинация
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
    for car in cars[:5]:  # по 5 машин на странице
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
            text=f"👤 {user[1]} (машин: {len(eval(user[3]))})",
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

# ========== ПОТВЕРЖДЕНИЯ ==========
confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
     InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no")]
])

# ========== АДМИН МЕНЮ (по команде /admin) ==========
admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Добавить машину", callback_data="admin_add_car")],
    [InlineKeyboardButton(text="📋 Список машин", callback_data="admin_list_cars")],
    [InlineKeyboardButton(text="💰 Выдать монеты", callback_data="admin_give_money")],
    [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
    [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")]
])

# ========== ВСПОМОГАТЕЛЬНЫЕ ==========
back_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
])
