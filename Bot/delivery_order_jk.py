import asyncio

from aiogram import F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from __bot_init__ import Form
import __bot_init__ as b_init
import admins_keyboard as adm_kb

bot = b_init.bot
dp = b_init.dp
admin_chat_ids = b_init.admin_chat_ids
JsonManager = b_init.JsonManager
SheetManager = b_init.SheetManager
OrderManager = b_init.OrderManager

@dp.message(Form.check_adress)
async def check_adress(mess: types.Message, state: FSMContext):
    await state.update_data(medicament=mess.text.lower())
    user_adress = JsonManager.get_adress(str(mess.from_user.id))
    if user_adress is None:
        await state.set_state(Form.set_adress)
        await set_adress(mess, state)
    else:
        await state.update_data(adress=user_adress)
        message = f'Доставку робимо на цей адрес?\n📍Адреса: {user_adress}'
        await mess.reply(message,
                         reply_markup=b_init.accept_user_adress.as_markup())

@dp.message(Form.set_adress)
async def set_adress(mess: types.Message, state: FSMContext):
    message = f"Чудово!\nТепер вкажи адресу 📍\nКуди треба зробити доставку по житловому комплексу:\n(вулиця, будинок, під'їзд, поверх, квартира)"
    await bot.send_message(mess.from_user.id, message)
    await state.set_state(Form.save_adress)

@dp.message(Form.save_adress)    
async def save_adress(mess: types.Message, state: FSMContext):
    await state.update_data(adress=mess.text)
    OrderManager.update_property(adress=mess.text)
    message = 'Зберегти вашу адресу 📍 для наступних замовлень?'
    keyboard = InlineKeyboardBuilder()
    keyboard.row(b_init.inl_btn_save, b_init.inl_btn_not_save, width=1)
    await mess.reply(message,
                     reply_markup=keyboard.as_markup())
    
@dp.message(Form.order)
async def order_received(mess: types.Message, state: FSMContext):
    data = JsonManager._get_data_()
    user_number = data[str(mess.from_user.id)]['number']
    user_data = await state.get_data()
    admin_message = f"id:{mess.from_user.id}\nКлієнт: @{mess.from_user.username}\nІм'я в ТГ: {mess.from_user.full_name}\n📍 Адреса: {user_data['adress']}\n📦 Отриманно нове замовлення:\n\n{user_data['medicament']}"
    for id_adm in admin_chat_ids:
        await bot.send_contact(chat_id=id_adm,
                               phone_number=user_number,
                               first_name=mess.from_user.first_name,
                               last_name=mess.from_user.last_name)
        await bot.send_message(chat_id=id_adm,
                               text=admin_message, 
                               reply_markup=adm_kb.adm_order_builder.as_markup())
    client_message = "Ваше замовлення прийнято 📥\nМи скоро з вами зв'яжемося!"
    await bot.send_message(mess.from_user.id,
                           client_message)
    await state.set_state(Form.order_await)

"""
***********************************************************
************************ CaLL_BACK ************************
***********************************************************
"""
async def callback_order_delivery_jk(call: types.CallbackQuery, state: FSMContext):
    if call.data == b_init.inl_btn_order.callback_data:
        message = 'Створення замовлення для доставки по ЖК 🔒\n\nВведіть назву препарату для передачі співробітнику аптеки:'
        await bot.send_message(call.from_user.id, 
                               text=message)
        await state.set_state(Form.check_adress)
        await bot.answer_callback_query(call.id)

    if await state.get_state() == Form.save_adress:
        previous_message = call.message.reply_to_message
        if call.data == b_init.inl_btn_save.callback_data:
            JsonManager.add_adress(str(call.from_user.id), previous_message.text)

        if call.data == b_init.inl_btn_not_save.callback_data:
            pass

        await state.set_state(Form.order)
        await order_received(previous_message, state)

    if await state.get_state() == Form.check_adress:
        previous_message = call.message.reply_to_message
        if call.data == b_init.inl_accept_yes.callback_data:
            await state.set_state(Form.order)
            await order_received(previous_message, state)

        if call.data == b_init.inl_accept_no.callback_data:
            await state.set_state(Form.set_adress)
            await set_adress(previous_message, state)