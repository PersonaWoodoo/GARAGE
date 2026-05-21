import asyncio
import json
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, ADMIN_ID, RARITIES, CONTAINERS
from db import get_user, update_user_balance, update_user_garage, get_all_cars, add_car, cursor, conn
from keyboards import (
    main_menu, garage_keyboard, containers_keyboard, 
    market_keyboard, exchange_keyboard, auctions_keyboard,
    confirm_keyboard, admin_menu, back_button
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== FSM ДЛЯ АДМИНА ==========
class AdminAddCar(StatesGroup):
    waiting_for_photo = State()
    waiting_for_name = State()
    waiting_for_rarity = State()
    waiting_for_price = State()
    waiting_for_description = State()

# ========== FSM ДЛЯ ОБМЕНА ==========
class ExchangeState(StatesGroup):
    waiting_for_user = State()
    waiting_for_my_car = State()
    waiting_for_their_car = State()

# ========== FSM ДЛЯ ТОРГОВ ==========
class AuctionState(StatesGroup):
    waiting_for_container_type = State()
    waiting_for_start_price = State()

# ========== КОМАНДА СТАРТ ==========
@dp.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    get_user(user_id, username)
    await message.answer(
        "🚗 Добро пожаловать в Car Game!\n\n"
        "💰 У тебя 1000 монет для старта\n"
        "🎁 Открывай контейнеры, собирай машины\n"
        "💎 Стань самым богатым игроком!",
        reply_markup=main_menu
    )

# ========== АДМИН ПАНЕЛЬ (скрытая команда) ==========
@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Нет доступа")
        return
    await message.answer("👑 Админ панель", reply_markup=admin_menu)

# ========== ОБРАБОТЧИКИ КНОПОК ==========
@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "🚗 Главное меню",
        reply_markup=main_menu
    )
    await callback.answer()

# ----- Мой гараж -----
@dp.callback_query(F.data == "my_garage")
async def my_garage(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    garage = json.loads(user[3])
    
    if not garage:
        await callback.message.edit_text(
            "🚫 У тебя пока нет машин\n🎁 Открой контейнер!",
            reply_markup=back_button
        )
        await callback.answer()
        return
    
    # Сохраняем в кэш текущую страницу
    await callback.message.edit_text(
        f"🚗 Твой гараж: {len(garage)} машин(ы)\n\n"
        f"🏷️ Нажми на кнопку машины чтобы продать",
        reply_markup=garage_keyboard(0, (len(garage)+4)//5)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("garage_page_"))
async def garage_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    user = get_user(callback.from_user.id)
    garage = json.loads(user[3])
    total_pages = (len(garage) + 4) // 5
    
    await callback.message.edit_reply_markup(
        reply_markup=garage_keyboard(page, total_pages)
    )
    await callback.answer()

# ----- Баланс -----
@dp.callback_query(F.data == "balance")
async def show_balance(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    await callback.message.edit_text(
        f"💰 Твой баланс: {user[2]} монет\n\n"
        f"🏆 Твоя коллекция: {len(json.loads(user[3]))} машин",
        reply_markup=back_button
    )
    await callback.answer()

# ----- Топ лидеров -----
@dp.callback_query(F.data == "top")
async def top_players(callback: CallbackQuery):
    cursor.execute("SELECT user_id, username, balance FROM users ORDER BY balance DESC LIMIT 10")
    top = cursor.fetchall()
    
    text = "🏆 ТОП 10 БОГАТЫХ ИГРОКОВ 🏆\n\n"
    for i, (uid, name, balance) in enumerate(top, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔹"
        text += f"{medal} {i}. @{name or 'anon'} — {balance} 💰\n"
    
    await callback.message.edit_text(text, reply_markup=back_button)
    await callback.answer()

# ----- Контейнеры -----
@dp.callback_query(F.data == "containers")
async def show_containers(callback: CallbackQuery):
    text = "🎁 **Контейнеры**\n\n"
    for name, data in CONTAINERS.items():
        text += f"{data['emoji']} {data['name']} — {data['price']} монет\n"
    await callback.message.edit_text(text, reply_markup=containers_keyboard)
    await callback.answer()

@dp.callback_query(F.data.startswith("open_container_"))
async def open_container(callback: CallbackQuery):
    container_type = callback.data.split("_")[2]
    container = CONTAINERS[container_type]
    
    user = get_user(callback.from_user.id)
    if user[2] < container["price"]:
        await callback.answer(f"❌ Не хватает монет! Нужно {container['price']}", show_alert=True)
        return
    
    # Список всех машин
    all_cars = get_all_cars()
    if not all_cars:
        await callback.answer("❌ Нет машин в базе! Добавьте через админку", show_alert=True)
        return
    
    # Рандомная машина с учетом редкости
    car = random.choice(all_cars)
    
    # Добавляем в гараж
    garage = json.loads(user[3])
    garage.append({
        "id": car[0],
        "name": car[1],
        "rarity": car[2],
        "price": car[3]
    })
    
    # Списываем монеты
    new_balance = user[2] - container["price"]
    update_user_balance(callback.from_user.id, new_balance)
    update_user_garage(callback.from_user.id, json.dumps(garage))
    
    rarity_emoji = RARITIES.get(car[2], {}).get("emoji", "🚗")
    await callback.message.edit_text(
        f"{container['emoji']} Ты открыл {container['name']}!\n\n"
        f"{rarity_emoji} Тебе выпала: **{car[1]}**\n"
        f"✨ Редкость: {car[2]}\n"
        f"💰 Цена продажи: {car[3]} монет",
        reply_markup=back_button
    )
    await callback.answer("🎉 Поздравляю!")

# ----- Рынок (покупка) -----
@dp.callback_query(F.data == "market")
async def show_market(callback: CallbackQuery):
    cars = get_all_cars()
    await callback.message.edit_text(
        "🏪 Рынок машин\n💰 Покупай напрямую у бота:",
        reply_markup=market_keyboard(cars)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def buy_car(callback: CallbackQuery):
    car_id = int(callback.data.split("_")[1])
    cursor.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
    car = cursor.fetchone()
    
    user = get_user(callback.from_user.id)
    if user[2] < car[3]:
        await callback.answer(f"❌ Нужно {car[3]} монет!", show_alert=True)
        return
    
    garage = json.loads(user[3])
    garage.append({"id": car[0], "name": car[1], "rarity": car[2], "price": car[3]})
    
    new_balance = user[2] - car[3]
    update_user_balance(callback.from_user.id, new_balance)
    update_user_garage(callback.from_user.id, json.dumps(garage))
    
    await callback.message.edit_text(
        f"✅ Ты купил {car[1]} за {car[3]} монет!",
        reply_markup=back_button
    )
    await callback.answer()

# ----- Продажа из гаража -----
@dp.callback_query(F.data.startswith("sell_"))
async def sell_car(callback: CallbackQuery):
    car_id = int(callback.data.split("_")[1])
    user = get_user(callback.from_user.id)
    garage = json.loads(user[3])
    
    for i, car in enumerate(garage):
        if car["id"] == car_id:
            price = car["price"] // 2  # Продажа за полцены
            garage.pop(i)
            new_balance = user[2] + price
            update_user_balance(callback.from_user.id, new_balance)
            update_user_garage(callback.from_user.id, json.dumps(garage))
            await callback.message.edit_text(
                f"💸 Ты продал {car['name']} за {price} монет!",
                reply_markup=back_button
            )
            await callback.answer()
            return
    
    await callback.answer("❌ Машина не найдена", show_alert=True)

# ========== АДМИН КОМАНДЫ ==========
@dp.callback_query(F.data == "admin_add_car")
async def admin_add_car_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет доступа")
        return
    await callback.message.edit_text("📸 Отправь фото машины (одно фото)")
    await state.set_state(AdminAddCar.waiting_for_photo)
    await callback.answer()

@dp.message(AdminAddCar.waiting_for_photo, F.photo)
async def admin_get_photo(message: Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo=photo_file_id)
    await message.answer("✏️ Введи название машины")
    await state.set_state(AdminAddCar.waiting_for_name)

@dp.message(AdminAddCar.waiting_for_name)
async def admin_get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    
    rarity_list = "\n".join([f"{e['emoji']} {r}" for r, e in RARITIES.items()])
    await message.answer(f"🌟 Выбери редкость:\n{rarity_list}\n\nНапиши название редкости из списка")
    await state.set_state(AdminAddCar.waiting_for_rarity)

@dp.message(AdminAddCar.waiting_for_rarity)
async def admin_get_rarity(message: Message, state: FSMContext):
    rarity = message.text.lower()
    if rarity not in RARITIES:
        await message.answer("❌ Неверная редкость! Напиши из списка")
        return
    await state.update_data(rarity=rarity)
    await message.answer("💰 Введи цену продажи (в монетах)")
    await state.set_state(AdminAddCar.waiting_for_price)

@dp.message(AdminAddCar.waiting_for_price)
async def admin_get_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price=price)
        await message.answer("📝 Введи описание машины")
        await state.set_state(AdminAddCar.waiting_for_description)
    except:
        await message.answer("❌ Введи число!")

@dp.message(AdminAddCar.waiting_for_description)
async def admin_get_description(message: Message, state: FSMContext):
    data = await state.get_data()
    add_car(
        name=data['name'],
        rarity=data['rarity'],
        price=data['price'],
        description=message.text,
        photo_file_id=data['photo']
    )
    await message.answer(f"✅ Машина {data['name']} добавлена!", reply_markup=admin_menu)
    await state.clear()

@dp.callback_query(F.data == "admin_list_cars")
async def admin_list_cars(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет доступа")
        return
    cars = get_all_cars()
    if not cars:
        await callback.message.edit_text("🚫 Нет машин", reply_markup=admin_menu)
        return
    
    text = "📋 Список машин:\n\n"
    for car in cars[:10]:
        text += f"🆔 {car[0]} | {car[1]} | {car[2]} | {car[3]}💰\n"
    await callback.message.edit_text(text, reply_markup=admin_menu)
    await callback.answer()

@dp.callback_query(F.data == "admin_give_money")
async def admin_give_money_start(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет доступа")
        return
    await callback.message.edit_text("📝 Формат: ID_пользователя сумма\nПример: 123456789 5000")
    await callback.answer()

@dp.message(F.text, lambda m: m.from_user.id == ADMIN_ID and m.text.startswith("admin_give_money"))
async def admin_give_money(message: Message):
    try:
        parts = message.text.replace("admin_give_money", "").strip().split()
        user_id = int(parts[0])
        amount = int(parts[1])
        user = get_user(user_id)
        new_balance = user[2] + amount
        update_user_balance(user_id, new_balance)
        await message.answer(f"✅ Выдано {amount} монет пользователю {user_id}")
    except:
        await message.answer("❌ Ошибка! Формат: admin_give_money 123456789 5000")

# ========== ОБМЕН МАШИНАМИ ==========
@dp.callback_query(F.data == "exchange_menu")
async def exchange_menu(callback: CallbackQuery):
    cursor.execute("SELECT user_id, username, garage FROM users WHERE user_id != ?", (callback.from_user.id,))
    users = cursor.fetchall()
    await callback.message.edit_text(
        "🔄 Выбери игрока для обмена:",
        reply_markup=exchange_keyboard(users)
    )
    await callback.answer()

# ========== ТОРГИ ==========
@dp.callback_query(F.data == "auctions")
async def auctions_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚡ Торги за контейнеры\n\n"
        "Создай торг за контейнер, игроки будут повышать ставки!",
        reply_markup=auctions_keyboard
    )
    await callback.answer()

async def main():
    print("🚗 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
