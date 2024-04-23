import json
import os

class Manager:
    def __init__(self) -> None:
        self.file_path = 'data/users_data.json'
        self.check_path()

    def check_path(self):
        directory = os.path.dirname(self.file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def login_user(self, user_id: str) -> bool:
        '''Checks the user in the database'''
        data = self._get_data_()
        if user_id in data:
            return True
        else:
            return False

    def _get_data_(self) -> dict:
        if not os.stat(self.file_path).st_size == 0:
            with open(self.file_path, 'r', encoding="utf-8") as file:
                return json.load(file)
        else:
            return {}

    def __save_data__(self, data) -> None:
        with open(self.file_path, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def add_full_name(self, user_id: str, full_name: str):
        data = self._get_data_()
        data[user_id]['full_name'] = full_name
        self.__save_data__(data)

    def add_adress(self, user_id: str, adress: str) -> None:
        data = self._get_data_()
        data[user_id]['adress'] = adress
        self.__save_data__(data)

    def add_np_adress(self, user_id: str, adress: str) -> None:
        data = self._get_data_()
        data[user_id]['adress_np'] = adress
        self.__save_data__(data)

    def get_phone_number(self, user_id: str) -> str | None:
        data = self._get_data_()
        if self.login_user(user_id) and data[user_id].get('number') is not None:
            return data[user_id]['number']
        else:
            return None

    def get_adress(self, user_id: str) -> str | None:
        '''Return user adress or Note'''
        data = self._get_data_()
        if self.login_user(user_id) and data[user_id].get('adress') is not None:
            return data[user_id]['adress']
        else:
            return None

    def get_np_adress(self, user_id: str) -> str | None:
        '''Return user adress for NovaPoshta or Note'''
        data = self._get_data_()
        if self.login_user(user_id) and data[user_id].get('adress_np') is not None:
            return data[user_id]['adress_np']
        else:
            return None
        
    def get_full_name(self, user_id: str) -> str | None:
        '''Return user full name or Note'''
        data = self._get_data_()
        if self.login_user(user_id) and data[user_id].get('full_name') is not None:
            return data[user_id]['full_name']
        else:
            return None

    def add_user(self, user_data: dict):
        data = self._get_data_()
        key = list(user_data.keys())[0]
        # print(f'_______data_json_______\n{data}')
        print('_______NEW USER_______')
        print(f'_______key_______\n{key}')
        print(f'_______user_data_______\n{user_data}')
        if not key in data:
            data[key] = user_data[key]
            self.__save_data__(data)


if __name__ == '__main__':
    mng = Manager()
    print(mng.get_adress('5493395971'))
    print(mng.get_phone_number('5493395977'))
    print(mng.get_full_name('656334227'))