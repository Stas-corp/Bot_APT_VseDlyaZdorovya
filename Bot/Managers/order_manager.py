from datetime import datetime

from Managers.json_manager import JsonManager

class Manager:

    __file_path__ = 'data/users_order.json'

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.order_id = 'None'
        self.delivery_type = 'None'
        self.user_name = 'None'
        self.full_name = 'None'
        self.phone_number = 'None'
        self.order = 'None'
        self.address = 'None'
        self.date = 'None'
        self.order_completed = False

    @property
    def __conver_dict__(self):
        obj_dict = self.__dict__
        obj_dict['order_completed'] = int(obj_dict['order_completed'])
        return obj_dict

    def update_property(self, **kwargs) -> None:
        ''':param kwargs: property_name = value: str'''
        for prop_name, value in kwargs.items():
            if hasattr(self, prop_name):
                setattr(self, prop_name, value)
            else:
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{prop_name}'")

    def get_order_number(self) -> str:
        ''':return: curent order number | str'''
        data = JsonManager(file_path=self.__file_path__)._get_data_()
        data_len = len(data)
        if data_len == 0:
            self.order_id = '1'
        else:
            self.order_id = str(int(max(data.keys(), key=int)) + 1)
        data = JsonManager(file_path=self.__file_path__)._get_data_()
        data[self.order_id] = self.__dict__
        print(f"{self.__dict__['user_id']} | {self.__dict__['order_id']}")
        JsonManager(file_path=self.__file_path__).__save_data__(data)
        return self.order_id
    
    @staticmethod
    def order_create(order_data) -> None:
        data = JsonManager(file_path=Manager.__file_path__)._get_data_()
        data[order_data['order_id']] = order_data
        print(order_data)
        JsonManager(file_path=Manager.__file_path__).__save_data__(data)
        # self.clear_all_properties()
        # print(self.__dict__)

    def clear_all_properties(self):
        for attr in dir(self):
            if not attr.startswith('__') and not callable(getattr(self, attr)):
                setattr(self, attr, 'None')

if __name__ == '__main__':
    mng = Manager()
    mng.__dict__
    mng.update_property(address='qwe')
    mng.order_create()
