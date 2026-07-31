from aiogram.fsm.storage.redis import RedisStorage, Redis

redis = Redis(host="redis", port=6379, db=0)
storage = RedisStorage(redis)