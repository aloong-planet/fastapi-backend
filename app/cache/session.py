from typing import Tuple, Union
from urllib.parse import (ParseResult, urlencode, urlunparse)

import botocore.session
import redis
import redis.asyncio as aioredis
from botocore.model import ServiceId
from botocore.signers import RequestSigner
from cachetools import TTLCache, cached

from app.configs import APP_SETTINGS
from app.log import logging

log = logging.getLogger(__name__)


class ElastiCacheIAMProvider(redis.CredentialProvider):

    def __init__(self, user: str, cluster_name: str, region: str = "us-west-2"):
        self.user = user
        self.cluster_name = cluster_name
        self.region = region

        session = botocore.session.get_session()
        self.request_signer = RequestSigner(
            ServiceId("elasticache"),
            self.region,
            "elasticache",
            "v4",
            session.get_credentials(),
            session.get_component("event_emitter"),
        )

    @cached(cache=TTLCache(maxsize=APP_SETTINGS.REDIS_IAM_TOKEN_MAX_SIZE,
                           ttl=APP_SETTINGS.REDIS_IAM_TOKEN_TTL))
    def get_credentials(self) -> Union[Tuple[str], Tuple[str, str]]:
        query_params = {"Action": "connect", "User": self.user}
        url = urlunparse(
            ParseResult(
                scheme="https",
                netloc=self.cluster_name,
                path="/",
                query=urlencode(query_params),
                params="",
                fragment="",
            ))
        signed_url = self.request_signer.generate_presigned_url(
            {
                "method": "GET",
                "url": url,
                "body": {},
                "headers": {},
                "context": {}
            },
            operation_name="connect",
            expires_in=900,
            region_name=self.region,
        )

        return (self.user, signed_url.removeprefix("https://"))


async def get_async_redis_connection_pool():
    redis_conn = None

    try:
        if APP_SETTINGS.ENV == 'local':
            redis_conn = await aioredis.from_url(
                url=APP_SETTINGS.REDIS_URI,
                socket_connect_timeout=APP_SETTINGS.REDIS_SOCKET_CONNECT_TIMEOUT,
                socket_timeout=APP_SETTINGS.REDIS_SOCKET_TIMEOUT,
            )
        else:
            iam_cred_provider = ElastiCacheIAMProvider(user=APP_SETTINGS.REDIS_USERNAME,
                                                       cluster_name=APP_SETTINGS.REDIS_CLUSTER_NAME)
            redis_conn = await aioredis.RedisCluster.from_url(
                url=APP_SETTINGS.REDIS_URI,
                socket_connect_timeout=APP_SETTINGS.REDIS_SOCKET_CONNECT_TIMEOUT,
                socket_timeout=APP_SETTINGS.REDIS_SOCKET_TIMEOUT,
                decode_responses=APP_SETTINGS.REDIS_DECODE_RESPONSES,
                credential_provider=iam_cred_provider)
        yield redis_conn
    except (aioredis.AuthenticationError, Exception) as e:
        log.error(f"Having problems during connect Redis {e}")
        raise e


def get_redis_connection_pool():
    redis_conn = None

    try:
        if APP_SETTINGS.ENV == 'local':
            redis_conn = redis.from_url(
                url=APP_SETTINGS.REDIS_URI,
                socket_connect_timeout=APP_SETTINGS.REDIS_SOCKET_CONNECT_TIMEOUT,
                socket_timeout=APP_SETTINGS.REDIS_SOCKET_TIMEOUT,
            )
        else:
            iam_cred_provider = ElastiCacheIAMProvider(user=APP_SETTINGS.REDIS_USERNAME,
                                                       cluster_name=APP_SETTINGS.REDIS_CLUSTER_NAME)
            redis_conn = redis.RedisCluster.from_url(
                url=APP_SETTINGS.REDIS_URI,
                socket_connect_timeout=APP_SETTINGS.REDIS_SOCKET_CONNECT_TIMEOUT,
                socket_timeout=APP_SETTINGS.REDIS_SOCKET_TIMEOUT,
                decode_responses=APP_SETTINGS.REDIS_DECODE_RESPONSES,
                credential_provider=iam_cred_provider)
        yield redis_conn
    except Exception as e:
        log.error(f"Having problems during connect Redis {e}")
        raise e
