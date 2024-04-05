import asyncio

from aiogram import F
from aiogram import Dispatcher, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

import __bot_init__ as b_init
import admins_keyboard as adm_kb
import user_init
import chat_manager

bot = b_init.bot
dp = Dispatcher()
JsonManager = b_init.JsonManager
admin_chat_ids = b_init.admin_chat_ids
ChatManager = chat_manager.ChatManager()

class Form(StatesGroup):
    no_contact = State()
    order = State()
    order_await = State()
    order_processing = State()
    set_adress = State()
    runUp_consultation = State()
    '''preparation for the consultation process'''
    during_consultation = State()
    '''consultation process'''
    
async def order_mess(mess: types.Message, user_id: int):
    message = 'Я можу у тебе прийняти бронь на ліки та надати можливисть задати питання фахівцю!'
    await bot.send_message(user_id,
                           message,
                           reply_markup=b_init.start_msg_builder.as_markup())
    
# async def adm_question_to_client(mess: types.Message, user_id: int)

@dp.message(Command('adm'), F.from_user.id.in_(admin_chat_ids))
async def get_auth_user(mess: types.Message):
    data = JsonManager._load_data()
    print(data)
    message = ''
    for key, user in data.items():
        print(key)
        print(user)
        # key = list(user.keys())[0]
        message += f'User: @{data[key]["username"]}\nNumber Phone: {data[key]["number"]}\n\n'
    await bot.send_message(mess.from_user.id, message)

@dp.message(CommandStart())
async def send_welcome(mess: types.Message, state: FSMContext):
    if not JsonManager.login_user(str(mess.from_user.id)):
        message = '''Привіт!🖐\nЯ бот🤖 аптеки "Все для Здоров'я".\nДля початку, надайте свій контак, для подальшої комунікації 👇'''
        await state.set_state(Form.no_contact)
        await bot.send_message(mess.from_user.id,
                            message,
                            reply_markup=b_init.rpl_builder)
    else:
        await order_mess(mess, mess.from_user.id)

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
    JsonManager.add_user(message_data)

    message = 'Контакт отримано📩 і опрацьовано⚙️'
    await bot.send_message(mess.chat.id,
                           message,
                           reply_markup=types.ReplyKeyboardRemove())
    
    # await asyncio.sleep(1)
    await order_mess(mess, mess.chat.id)

@dp.message(Form.set_adress)
async def set_adress(mess: types.Message, state: FSMContext):
    await state.update_data(medicament=mess.text.lower())
    message = f"Чудово!\nТепер вкажи адресу 📍\nКуди треба зробити доставку по житловому комплексу:\n(вулиця, будинок, під'їзд, поверх, квартира)"
    await bot.send_message(mess.from_user.id,
                           message)
    await state.set_state(Form.order)

@dp.message(Form.order)
async def order_received(mess: types.Message, state: FSMContext):
    await state.update_data(adress=mess.text)
    user_data = await state.get_data()
    admin_message = f"id:{mess.from_user.id}\nКлієнт: @{mess.from_user.username}\nІм'я: {mess.from_user.full_name}\n📍 Адреса: {user_data['adress']}\n📦 Отриманно нове замовлення:\n\n{user_data['medicament']}"
    for id_adm in admin_chat_ids:
        data = JsonManager._load_data()
        user_number = data[str(mess.from_user.id)]['number']
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
    await state.set_state(Form.order_await) # НАДО ПОДУМАТЬ НАД СТАТУСОМ!

@dp.message(Form.runUp_consultation)
async def runUp_consultation(mess: types.Message, state: FSMContext):
    admin_message = f"id:{mess.from_user.id}\nКлієнт: @{mess.from_user.username}\nІм'я: {mess.from_user.full_name}\nЗапит від клієнта: \n\n{mess.text}"
    for id_adm in admin_chat_ids:
        data = JsonManager._load_data()
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
        await order_mess(mess, ChatManager.client_id)
        ChatManager.clear_id_chating()
    else:
        await ChatManager.chating(mess)
    
@dp.callback_query(lambda call: call.data.startswith('cli'))
async def callback_client(call: types.CallbackQuery, state: FSMContext):
    # print('cli_handler')
    if call.data == b_init.inl_btn_order.callback_data:
        message = '''Створення замовлення для доставки по ЖК 🔒\n\nВведіть назву препарату для передачі співробітнику аптеки:'''
        await bot.send_message(call.from_user.id, text=message)
        await state.set_state(Form.set_adress)
        await bot.answer_callback_query(call.id)

    if call.data == b_init.inl_btn_consultation.callback_data:
        message = f'''Запит на комунікацію 📨\n\nВведіть ваше запитання і очікуйте відповіді від фахівця!'''
        await bot.send_message(call.from_user.id, text=message)
        await state.set_state(Form.runUp_consultation)
        await bot.answer_callback_query(call.id)

    await bot.edit_message_reply_markup(call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=None)

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
        await state.set_state(Form.order_await) #НАДО ПОДУМАТЬ НАД СТАТУСОМ
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