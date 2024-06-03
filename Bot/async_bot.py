import asyncio

from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.base import StorageKey

from aiogram_dialog import DialogManager, StartMode

from __bot_init__ import Form
import __bot_init__ as b_init
import admins_keyboard as adm_kb
import Managers.chat_manager as chat_manager
import bot_comands
from OrderProcesing.delivery_order_np import callback_order_delivery_np
from OrderProcesing.delivery_order_jk import callback_order_delivery_jk
from OrderProcesing.delivery_order_pickup import callback_order_delivery_pk
from orders_dialog import DialogSG

bot = b_init.bot
dp = b_init.dp
admin_chat_ids = b_init.admin_chat_ids
JsonManager = b_init.JsonManager
SheetManager = b_init.SheetManager
OrderManager = b_init.OrderManager
ChatManager = chat_manager.ChatManager()

@dp.message(F.contact, Form.no_contact)
async def get_contac(mess: types.Message, state: FSMContext):
    await state.set_state(None)
    message_data = {
        str(mess.from_user.id): {
            "id": mess.from_user.id,
            "username": mess.from_user.username,
            "first_name": mess.from_user.first_name,
            "last_name": mess.from_user.last_name,
            "number": mess.contact.phone_number
        }
    }
    print(mess.from_user)
    print(mess.contact)
    JsonManager.add_data(message_data)
    message = 'Контакт отримано📩 і опрацьовано⚙️'
    await bot.send_message(mess.chat.id,
                           message,
                           reply_markup=types.ReplyKeyboardRemove())
    await bot_comands.order_mess(mess, mess.chat.id)

@dp.message((F.text == adm_kb.menu_consultation.text) & (F.from_user.id.in_(admin_chat_ids)))
async def menu_consultation(mess: types.Message, state: FSMContext):
    message = 'Меню взаімодії під час консультації:'
    adm_state = await state.get_state()
    if adm_state == Form.order_await:
        kb = InlineKeyboardBuilder().row(adm_kb.inl_btn_disconect_consultation)
        await bot.send_message(mess.from_user.id,
                                message,
                                reply_markup=kb.as_markup())
    if adm_state == Form.during_consultation:
        user_data = await state.storage.get_data(StorageKey(mess.bot.id,
                                                            ChatManager.client_id,
                                                            ChatManager.client_id))
        if 'order' in user_data and isinstance(user_data['order'], dict):
            order_completed = user_data['order']['order_completed']
            if order_completed:
                await bot.send_message(mess.from_user.id,
                                        message,
                                        reply_markup=adm_kb.adm_menu_consultation_bilder.as_markup())
            else:
                kb = InlineKeyboardBuilder().row(adm_kb.inl_btn_disconect_consultation)
                await bot.send_message(mess.from_user.id,
                                        message,
                                        reply_markup=kb.as_markup())

@dp.message(Form.runUp_consultation)
async def runUp_consultation(mess: types.Message, state: FSMContext):
    admin_message = f"id:{mess.from_user.id}\nКлієнт: @{mess.from_user.username}\nІм'я: {mess.from_user.full_name}\nЗапит від клієнта: \n\n{mess.text}"
    for id_adm in admin_chat_ids:
        data = JsonManager._get_data_()
        user_number = data[str(mess.from_user.id)]['number']
        await bot.send_contact(chat_id=id_adm,
                               phone_number=user_number,
                               first_name=mess.from_user.first_name,
                               last_name=mess.from_user.last_name)
        await bot.send_message(chat_id=id_adm,
                               text=admin_message, 
                               reply_markup=adm_kb.adm_consultation_builder.as_markup())
        
    client_reply = "Запит прийнято! Очікуйте на відповідь фахівця!"
    await mess.reply(client_reply)
    await state.set_state(Form.during_consultation)

@dp.message(Form.order_await)
async def order_consultation(mess: types.Message, state: FSMContext):
    # if mess.text == adm_kb.menu_consultation.text:
    #     await state.set_state(Form.order_processing)
    #     message = 'Фахівець 👩‍⚕️ дізнався необхідну інформацію з приводу вашого замовлення!\nОчікуйте на підтвердження замовлення!'
    #     await bot.send_message(ChatManager.client_id,
    #                            message,
    #                            reply_markup=types.ReplyKeyboardRemove())
    #     ChatManager.clear_id_chating()
    # else:
        await ChatManager.chating(mess)

@dp.message(Form.during_consultation)
async def during_consultation(mess: types.Message, state: FSMContext):
    # if mess.text == adm_kb.menu_consultation.text:
    #     await state.set_state(None)
    #     message = 'Комунікація завершенна❗️\nДякую за зверення до фахівця 👩‍⚕️'
    #     await bot.send_message(ChatManager.client_id,
    #                            message,
    #                            reply_markup=types.ReplyKeyboardRemove())
        
    #     user_data = await state.storage.get_data(StorageKey(mess.bot.id,
    #                                                         ChatManager.client_id,
    #                                                         ChatManager.client_id))
    #     if 'order' in user_data and isinstance(user_data['order'], dict):
    #         order_completed = user_data['order']['order_completed']
    #         if order_completed:
    #             await bot_comands.order_mess(mess, ChatManager.client_id)
    #         else:
    #             message = 'Очікуйте опрацювання вашого замовлення ⏱\nНезабаром отримаєте нове сповіщення 🔔'
    #             await bot.send_message(ChatManager.client_id,
    #                                    message)
    #     else:
    #         await bot_comands.order_mess(mess, ChatManager.client_id)
    #     ChatManager.clear_id_chating()
    # else:
        await ChatManager.chating(mess)


"""
***********************************************************
************************ CaLL_BACK ************************
***********************************************************
"""
@dp.callback_query(lambda call: call.data.startswith('cli'))
async def callback_client(call: types.CallbackQuery, state: FSMContext):
    # print('cli_handler')
    await bot.edit_message_reply_markup(call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=None)

    if call.data == b_init.inl_btn_consultation.callback_data:
        message = 'Запит на комунікацію 📨\n\nВведіть ваше запитання і очікуйте відповіді від фахівця!'
        await bot.send_message(call.from_user.id, 
                               text=message)
        await state.set_state(Form.runUp_consultation)
        await bot.answer_callback_query(call.id)

    await callback_order_delivery_np(call, state)
    await callback_order_delivery_jk(call, state)
    await callback_order_delivery_pk(call, state)

"""
***********************************************************
************************ ADM CALL *************************
***********************************************************
"""
@dp.callback_query(lambda call: call.data.startswith('adm'))
async def callback_admin(call: types.CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    # print('adm_handler')
    if call.data == adm_kb.inl_btn_order.callback_data:
        client_id = call.message.text.split()[0][3:]
        user_data = await state.storage.get_data(StorageKey(call.message.bot.id,
                                                            client_id,
                                                            client_id))
        print(user_data, type(user_data))
        await state.set_state(Form.order_processing)
        client_message = 'Адміністратор👩‍💻 взяв в опрацювання ваше замовлення!\nОчікуйте на підтвердження!'
        await bot.send_message(client_id, client_message)
        message = call.message.text + '\n\n📌 Замовлення клієнта взято в обробку⚙️'
        keyboard = InlineKeyboardBuilder().row(
            adm_kb.inl_btn_qustion_client, 
            adm_kb.inl_btn_accept_order,
            width=1)
        await bot.edit_message_text(message,
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=keyboard.as_markup())
        await bot.answer_callback_query(call.id)

    if call.data == adm_kb.inl_btn_accept_order.callback_data:
        client_id = call.message.text.split()[0][3:]
        # order = JsonManager.decod_order(await rd.redis.hgetall(client_id))
        user_data = await state.storage.get_data(StorageKey(call.message.bot.id,
                                                            client_id,
                                                            client_id))
        order = user_data['order']

        if order['delivery_type'] == 'JK_delivery':
            client_message = 'Ваше замовлення підтверджено✅\nОчікуйте на доставку!'
            await bot.send_message(client_id, client_message)
            message = call.message.text + '\n\n📌 Замовлення клієнта підтверджено✅'
            keyboard = InlineKeyboardBuilder().row(
                adm_kb.inl_btn_qustion_client, 
                adm_kb.inl_btn_acept_delivery,
                width=1)
            await bot.edit_message_text(message,
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=keyboard.as_markup())
            await SheetManager.writing_order(SheetManager.salutna_delivery_sheet,
                                    order['user_id'],
                                    order['user_name'],
                                    order['phone_number'],
                                    order['full_name'],
                                    order['order'],
                                    order['address'])
            
        if order['delivery_type'] == 'PK_delivery':
            client_message = f"Ваше замовлення підтверджено✅\n\nОчікуємо Вас для отримання за адресою:\n{order['address']}"
            await bot.send_message(client_id, client_message)
            message = call.message.text + '\n\n📌 Замовлення клієнта підтверджено✅\nОчікуємо на клієнта для отримання замовлення❗️'
            keyboard = InlineKeyboardBuilder().row(
                adm_kb.inl_btn_qustion_client, 
                adm_kb.inl_btn_acept_delivery,
                width=1)
            await bot.edit_message_text(message,
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=keyboard.as_markup())
        
        await bot.answer_callback_query(call.id)

    if call.data == adm_kb.inl_btn_acept_delivery.callback_data:
        client_id = call.message.text.split()[0][3:]
        # order = JsonManager.decod_order(await rd.redis.hgetall(client_id))
        user_data = await state.storage.get_data(StorageKey(call.message.bot.id,
                                                            client_id,
                                                            client_id))
        order = user_data['order']

        if order['delivery_type'] == 'JK_delivery':
            client_message = 'Ваше замовлення було доставлено! 📦\n\nДякую що обираєте нас!'
            await bot.send_message(client_id, client_message)

            message = call.message.text + '\n\n📌 Замовлення клієнта доставлено 📦\n❗️❗️❗️Повністю опрацьовано❗️❗️❗️'
            await bot.edit_message_text(message,
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=None)
        
        if order['delivery_type'] == 'PK_delivery':
            client_message = 'Ваше замовлення було отримано! 📦\n\nДякую що обираєте нас!'
            await bot.send_message(client_id, client_message)

            message = call.message.text + '\n\n📌 Замовлення клієнта отримано 📦\n❗️❗️❗️Повністю опрацьовано❗️❗️❗️'
            await bot.edit_message_text(message,
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=None)
        
        OrderManager.update_order_data(order_id=order['order_id'],
                                       order_completed=1)
        order['order_completed'] = 1
        await state.storage.update_data(StorageKey(call.message.bot.id,
                                                    client_id,
                                                    client_id), 
                                        {'order': order})
        await bot.answer_callback_query(call.id)

    if call.data == adm_kb.inl_btn_answer_consultation.callback_data:
        await state.set_state(Form.during_consultation)
        message = call.message.text + '\nЗапит клієнта взято в обробку ⚙️'
        await bot.edit_message_text(message,
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=None)
        message = f'Напишіть вашу відповідь клієнту 👇'
        await bot.send_message(call.from_user.id, message, reply_markup=adm_kb.adm_rpl_builder)
        client_id = int(call.message.text.split()[0][3:])
        ChatManager.set_id_chating(call.from_user.id, client_id)
        await bot.answer_callback_query(call.id)

    if call.data == adm_kb.inl_btn_disconect_consultation.callback_data:
        adm_state = await state.get_state()
        if adm_state == Form.order_await:
            await state.set_state(Form.order_processing)
            message = 'Фахівець 👩‍⚕️ дізнався необхідну інформацію з приводу вашого замовлення!\nОчікуйте на підтвердження замовлення!'
            await bot.send_message(ChatManager.client_id,
                                message,
                                reply_markup=types.ReplyKeyboardRemove())

        if adm_state == Form.during_consultation:
            await state.set_state(None)
            cli_message = 'Комунікація завершенна❗️\nДякую за зверення до фахівця 👩‍⚕️'
            await bot.send_message(ChatManager.client_id,
                                    cli_message,
                                    reply_markup=types.ReplyKeyboardRemove())
            
            user_data = await state.storage.get_data(StorageKey(call.message.bot.id,
                                                                ChatManager.client_id,
                                                                ChatManager.client_id))
            if 'order' in user_data and isinstance(user_data['order'], dict):
                order_completed = user_data['order']['order_completed']
                if order_completed:
                    pass
                    # await bot_comands.order_mess(call.message, ChatManager.client_id)
                else:
                    cli_message = 'Очікуйте опрацювання вашого замовлення ⏱\nНезабаром отримаєте нове сповіщення 🔔'
                    await bot.send_message(ChatManager.client_id,
                                            cli_message)
            # else:
            #     await bot_comands.order_mess(call.message, ChatManager.client_id)

        ChatManager.clear_id_chating()
        message = 'Комунікація з клієнтом була ЗАВЕРШЕНА🛑\nНаступні повідомлення клієнт не отримає❗️'
        await bot.delete_message(call.from_user.id,
                                 call.message.message_id)
        await bot.send_message(call.from_user.id,
                               message,
                               reply_markup=types.ReplyKeyboardRemove())
        await bot.answer_callback_query(call.id)
    
    if call.data == adm_kb.inl_btn_for_order_jk.callback_data:
        message = 'Створити замовлення з доставкую по ЖК 📫'
        kb = InlineKeyboardBuilder().row(b_init.inl_btn_order_jk)
        await bot.send_message(ChatManager.client_id,
                               message,
                               reply_markup=kb.as_markup())
        await bot.answer_callback_query(call.id)
        
    if call.data == adm_kb.inl_btn_for_order_pknp.callback_data:
        message = 'Створити замовлення для самовивозу 🚶 або доставкою НП 📦'
        kb = InlineKeyboardBuilder().row(b_init.inl_btn_NP_order, b_init.inl_btn_pickup_order)
        await bot.send_message(ChatManager.client_id,
                               message,
                               reply_markup=kb.as_markup())
        await bot.answer_callback_query(call.id)
    
    if call.data == adm_kb.inl_btn_qustion_client.callback_data:
        await state.set_state(Form.order_await)
        client_id = int(call.message.text.split()[0][3:])
        client_message = 'Адміністратор👩‍💻 хоче задати вам запитання!\nОчікуйте на повідомлення 📩'
        await bot.send_message(client_id, client_message)
        message = f'Введіть ваше запитання клієнту 👇'
        # await bot.send_message(call.from_user.id, message, reply_markup=adm_kb.adm_rpl_builder)
        await call.message.reply(message, reply_markup=adm_kb.adm_rpl_builder)
        ChatManager.set_id_chating(call.from_user.id, client_id)
        await bot.answer_callback_query(call.id)
        
    if call.data == adm_kb.inl_btn_go_to_orders.callback_data:
        await dialog_manager.start(DialogSG.PAGERS, mode=StartMode.NORMAL)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())