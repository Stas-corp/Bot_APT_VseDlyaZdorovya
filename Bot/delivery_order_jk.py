from aiogram import F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from __bot_init__ import Form
import __bot_init__ as b_init
import admins_keyboard as adm_kb
from Managers.order_manager import Manager as OrderManager

bot = b_init.bot
dp = b_init.dp
rd = b_init.redis_storage
admin_chat_ids = b_init.admin_chat_ids
JsonManager = b_init.JsonManager
SheetManager = b_init.SheetManager

@dp.message(Form.check_address)
async def check_address(mess: types.Message, state: FSMContext):
    # await state.update_data(medicament=mess.text.lower())
    data = await state.get_data()
    order = data['order']
    order['order']=mess.text.lower()
    user_address = JsonManager.get_address(str(mess.from_user.id))
    if user_address is None:
        await state.set_state(Form.set_address)
        await set_address(mess, state)
    else:
        # await state.update_data(address=user_address)
        order['address']=user_address
        message = f'Доставку робимо на цей адрес?\n📍Адреса: {user_address}'
        await mess.reply(message,
                         reply_markup=b_init.accept_user_address.as_markup())
    await state.update_data(order=order)

@dp.message(Form.set_address)
async def set_address(mess: types.Message, state: FSMContext):
    message = f"Чудово!\nТепер вкажи адресу 📍\nКуди треба зробити доставку по житловому комплексу:\n(вулиця, будинок, під'їзд, поверх, квартира)"
    await bot.send_message(mess.from_user.id, message)
    await state.set_state(Form.save_address)

@dp.message(Form.save_address)    
async def save_address(mess: types.Message, state: FSMContext):
    # await state.update_data(address=mess.text)
    data = await state.get_data()
    order = data['order']
    order['address']=mess.text
    message = 'Зберегти вашу адресу 📍 для наступних замовлень?'
    keyboard = InlineKeyboardBuilder()
    keyboard.row(b_init.inl_btn_save, b_init.inl_btn_not_save, width=1)
    await mess.reply(message,
                     reply_markup=keyboard.as_markup())
    await state.update_data(order=order)
    
@dp.message(Form.order)
async def order_received(mess: types.Message, state: FSMContext):
    user_data = await state.get_data()
    order = user_data['order']
    admin_message = f"id:{mess.from_user.id}\n№ Замовлення: {order['order_id']}\nКлієнт: @{mess.from_user.username}\nІм'я в ТГ: {mess.from_user.full_name}\n📍 Адреса: {order['address']}\n📦 Отриманно нове замовлення:\n\n{order['order']}"
    for id_adm in admin_chat_ids:
        await bot.send_contact(chat_id=id_adm,
                               phone_number=order['phone_number'],
                               first_name=mess.from_user.first_name,
                               last_name=mess.from_user.last_name)
        await bot.send_message(chat_id=id_adm,
                               text=admin_message, 
                               reply_markup=adm_kb.adm_order_builder.as_markup())
        # message = ''
        # for key, value in order.items():
        #     message += f'{key} - {value}\n'
        # await bot.send_message(chat_id=id_adm,
        #                        text=message)

    client_message = "Ваше замовлення прийнято 📥\nМи скоро з вами зв'яжемося!"
    await bot.send_message(mess.from_user.id,
                           client_message)
    await state.set_state(Form.order_await)
    OrderManager.order_create(order)
    await rd.redis.hmset(str(mess.from_user.id), order)

"""
***********************************************************
************************ CaLL_BACK ************************
***********************************************************
"""
async def callback_order_delivery_jk(call: types.CallbackQuery, state: FSMContext):
    if call.data == b_init.inl_btn_order.callback_data:
        user_id = str(call.from_user.id)
        order = OrderManager(user_id)
        message = 'Створення замовлення для доставки по ЖК 🔒\n\nВведіть назву препарату для передачі співробітнику аптеки:'
        await bot.send_message(call.from_user.id, 
                               text=message)
        await state.set_state(Form.check_address)
        await bot.answer_callback_query(call.id)
        order.update_property(
            order_id=order.get_order_number(),
            delivery_type='JK_delivery',
            user_name=call.from_user.username,
            full_name=call.from_user.full_name,
            phone_number=JsonManager.get_phone_number(str(call.from_user.id)))
        await state.update_data(order=order.__conver_dict__)

    if await state.get_state() == Form.save_address:
        previous_message = call.message.reply_to_message
        if call.data == b_init.inl_btn_save.callback_data:
            JsonManager.add_address(str(call.from_user.id), previous_message.text)

        if call.data == b_init.inl_btn_not_save.callback_data:
            pass

        await state.set_state(Form.order)
        await order_received(previous_message, state)

    if await state.get_state() == Form.check_address:
        previous_message = call.message.reply_to_message
        if call.data == b_init.inl_accept_yes.callback_data:
            await state.set_state(Form.order)
            await order_received(previous_message, state)

        if call.data == b_init.inl_accept_no.callback_data:
            await state.set_state(Form.set_address)
            await set_address(previous_message, state)