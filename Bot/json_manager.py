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
        data = self._load_data()
        if user_id in data:
            return True
        else:
            return False

    def _load_data(self) -> dict:
        if not os.stat(self.file_path).st_size == 0:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        else:
            return {}

    def __save_data(self, data) -> None:
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def add_adress(self, user_id: str, adress: str) -> None:
        data = self._load_data()
        data[user_id]['adress'] = adress
        self.__save_data(data)

    def get_adress(self, user_id: str) -> str | None:
        '''Return user adress or Note'''
        data = self._load_data()
        if self.login_user(user_id) and data[user_id].get('adress') is not None:
            return data[user_id]['adress']
        else:
            return None

    def add_user(self, user_data: dict):
        data = self._load_data()
        key = list(user_data.keys())[0]
        # print(f'_______data_json_______\n{data}')
        print('_______NEW USER_______')
        print(f'_______key_______\n{key}')
        print(f'_______user_data_______\n{user_data}')
        if not key in data:
            data[key] = user_data[key]
            self.__save_data(data)


if __name__ == '__main__':
    mng = Manager()
    print(mng.get_adress('5493395971'))