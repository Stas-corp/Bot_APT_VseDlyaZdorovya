import asyncio

from aiogram import F
from aiogram import Dispatcher, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

import __bot_init__ as b_init
import user_init

bot = b_init.bot
dp = Dispatcher()
admin_chat_ids = b_init.admin_chat_ids

class Form(StatesGroup):
    no_contact = State()
    order = State()
    consultation = State()

@dp.message(CommandStart())
async def send_welcome(mess: types.Message, state: FSMContext):
    message = '''Привіт!🖐\nЯ бот🤖 аптеки "Все для Здоров'я".\nДля початку, надайте свій контак, для подальшої комунікації 👇'''
    await state.set_state(Form.no_contact)
    await bot.send_message(mess.from_user.id,
                           message,
                           reply_markup=b_init.rpl_builder)

    # await bot.send_message(chat_id=mess.chat.id, 
    #                        reply_markup=b_init.start_msg_builder.as_markup(),
    #                        text = '''Бажаю здоров'я!\nЯ бот аптеки "Все для Здоров'я".\nЯ можу у тебе прийняти бронь на лікі та надати можливисть задати питання вахівцю!''')

@dp.message(F.contact, Form.no_contact)
async def get_contac(mess: types.Message, state: FSMContext):
    await state.set_state(None)
    print(mess)

    message = 'Контакт отримано📩 і опрацьовано⚙️'
    await bot.send_message(mess.chat.id,
                           message,
                           reply_markup=types.ReplyKeyboardRemove())
    
    await asyncio.sleep(1)

    message = 'Я можу у тебе прийняти бронь на лікі та надати можливисть задати питання вахівцю!'
    await bot.send_message(mess.chat.id,
                           message,
                           reply_markup=b_init.start_msg_builder.as_markup())

@dp.message(Form.order)
async def order_received(mess: types.Message, state: FSMContext):
    admin_message = f"Отриманно нове замовлення:\n\n{mess.text}"
    for id_adm in admin_chat_ids:
        await bot.send_message(chat_id=id_adm, text=admin_message)

    client_reply = "Ваше замовлення прийнято. Ми скоро з вами зв'яжемося!"
    await mess.reply(client_reply)
    await state.set_state(None)

@dp.callback_query(lambda call:True)
async def caller(call: types.CallbackQuery, state: FSMContext):
    if call.data == b_init.inl_btn_order.callback_data:
        message = '''Ви настиснули кнопку для створення броні!\nВведіть назву препарату для передачі співробітнику аптекі:'''
        await bot.send_message(call.from_user.id, text=message)
        await state.set_state(Form.order)
        await bot.answer_callback_query(call.id)

    
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())