from datetime import datetime

from Managers.json_manager import Manager as JsonManager

class Manager:
    def __init__(self):
        self.__file_path__ = 'data/users_order.json'
        self.order_id = str
        self.user_id: str
        self.delivery_type: str
        self.user_name: str
        self.user_fullname: str
        self.phone_number: str
        self.order: str
        self.adress: str
        self.date: str
        self.order_completed = False

    def update_property(self, **kwargs) -> None:
        ''':param kwargs: property_name=value'''
        for prop_name, value in kwargs:
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

if __name__ == '__main__':
    mng = Manager()
    mng.order_create()