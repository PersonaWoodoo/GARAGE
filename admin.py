from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID, RARITIES
from db import add_car, get_all_cars
from states import AdminAddCar
from keyboards import admin_menu, rarity_buttons

admin_router = Router()

# Проверка админа
def is_admin(user_id):
    return user_id == ADMIN_ID

# Главное админ-меню
@admin_router.message(F.text == "➕ Добавить машину")
async def add_car_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("📸 Отправь фото машины (одно фото)")
    await state.set_state(AdminAddCar.waiting_for_photo)

@admin_router.message(AdminAddCar.waiting_for_photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo=photo_file_id)
    await message.answer("✏️ Введи название машины (например: BMW M5 F90)")
    await state.set_state(AdminAddCar.waiting_for_name)

@admin_router.message(AdminAddCar.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("🌟 Выбери редкость:", reply_markup=rarity_buttons)
    await state.set_state(AdminAddCar.waiting_for_rarity)

@admin_router.callback_query(AdminAddCar.waiting_for_rarity)
async def get_rarity(callback: CallbackQuery, state: FSMContext):
    rarity = callback.data.replace("rarity_", "")
    await state.update_data(rarity=rarity)
    await callback.message.answer(f"💰 Введи цену продажи (в монетах)")
    await state.set_state(AdminAddCar.waiting_for_price)
    await callback.answer()

@admin_router.message(AdminAddCar.waiting_for_price)
async def get_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price=price)
        await message.answer("📝 Введи описание машины")
        await state.set_state(AdminAddCar.waiting_for_description)
    except:
        await message.answer("❌ Введи число!")

@admin_router.message(AdminAddCar.waiting_for_description)
async def get_description(message: Message, state: FSMContext):
    data = await state.get_data()
    add_car(
        name=data['name'],
        rarity=data['rarity'],
        price=data['price'],
        description=message.text,
        photo_file_id=data['photo']
    )
    await message.answer(f"✅ Машина {data['name']} добавлена!\nРедкость: {RARITIES[data['rarity']]['emoji']} {data['rarity']}")
    await state.clear()

# Просмотр всех машин
@admin_router.message(F.text == "📋 Список машин")
async def list_cars(message: Message):
    if not is_admin(message.from_user.id):
        return
    cars = get_all_cars()
    if not cars:
        await message.answer("🚫 Нет машин")
        return
    for car in cars[:10]:  # первые 10
        await message.answer_photo(
            car[5],
            caption=f"🚗 {car[1]}\n✨ {car[2]}\n💰 {car[3]}\n📖 {car[4]}"
        )
