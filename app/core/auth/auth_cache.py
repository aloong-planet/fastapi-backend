import redis
from msal import SerializableTokenCache

from app.crypto import AESCipher
from app.log import logger


class RedisTokenCache(SerializableTokenCache):
    def __init__(self, redis_conn, encryption_key: str):
        super().__init__()
        self._redis = redis_conn
        self._prefix = "msal_token_cache:"
        self.username = None
        self.cipher = AESCipher(encryption_key.encode())

    def set_user(self, username):
        self.username = username

    def load(self):
        logger.debug(f"load called, username: {self.username}")
        try:
            key = f"{self._prefix}state:{self.username}"
            cache_state = self._redis.get(f"{key}")
            if cache_state:
                decrypted_state = self.cipher.decrypt(cache_state)
                logger.debug(f"Deserializing token cache from Redis: {key}")
                self.deserialize(decrypted_state)
            else:
                logger.debug("No token cache found in Redis")
        except redis.RedisError as e:
            logger.error(f"Error loading cache from redis: {e}")

    def save(self, username):
        logger.debug(f"save called, username: {username}")
        self.set_user(username)
        self.serialize()

    def delete(self, username):
        logger.debug(f"remove called, username: {username}")
        self.set_user(username)
        try:
            key = f"{self._prefix}state:{self.username}"
            logger.debug(f"Deleting token cache from redis: {key}")
            self._redis.delete(f"{key}")
        except redis.RedisError as e:
            logger.error(f"Error deleting cache from redis: {e}")

    def serialize(self) -> str:
        logger.debug("serialize called")
        if not self.has_state_changed:
            return ''
        cache_state = super().serialize()
        encrypted_state = self.cipher.encrypt(cache_state)
        try:
            key = f"{self._prefix}state:{self.username}"
            logger.debug(f"Saving token cache to redis: {key}")
            self._redis.set(f"{key}", encrypted_state, ex=60 * 60 * 12)
            self.has_state_changed = False
        except redis.RedisError as e:
            logger.error(f"Error saving cache to redis: {e}")
        return cache_state

    def deserialize(self, state):
        logger.debug("deserialize called")
        try:
            super().deserialize(state)
            self.has_state_changed = False
        except Exception as e:
            logger.error(f"Error deserializing cache from redis: {e}")
