import asyncio

from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from __bot_init__ import Form
import __bot_init__ as b_init
import admins_keyboard as adm_kb
import Managers.chat_manager as chat_manager
import bot_comands
from delivery_order_dp import callback_order_delivery_np
from delivery_order_jk import callback_order_delivery_jk

bot = b_init.bot
dp = b_init.dp
admin_chat_ids = b_init.admin_chat_ids
JsonManager = b_init.JsonManager
SheetManager = b_init.SheetManager
# OrderManager = b_init.OrderManager
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
    if mess.text == adm_kb.disconect_consultation.text:
        await state.set_state(Form.order_processing)
        message = 'Фахівець 👩‍⚕️ дізнався необхідну інформацію з приводу вашого замовлення!\nОчікуйте на підтвердження замовлення!'
        await bot.send_message(ChatManager.client_id,
                               message,
                               reply_markup=types.ReplyKeyboardRemove())
        ChatManager.clear_id_chating()
    else:
        await ChatManager.chating(mess)

@dp.message(Form.during_consultation)
async def during_consultation(mess: types.Message, state: FSMContext):
    if mess.text == adm_kb.disconect_consultation.text:
        await state.set_state(None)
        message = 'Комунікація завершенна❗️\nДякую за зверення до фахівця 👩‍⚕️'
        await bot.send_message(ChatManager.client_id,
                               message,
                               reply_markup=types.ReplyKeyboardRemove())
        await bot_comands.order_mess(mess, ChatManager.client_id)
        ChatManager.clear_id_chating()
    else:
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

@dp.callback_query(lambda call: call.data.startswith('adm'))
async def callback_admin(call: types.CallbackQuery, state: FSMContext):
    # print('adm_handler')
    if call.data == adm_kb.inl_btn_order.callback_data:
        await state.set_state(Form.order_processing)
        client_message = 'Адміністратор👩‍💻 взяв в опрацювання ваше замовлення!\nОчікуйте на підтвердження!'
        client_id = call.message.text.split()[0][3:]
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
        
        client_message = 'Ваше замовлення підтверджено✅\nОчікуйте на доставку!'
        client_id = call.message.text.split()[0][3:]
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
        await bot.answer_callback_query(call.id)
        await SheetManager.writing_order(SheetManager.salutna_delivery_sheet,
                                   client_id,
                                   '-',
                                   '-',
                                   '-',
                                   '-',
                                   '-')

    if call.data == adm_kb.inl_btn_acept_delivery.callback_data:
        client_message = 'Ваше замовлення було доставлено! 📦\n\nДякую що обераєте нас!'
        client_id = call.message.text.split()[0][3:]
        await bot.send_message(client_id, client_message)
        message = call.message.text + '\n\n📌 Замовлення клієнта доставлено 📦\n❗️❗️❗️Повністю опрацьовано❗️❗️❗️'
        await bot.edit_message_text(message,
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=None)
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
        
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())