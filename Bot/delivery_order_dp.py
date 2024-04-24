import asyncio

from aiogram import F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from __bot_init__ import Form
import __bot_init__ as b_init
import admins_keyboard as adm_kb
import Managers.chat_manager as chat_manager

bot = b_init.bot
dp = b_init.dp
JsonManager = b_init.JsonManager
SheetManager = b_init.SheetManager

async def set_order_data(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await bot.send_message(call.from_user.id,
                           '⏳')
    await SheetManager.writing_order(SheetManager.salutna_delivery_sheet,
                                        str(call.from_user.id),
                                        call.from_user.username,
                                        JsonManager.get_phone_number(str(call.from_user.id)),
                                        user_data['full_name'],
                                        user_data['medicament'],
                                        user_data['adress'])
    admin_message = f"id:{call.from_user.id}\nКлієнт: @{call.from_user.username}\nІм'я в ТГ: {call.from_user.full_name}\nПовне ім'я: {user_data['full_name']}\n📍 Адреса: {user_data['adress']}\n📦 Отриманно нове замовлення:\n{user_data['medicament']}\n\n❗️❗️❗️ДОСТАВКА НОВА ПОШТА❗️❗️❗️"
    for id_adm in b_init.admin_chat_ids:
        user_number = JsonManager.get_phone_number(str(call.from_user.id))
        # print(mess)
        await bot.send_contact(chat_id=id_adm,
                               phone_number=user_number,
                               first_name=user_data['full_name'])
        await bot.send_message(chat_id=id_adm,
                               text=admin_message)
        
    await bot.delete_message(call.from_user.id,
                             call.message.message_id + 1)
    await asyncio.sleep(0.4)
    client_message = "Ваше замовлення прийнято 📥\nМи скоро з вами зв'яжемося!"
    await bot.send_message(call.from_user.id,
                           client_message)
    # await state.set_state(Form.order_await) # НАДО ПОДУМАТЬ НАД СТАТУСОМ!

@dp.message(Form.check_full_name)
async def check_full_name(mess: types.Message, state: FSMContext):
    await state.update_data(medicament=mess.text)
    user_full_name = JsonManager.get_full_name(str(mess.from_user.id))
    if user_full_name is None:
        await state.update_data(mark_full_name=False)
        await state.set_state(Form.set_full_name)
        await set_full_name(mess, state)
    else:
        await state.update_data(mark_full_name=True)
        await state.update_data(full_name=user_full_name)
        message = f"Доставку робимо на це ім'я?\n📍Ім'я: {user_full_name}"
        await mess.reply(message,
                         reply_markup=b_init.accept_user_adress.as_markup())

@dp.message(Form.set_full_name)
async def set_full_name(mess: types.Message, state: FSMContext):
    message = f'Принято!\n\nТепер вкажіть ПІБ отримувача на новій пошті:'
    await bot.send_message(mess.from_user.id, message)
    await state.set_state(Form.save_full_name)

@dp.message(Form.save_full_name)    
async def save_full_name(mess: types.Message, state: FSMContext):
    await state.update_data(full_name=mess.text)
    message = "Зберегти ваше ім'я для наступних замовлень?"
    keyboard = InlineKeyboardBuilder()
    keyboard.row(b_init.inl_btn_save, b_init.inl_btn_not_save, width=1)
    await mess.reply(message,
                     reply_markup=keyboard.as_markup())

@dp.message(Form.save_np_adress)    
async def save_adress(mess: types.Message, state: FSMContext):
    await state.update_data(adress=mess.text)
    message = 'Зберегти вашу адресу 📍 для наступних замовлень?'
    keyboard = InlineKeyboardBuilder()
    keyboard.row(b_init.inl_btn_save, b_init.inl_btn_not_save, width=1)
    await mess.reply(message,
                     reply_markup=keyboard.as_markup())
    
@dp.message(Form.set_adress)
async def set_adress(mess: types.Message, state: FSMContext):
    message = f"Чудово!\nТепер вкажи адресу 📍\nКуди треба зробити доставку Новою Поштою:\n(Місто, № віділення НП, адреса віділення)"
    await bot.send_message(mess.from_user.id, message)
    await state.set_state(Form.save_np_adress)

@dp.message(Form.check_np_adress)
async def check_np_adress(mess: types.Message, state: FSMContext):
    state_data = await state.get_data()
    if not state_data['mark_full_name']: 
        await state.update_data(full_name=mess.text)
        JsonManager.add_full_name(str(mess.from_user.id), mess.text)
    user_np_adress = JsonManager.get_np_adress(str(mess.from_user.id))
    if user_np_adress is None:
        await state.set_state(Form.set_adress)
        await set_adress(mess, state)
    else:
        await state.update_data(adress=user_np_adress)
        message = f'Доставку робимо на цей адрес?\n📍Адреса: {user_np_adress}'
        await mess.reply(message,
                         reply_markup=b_init.accept_user_adress.as_markup())


"""
************************ CaLL_BACK ************************
"""
async def callback_order_delivery(call: types.CallbackQuery, state: FSMContext):
    if call.data == b_init.inl_btn_delivery.callback_data:
        message = 'Як бажаєте створити замовлення?'
        await bot.send_message(call.from_user.id,
                               text=message, 
                               reply_markup=b_init.menu_delivery_order.as_markup())
        await bot.answer_callback_query(call.id)

    if call.data == b_init.inl_btn_NP_order.callback_data:
        message = 'Створюємо замовлення для доставки Новою Поштою 📦\n\nВведіть назву препарату:'
        await bot.send_message(call.from_user.id,
                               text=message)
        await state.set_state(Form.check_full_name)
        await bot.answer_callback_query(call.id)

    if await state.get_state() == Form.save_np_adress:
        if call.data == b_init.inl_btn_save.callback_data:
            previous_message = call.message.reply_to_message
            JsonManager.add_np_adress(str(call.from_user.id), previous_message.text)
            await state.set_state(Form.order)
            await set_order_data(call, state)

        if call.data == b_init.inl_btn_not_save.callback_data:
            previous_message = call.message.reply_to_message
            await state.set_state(Form.order)
            await set_order_data(call, state)

    if await state.get_state() == Form.save_full_name:
        previous_message = call.message.reply_to_message
        if call.data == b_init.inl_btn_save.callback_data:
            JsonManager.add_full_name(str(call.from_user.id), previous_message.text)
        if call.data == b_init.inl_btn_not_save.callback_data:
            pass
        await state.set_state(Form.check_np_adress)
        await check_np_adress(previous_message, state)

    if await state.get_state() == Form.check_np_adress:
        if call.data == b_init.inl_accept_yes.callback_data:
            previous_message = call.message.reply_to_message
            await state.set_state(Form.order)
            await set_order_data(call, state)

        if call.data == b_init.inl_accept_no.callback_data:
            previous_message = call.message.reply_to_message
            await state.set_state(Form.set_adress)
            await set_adress(previous_message, state)

    if await state.get_state() == Form.check_full_name:
        previous_message = call.message.reply_to_message
        if call.data == b_init.inl_accept_yes.callback_data:
            await state.set_state(Form.check_np_adress)
            await check_np_adress(previous_message, state)

        if call.data == b_init.inl_accept_no.callback_data:
            await state.set_state(Form.set_full_name)
            await set_full_name(previous_message, state)
