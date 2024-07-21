import asyncio
from datetime import datetime

from DB.db_redis import redis_storage
from Managers.json_manager import JsonManager

class Manager:

    __file_path__ = 'data/users_order.json'

    def __init__(self):
        self.user_id = 'None'
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
    
    @staticmethod
    def order_create(order_data) -> None:
        data = JsonManager(file_path=Manager.__file_path__)._get_data_()
        data[order_data['order_id']] = order_data
        print(order_data)
        JsonManager(file_path=Manager.__file_path__).__save_data__(data)
        # self.clear_all_properties()
        # print(self.__dict__)

    @staticmethod
    def update_order_data(order_id: str, **kwargs):
        '''
        :param order_id: str
        :param kwargs: property_name = value: str
        '''
        data = JsonManager(file_path=Manager.__file_path__)._get_data_()
        for prop_name, value in kwargs.items():
            data[order_id][prop_name] = value
            print(data[order_id])
        JsonManager(file_path=Manager.__file_path__).__save_data__(data)

    @staticmethod
    def get_NotCompletedOrder() -> list:
        ''':return: list ['Замовлення N']'''
        result = []
        data = JsonManager(file_path=Manager.__file_path__)._get_data_()
        for order_id, order_data in data.items():
            if not order_data['order_completed']:
                result.append(f'Замовлення {order_id}')
        return result
    
    @staticmethod
    async def add_order_in_processing(order_id: str):
        ords = await Manager.get_orders_in_processing()
        if not order_id in ords:
            await redis_storage.redis.rpush('order_in_processing', order_id)

    @staticmethod
    async def get_orders_in_processing():
    # Получение всех элементов списка по ключу
        result = await redis_storage.redis.lrange('order_in_processing', 0, -1)
        return [item.decode('utf-8') for item in result]
    
    @staticmethod
    async def del_order_in_processing(order_id: str):
        order = f'Замовлення {order_id}'
        await redis_storage.redis.lrem('order_in_processing', 0, order)
    
    @staticmethod
    def get_order(order_id: str) -> dict:
        data = JsonManager(file_path=Manager.__file_path__)._get_data_()
        return data[order_id]

    def update_property(self, **kwargs) -> None:
        ''':param kwargs: property_name = value: str'''
        for prop_name, value in kwargs.items():
            if hasattr(self, prop_name):
                setattr(self, prop_name, value)
            else:
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{prop_name}'")

    async def get_order_number(self) -> str:
        ''':return: curent order number | str'''
        last_order_id = await redis_storage.redis.get('last_order_id')
        if last_order_id:
            new_order_id = str(int(last_order_id) + 1)
            await redis_storage.redis.set('last_order_id', new_order_id)
            # print(f"{self.__dict__['user_id']} | {self.__dict__['order_id']}")
            return new_order_id
        else:
            data = JsonManager(file_path=self.__file_path__)._get_data_()
            data_len = len(data)
            if data_len == 0:
                await redis_storage.redis.set('last_order_id', '1')
                return '1'
            else:
                order_id = str(int(max(data.keys(), key=int)) + 1)
                await redis_storage.redis.set('last_order_id', order_id)
            # data[self.order_id] = self.__dict__
            # JsonManager(file_path=self.__file_path__).__save_data__(data)
            # print(f"{self.__dict__['user_id']} | {self.__dict__['order_id']}")
            return order_id

if __name__ == '__main__':
    mng = Manager()
    print(mng.get_NotCompletedOrder())
    # print(mng.get_orders_in_processing())
    # mng.update_order_data('86', order_completed=1)

    # mng.__dict__
    # mng.update_property(address='qwe')
    # mng.order_create()
