import asyncio
import json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command

from config import BOT_TOKEN, ADMIN_ID
from db import get_user, update_user_balance, get_all_cars
from keyboards import main_menu, admin_menu
from admin import admin_router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключаем админ-роутер
dp.include_router(admin_router)

# Старт
@dp.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    get_user(user_id, username)
    
    if user_id == ADMIN_ID:
        await message.answer("👑 Привет, Админ!", reply_markup=admin_menu)
    else:
        await message.answer("🚗 Добро пожаловать в Car Game!", reply_markup=main_menu)

# Мой гараж (заглушка)
@dp.message(F.text == "🚗 Мой гараж")
async def my_garage(message: Message):
    user = get_user(message.from_user.id)
    garage = json.loads(user[3])
    if not garage:
        await message.answer("🚫 У тебя пока нет машин")
    else:
        await message.answer(f"🚘 У тебя {len(garage)} машин(ы)")

# Баланс
@dp.message(F.text == "💰 Баланс")
async def balance(message: Message):
    user = get_user(message.from_user.id)
    await message.answer(f"💰 Твой баланс: {user[2]} монет")

# Кнопка назад в главное меню (для админа)
@dp.message(F.text == "🔙 В главное меню")
async def back_to_main(message: Message):
    await message.answer("Главное меню", reply_markup=main_menu)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
