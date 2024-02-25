from typing import Dict

import aiogram 

import __bot_init__

bot = __bot_init__.bot

# добавить метод для проверки подлиности ключа
class User:
    def __init__(self) -> None:
        self.user_id: int
        self.user_name: str
        self.key: str
        self.user_keys: Dict[str, str]

    @staticmethod
    def key_validation(key: str) -> bool:
        """ key validity query """
        if key != 'key':
            return True
        else:
            return False

    def set_user_param(self, mess:aiogram.types.Message):
        self.user_id = mess.from_user.id
        self.user_name = mess.from_user.username
        self.user_keys = dict()

    def add_key(self, key: str) -> bool:
        if User.key_validation(key):
            self.key = key
            return True
        else:
            return False

    def add_key_name(self, name: str) -> tuple:
        name_key = name
        self.user_keys[name_key] = self.key
        return self.user_keys[name_key], name_key