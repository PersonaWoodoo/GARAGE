# ========== ПОПОЛНЕНИЕ ==========
@dp.callback_query(F.data == "deposit_menu")
async def deposit_menu(callback: CallbackQuery):
    min_deposit = get_setting('min_deposit')
    fee = get_setting('deposit_fee_percent')
    await callback.message.edit_text(
        f"💳 **Пополнение баланса**\n\n"
        f"💰 Минимальная сумма: {min_deposit} монет\n"
        f"📊 Комиссия: {fee}% (при пополнении)\n\n"
        f"Выбери валюту:",
        reply_markup=currencies_menu
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("currency_"))
async def select_currency(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[1]
    await state.update_data(currency=currency)
    min_deposit = get_setting('min_deposit')
    await callback.message.edit_text(
        f"💎 Валюта: {currency}\n\n"
        f"💰 Минимальная сумма пополнения: {min_deposit}\n"
        f"📝 Введи сумму пополнения (комиссия 10% добавится автоматически):"
    )
    await state.set_state(DepositState.waiting_for_amount)
    await callback.answer()

@dp.message(DepositState.waiting_for_amount)
async def process_deposit_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        min_deposit = int(get_setting('min_deposit'))
        
        if amount < min_deposit:
            await message.answer(f"❌ Минимальная сумма: {min_deposit}")
            return
        
        data = await state.get_data()
        currency = data['currency']
        user = get_user(message.from_user.id, message.from_user.username)
        
        operation_id, amount_with_fee = create_deposit_request(
            message.from_user.id, 
            message.from_user.username or "anon",
            currency, 
            amount
        )
        
        bank_username = get_setting('bank_username')
        
        await message.answer(
            f"💳 **Реквизиты для оплаты**\n\n"
            f"🏦 Банк: {bank_username}\n"
            f"💎 Валюта: {currency}\n"
            f"💰 Сумма к оплате: {amount_with_fee:,}\n"
            f"📊 Комиссия (10%): {amount_with_fee - amount:,}\n"
            f"🆔 ID операции: #{operation_id}\n\n"
            f"✅ После оплаты отправь СКРИНШОТ чека в этот чат\n"
            f"⚠️ В подписи к фото укажи:\n"
            f"• Сумма: {amount:,}\n"
            f"• Валюта: {currency}\n"
            f"• ID: {operation_id}"
        )
        await state.update_data(operation_id=operation_id)
        await state.set_state(DepositState.waiting_for_screenshot)
        
    except ValueError:
        await message.answer("❌ Введи число!")

@dp.message(DepositState.waiting_for_screenshot, F.photo)
async def process_deposit_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    operation_id = data['operation_id']
    photo_id = message.photo[-1].file_id
    
    update_screenshot(operation_id, photo_id)
    
    await message.answer(
        f"✅ Скриншот получен!\n"
        f"🆔 ID операции: {operation_id}\n\n"
        f"⏳ Ожидай подтверждения от администратора.\n"
        f"💰 Баланс пополнится автоматически после одобрения."
    )
    await state.clear()

# ========== ВЫВОД ==========
@dp.callback_query(F.data == "withdraw_menu")
async def withdraw_menu(callback: CallbackQuery):
    min_withdraw = get_setting('min_withdraw')
    fee = get_setting('withdraw_fee_percent')
    await callback.message.edit_text(
        f"💸 **Вывод средств**\n\n"
        f"💰 Минимальная сумма: {min_withdraw}\n"
        f"📊 Комиссия: {fee}% (вычитается из суммы)\n\n"
        f"📝 Введи сумму вывода:"
    )
    await callback.answer()

@dp.message(WithdrawState.waiting_for_amount)
async def process_withdraw_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        min_withdraw = int(get_setting('min_withdraw'))
        user = get_user(message.from_user.id)
        
        if amount < min_withdraw:
            await message.answer(f"❌ Минимальная сумма: {min_withdraw}")
            return
        
        if amount > user[2]:
            await message.answer(f"❌ Недостаточно средств! У тебя: {user[2]} монет")
            return
        
        fee_percent = int(get_setting('withdraw_fee_percent'))
        fee = int(amount * fee_percent / 100)
        amount_after = amount - fee
        
        await state.update_data(amount=amount, amount_after=amount_after, fee=fee)
        await message.answer(
            f"💸 **Детали вывода**\n\n"
            f"💰 Сумма: {amount:,}\n"
            f"📊 Комиссия ({fee_percent}%): {fee:,}\n"
            f"✅ Ты получишь: {amount_after:,}\n\n"
            f"📝 Введи адрес кошелька ({await get_setting('bank_username')}):"
        )
        await state.set_state(WithdrawState.waiting_for_wallet)
        
    except ValueError:
        await message.answer("❌ Введи число!")
