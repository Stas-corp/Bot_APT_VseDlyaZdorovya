from datetime import datetime

from Managers.json_manager import Manager as JsonManager

class Manager:

    __file_path__ = 'data/users_order.json'
    __orders__ = dict()

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

    def update_property(self, id: str, **kwargs) -> None:
        '''
        :param user_id: user id in Telegram: str
        :param kwargs: property_name = value: str
        '''
        for prop_name, value in kwargs.items():
            if hasattr(self, prop_name):
                setattr(self, prop_name, value)
            else:
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{prop_name}'")
        self.__orders__[id] = self.__dict__

    def get_property(self, id: str, property_name: str) -> None | str:
        """
        Returns the value of the specified property for the given user.

        :param id: user id Telegram.
        :param property_name: name of the property.
        :return: value of the property.
        """
        if id in self.__orders__ and property_name in self.__orders__[id]:
            print(f'{self.__class__} {self.__class__.__name__} {self.__orders__[id][property_name]}')
            return self.__orders__[id][property_name]
        else:
            print(f'{self.__class__} {self.__class__.__name__} {None}')
            return None

    def get_order_number(self, id: str) -> str:
        ''':return: curent order number | str'''
        data = JsonManager(file_path=self.__file_path__)._get_data_()
        data_len = len(data)
        if data_len == 0:
            self.update_property(id, 
                                 order_id='1')
        else:
            self.update_property(id, 
                                 order_id=str(int(max(data.keys(), key=int)) + 1))
        return self.__orders__[id]['order_id']

    def order_create(self, id: str) -> None:
        data = JsonManager(file_path=self.__file_path__)._get_data_()
        data[self.get_property(id, 'order_id')] = self.__orders__[id]
        print(self.__orders__[id])
        JsonManager(file_path=self.__file_path__).__save_data__(data)
        # self.clear_all_properties()
        del self.__orders__[id]
        print(self.__dict__)

    def clear_all_properties(self):
        for attr in dir(self):
            if not attr.startswith('__') and not callable(getattr(self, attr)):
                setattr(self, attr, 'None')

if __name__ == '__main__':
    mng = Manager()
    mng.update_property(adress='qwe')
    mng.order_create()
