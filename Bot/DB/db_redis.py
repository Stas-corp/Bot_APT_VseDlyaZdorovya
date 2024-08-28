from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.base import DefaultKeyBuilder
from redis.asyncio.client import Redis

redis_storage = RedisStorage(redis=Redis(host='192.168.3.78', password='1111'),
                             key_builder=DefaultKeyBuilder(with_destiny=True))

'''For SERVER'''
# redis_storage = RedisStorage(redis=Redis(host='localhost'), 
#                              key_builder=DefaultKeyBuilder(with_destiny=True))
