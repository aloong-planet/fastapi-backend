import json
from abc import abstractmethod, ABC
from typing import Optional, Any

import redis

from app.log import logger


class BaseRedisCache(ABC):

    @abstractmethod
    def set(self, key: str, value: Any):
        """Setting key to Redis

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Getting key to Redis

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()

    @abstractmethod
    def delete(self, key: str):
        """Deleting key to Redis

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()


class BaseAsyncRedisCache(ABC):

    @abstractmethod
    async def set(self, key: str, value: Any):
        """Setting key to Redis

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Getting key to Redis

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, key: str):
        """Deleting key to Redis

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()


class RedisCache(BaseRedisCache):
    def __init__(self, redis_conn: redis.Redis, prefix: str = "", expiration: int = 60 * 60 * 12):
        """
        Initialize the cache with a Redis connection, an optional key prefix, and a default expiration time.

        :param redis_conn: The Redis connection instance.
        :param prefix: Optional prefix to prepend to all keys.
        :param expiration: Default expiration time in seconds.
        """
        self.redis = redis_conn
        self.prefix = prefix
        self.expiration = expiration

    def set(self, key: str, value: Any):
        """
        Save a value to Redis, automatically serializing to JSON.

        :param key: The key under which to store the value.
        :param value: The value to store.
        """
        full_key = f"{self.prefix}{key}"
        logger.debug(f"Saving key {full_key}")
        self.redis.set(full_key, json.dumps(value), self.expiration)

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from Redis by key, automatically deserializing from JSON.

        :param key: The key of the value to retrieve.
        :return: The deserialized value if key exists, otherwise None.
        """
        full_key = f"{self.prefix}{key}"
        logger.debug(f"Getting key {full_key}")
        value = self.redis.get(full_key)
        return json.loads(value) if value else None

    def delete(self, key: str):
        """
        Delete a value from Redis by key.

        :param key: The key of the value to delete.
        """
        full_key = f"{self.prefix}{key}"
        self.redis.delete(full_key)


class AsyncRedisCache(BaseAsyncRedisCache):
    def __init__(self, redis_conn: redis.Redis, prefix: str = "", expiration: int = 60 * 60 * 12):
        """
        Initialize the cache with a Redis connection, an optional key prefix, and a default expiration time.

        :param redis_conn: The Redis connection instance.
        :param prefix: Optional prefix to prepend to all keys.
        :param expiration: Default expiration time in seconds.
        """
        self.redis = redis_conn
        self.prefix = prefix
        self.expiration = expiration

    async def set(self, key: str, value: Any):
        """
        Save a value to Redis, automatically serializing to JSON.

        :param key: The key under which to store the value.
        :param value: The value to store.
        """
        full_key = f"{self.prefix}{key}"
        logger.debug(f"Saving key {full_key}")
        await self.redis.set(full_key, json.dumps(value), self.expiration)

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from Redis by key, automatically deserializing from JSON.

        :param key: The key of the value to retrieve.
        :return: The deserialized value if key exists, otherwise None.
        """
        full_key = f"{self.prefix}{key}"
        logger.debug(f"Getting key {full_key}")
        value = await self.redis.get(full_key)
        return json.loads(value) if value else None

    async def delete(self, key: str):
        """
        Delete a value from Redis by key.

        :param key: The key of the value to delete.
        """
        full_key = f"{self.prefix}{key}"
        await self.redis.delete(full_key)
