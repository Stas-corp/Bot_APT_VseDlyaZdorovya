import logging

from aiogram import F, types

import __bot_init__ as b_init

bot = b_init.bot

class ChatManager:
    def __init__(self) -> None:    
        self.admin_id: int
        self.client_id: int

    def set_id_chating(self, admin_id: int, client_id: int):
        self.admin_id = admin_id
        self.client_id = client_id

    def clear_id_chating(self):
        self.admin_id = None
        self.client_id = None

    async def chating(self, mess: types.Message):
        # logging.warn(f'Mess from: {mess.from_user.full_name}\nMess text: {mess.text}')
        if mess.from_user.id == self.admin_id:
            cli_mess = f'Повідомлення від адміністратора 👩‍💻:\n\n{mess.text}'
            await bot.send_message(self.client_id,
                                    text=cli_mess)
            logging.warn(f'adm send mess:\nMess from: {mess.from_user.full_name}\nMess text: {mess.text}')
        elif mess.from_user.id == self.client_id:
            adm_mess = f'Повідомлення від:\n@{mess.from_user.username}\n{mess.from_user.full_name}\n\n{mess.text}'
            await bot.send_message(self.admin_id,
                                    text=adm_mess)
            logging.warn(f'cli send mess:\nMess from: {mess.from_user.full_name}\nMess text: {mess.text}')
            