from datetime import datetime

from Managers.json_manager import Manager as JsonManager

class Manager:

    __file_path__ = 'data/users_order.json'

    def __init__(self):
        self.order_id = 'None'
        self.user_id = 'None'
        self.delivery_type = 'None'
        self.user_name = 'None'
        self.user_fullname = 'None'
        self.phone_number = 'None'
        self.order = 'None'
        self.adress = 'None'
        self.date = 'None'
        self.order_completed = False

    def update_property(self, **kwargs) -> None:
        ''':param kwargs: property_name=value'''
        for prop_name, value in kwargs.items():
            if hasattr(self, prop_name):
                setattr(self, prop_name, value)
            else:
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{prop_name}'")

    def order_create(self) -> None:
        data = JsonManager(file_path=self.__file_path__)._get_data_()
        data_len = len(data)
        if data_len == 0:
            self.order_id = '1'
        else:
            self.order_id = str(int(max(data.keys(), key=int)) + 1)
        print(self.order_id)
        data[self.order_id] = self.__dict__
        JsonManager(file_path=self.__file_path__).__save_data__(data)

if __name__ == '__main__':
    mng = Manager()
    mng.update_property(adress='qwe')
    mng.order_create()
