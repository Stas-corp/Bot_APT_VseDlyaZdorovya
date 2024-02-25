import asyncio

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
    key = State()
    name_key = State()

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я телеграм бот аптеки. Отправьте мне сообщение для сделки заказа.")

@dp.message()
async def order_received(message: types.Message):
    admin_message = f"Получен новый заказ:\n\n{message.text}"
    await bot.send_message(chat_id=admin_chat_ids[-1], text=admin_message)

    client_reply = "Ваш заказ принят. Мы скоро с вами свяжемся!"
    await message.reply(client_reply)

@dp.callback_query(lambda call:True)
async def caller(call: types.CallbackQuery, state: FSMContext):
    
    await bot.send_message(call.from_user.id, "Вы нажали на кнопку начала чата.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())