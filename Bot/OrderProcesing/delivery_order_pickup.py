import logging

from aiogram import F, types
from aiogram.fsm.context import FSMContext

from __bot_init__ import Form
import __bot_init__ as b_init
import admins_keyboard as adm_kb
from Managers.order_manager import Manager as OrderManager

bot = b_init.bot
dp = b_init.dp

admin_chat_ids = b_init.admin_chat_ids
JsonManager = b_init.JsonManager
SheetManager = b_init.SheetManager

async def chooses_apt_address(mess: types.Message, state: FSMContext, call: types.CallbackQuery = None):
    if call != None:
        logging.warn(f"User {call.from_user.username, call.from_user.id} CHOOSES apteca pickup")
    message = 'Оберіть аптеку для самовивозу 👇'
    await mess.reply(text=message,
                    reply_markup=b_init.keyboard_apt_adress().as_markup())
    
@dp.message(Form.set_pickup_address)
async def set_order(mess: types.Message, state: FSMContext):
    # await state.update_data(medicament=mess.text.lower())
    data = await state.get_data()
    order = data['order']
    order['order']=mess.text.lower()
    await state.update_data(order=order)
    await chooses_apt_address(mess, state)

@dp.message(Form.order)
async def order_received(mess: types.Message, state: FSMContext, call: types.CallbackQuery = None):
    data = await state.get_data()
    order = data['order']
    order['address'] = data['address']
    order['order_id'] = data['reserv_order_id']
    admin_message = 'Нове замовлення ❗️❗️❗️'
    for id_adm in admin_chat_ids:
        await bot.send_message(chat_id=id_adm,
                               text=admin_message, 
                               reply_markup=adm_kb.adm_go_to_orders_bilder.as_markup())
    # admin_message = f"id:{mess.from_user.id}\n№ Замовлення: {order['order_id']}\nКлієнт: @{mess.from_user.username}\nІм'я в ТГ: {mess.from_user.full_name}\n📍 Адреса: {order['address']}\n📦 Отриманно нове замовлення:\n\n{order['order']}\n\n❗️❗️❗️Самовивіз❗️❗️❗️"
    # for id_adm in admin_chat_ids:
    #     await bot.send_contact(chat_id=id_adm,
    #                            phone_number=order['phone_number'],
    #                            first_name=mess.from_user.first_name,
    #                            last_name=mess.from_user.last_name)
    #     await bot.send_message(chat_id=id_adm,
    #                            text=admin_message, 
    #                            reply_markup=adm_kb.adm_order_builder.as_markup())

    client_message = f"Ваше замовлення прийнято 📥\n\nЗамовлення №{order['order_id']}\n\nМи скоро з вами зв'яжемося!"
    await bot.send_message(int(order['user_id']),
                           client_message)
    await state.set_state(Form.order_await)
    await state.update_data(order=order)
    OrderManager.order_create(order)
    if call != None:
        logging.warn(f"User {call.from_user.username, call.from_user.id} CREATED order №{order['order_id']}")
    else:
        logging.warn(f"User {mess.from_user.username, mess.from_user.id} CREATED order №{order['order_id']}")
    
    # await redis_storage.redis.hmset(str(mess.from_user.id), order)

"""
***********************************************************
************************ CaLL_BACK ************************
***********************************************************
"""
async def callback_order_delivery_pk(call: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if call.data == b_init.inl_btn_pickup_order.callback_data:
        await state.set_state(Form.set_pickup_address)
        user_id = str(call.from_user.id)
        order = OrderManager()
        message = 'Створення замовлення для самовивозу 🔒\n\nВведіть назву препарату для передачі співробітнику аптеки:'
        await bot.send_message(call.from_user.id, 
                               text=message)
        await bot.answer_callback_query(call.id)
        order.update_property(
            user_id=user_id,
            # order_id=await order.get_order_number(),
            delivery_type='PK_delivery',
            user_name=call.from_user.username,
            full_name=call.from_user.full_name,
            phone_number=JsonManager.get_phone_number(str(call.from_user.id)))
        # await state.update_data(order_obj=json.dumps(order))
        await state.update_data(order=order.__conver_dict__)
        await state.update_data(reserv_order_id= await order.get_order_number())
        # logging.warn(f"User {call.from_user.username, call.from_user.id} creating order №{order.order_id}")
        logging.warn(f"User {call.from_user.username, call.from_user.id} creating order")

    if call.data.startswith('cli_apt_address_') and current_state == Form.set_pickup_address:
        logging.warn(f"User {call.from_user.username, call.from_user.id} SELECTED apt pickup")
        await state.set_state(Form.accept_pickup_address)
        apt = call.data.split('cli_apt_address_')[-1].replace('_', ' ')
        await state.update_data(address=apt)
        # print(address)
        # previous_message = call.message.reply_to_message
        await call.message.reply(text=b_init.get_apt_info(apt),
                                 reply_markup=b_init.accept_user_address.as_markup())
        
    if current_state == Form.accept_pickup_address:
        if call.data == b_init.inl_accept_yes.callback_data:
            logging.warn(f"User {call.from_user.username, call.from_user.id} ACCEPT apt pickup")
            await state.set_state(Form.order)
            await order_received(call.message, state, call)
            
        if call.data == b_init.inl_accept_no.callback_data:
            logging.warn(f"User {call.from_user.username, call.from_user.id} CHANGES apt pickup")
            await state.set_state(Form.set_pickup_address)
            await chooses_apt_address(call.message, state, call)