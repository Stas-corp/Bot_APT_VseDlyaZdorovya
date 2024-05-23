import json

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
redis_storage = b_init.redis_storage

admin_chat_ids = b_init.admin_chat_ids
JsonManager = b_init.JsonManager
SheetManager = b_init.SheetManager

@dp.message(Form.set_pickup_address)
async def set_address(mess: types.Message, state: FSMContext):
    # await state.update_data(medicament=mess.text.lower())
    data = await state.get_data()
    order = data['order']
    order['order']=mess.text.lower()
    message = 'Оберіть аптеку для самовивозу 👇'
    await mess.reply(text=message,
                    reply_markup=b_init.keyboard_apt_adress().as_markup())
    await state.update_data(order=order)
    
@dp.message(Form.order)
async def order_received(mess: types.Message, state: FSMContext):
    data = await state.get_data()
    order = data['order']
    order['address'] = data['address']
    admin_message = f"id:{mess.from_user.id}\n№ Замовлення: {order['order_id']}\nКлієнт: @{mess.from_user.username}\nІм'я в ТГ: {mess.from_user.full_name}\n📍 Адреса: {order['address']}\n📦 Отриманно нове замовлення:\n\n{order['order']}\n\n❗️❗️❗️Самовивіз❗️❗️❗️"
    for id_adm in admin_chat_ids:
        await bot.send_contact(chat_id=id_adm,
                               phone_number=order['phone_number'],
                               first_name=mess.from_user.first_name,
                               last_name=mess.from_user.last_name)
        await bot.send_message(chat_id=id_adm,
                               text=admin_message, 
                               reply_markup=adm_kb.adm_order_builder.as_markup())

    client_message = "Ваше замовлення прийнято 📥\nМи скоро з вами зв'яжемося!"
    await bot.send_message(mess.from_user.id,
                           client_message)
    await state.set_state(Form.order_await)
    await state.update_data(order=order)
    OrderManager.order_create(order)
    # await redis_storage.redis.hmset(str(mess.from_user.id), order)

"""
***********************************************************
************************ CaLL_BACK ************************
***********************************************************
"""
async def callback_order_delivery_pk(call: types.CallbackQuery, state: FSMContext):
    if call.data == b_init.inl_btn_pickup_order.callback_data:
        user_id = str(call.from_user.id)
        order = OrderManager(user_id)
        message = 'Створення замовлення для самовивозу 🔒\n\nВведіть назву препарату для передачі співробітнику аптеки:'
        await bot.send_message(call.from_user.id, 
                               text=message)
        await state.set_state(Form.set_pickup_address)
        await bot.answer_callback_query(call.id)
        order.update_property(
            order_id=order.get_order_number(),
            delivery_type='PK_delivery',
            user_name=call.from_user.username,
            full_name=call.from_user.full_name,
            phone_number=JsonManager.get_phone_number(str(call.from_user.id)))
        # await state.update_data(order_obj=json.dumps(order))
        await state.update_data(order=order.__conver_dict__)

    if call.data.startswith('cli_apt_address_'):
        address = call.data.split('_')[-1]
        # print(address)
        previous_message = call.message.reply_to_message
        await state.update_data(address=address)
        await state.set_state(Form.order)
        await order_received(previous_message, state)