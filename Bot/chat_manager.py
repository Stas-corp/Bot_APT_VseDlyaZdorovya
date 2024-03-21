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

class ChatManager:
    def __init__(self):    
        self.admin_id: int
        self.client_id: int

    def set_id_chating(self, admin_id: int, client_id: int):
        self.admin_id = admin_id
        self.client_id = client_id

    async def chating(self, mess: types.Message):
        print(f'Chating between {self.admin_id} and {self.client_id}\nMess from: {mess.from_user.full_name}\nMess text: {mess.text}')
        if mess.from_user.id == self.admin_id:
            await bot.send_message(self.client_id,
                                    mess.text)
            print('adm send mess')
        elif mess.from_user.id == self.client_id:
            await bot.send_message(self.admin_id,
                                    mess.text)
            print('cli send mess')
            