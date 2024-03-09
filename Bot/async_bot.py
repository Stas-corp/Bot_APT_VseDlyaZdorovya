import asyncio

from aiogram import F
from aiogram import Dispatcher, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command

import __bot_init__ as b_init
import admins_keyboard as adm_kb
import user_init

bot = b_init.bot
JsonManager = b_init.JsonManager
dp = Dispatcher()
admin_chat_ids = b_init.admin_chat_ids

class Form(StatesGroup):
    no_contact = State()
    order = State()
    consultation = State()
    await_order = State()

async def order_mess(mess: types.Message):
    message = 'Я можу у тебе прийняти бронь на ліки та надати можливисть задати питання вахівцю!'
    await bot.send_message(mess.chat.id,
                           message,
                           reply_markup=b_init.start_msg_builder.as_markup())

@dp.message(Command('adm'))
async def get_auth_user(mess: types.Message):
    if mess.from_user.id in admin_chat_ids:
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
        await order_mess(mess)

    # await bot.send_message(chat_id=mess.chat.id, 
    #                        reply_markup=b_init.start_msg_builder.as_markup(),
    #                        text = '''Бажаю здоров'я!\nЯ бот аптеки "Все для Здоров'я".\nЯ можу у тебе прийняти бронь на лікі та надати можливисть задати питання вахівцю!''')

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
    
    await asyncio.sleep(1)

    await order_mess(mess)

@dp.message(Form.order)
async def order_received(mess: types.Message, state: FSMContext):
    admin_message = f"Клієнт: {mess.from_user.username}\nІм'я: {mess.from_user.full_name}\nОтриманно нове замовлення:\n\n{mess.text}"
    for id_adm in admin_chat_ids:
        await bot.send_message(chat_id=id_adm,
                               text=admin_message, 
                               reply_markup=adm_kb.order_adm_builder.as_markup())

    client_reply = "Ваше замовлення прийнято. Ми скоро з вами зв'яжемося!"
    await mess.reply(client_reply)
    await state.set_state(Form.await_order)

@dp.callback_query(lambda call:True)
async def caller(call: types.CallbackQuery, state: FSMContext):
    if call.data == b_init.inl_btn_order.callback_data:
        message = '''Створення броні 🔒\n\nВведіть назву препарату для передачі співробітнику аптеки:'''
        await bot.send_message(call.from_user.id, text=message)
        await state.set_state(Form.order)
        await bot.answer_callback_query(call.id)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())