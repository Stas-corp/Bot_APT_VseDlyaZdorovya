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
    
    def login_user(self, id: str) -> bool:
        data = self._load_data()
        if id in data:
            return True
        else:
            return False

    def _load_data(self) -> dict:
        if not os.stat(self.file_path).st_size == 0:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        else:
            return {}

    def __save_data(self, data):
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def add_user(self, user_data: dict):
        data = self._load_data()
        key = list(user_data.keys())[0]
        print(f'_______data_json_______\n{data}')
        print(f'_______key_______\n{key}')
        print(f'_______user_data_______\n{user_data}')
        if not key in data:
            data[key] = user_data[key]
            self.__save_data(data)