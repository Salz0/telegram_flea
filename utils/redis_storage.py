"""
The module that provides the `RedisStorage2` storage for the bot.

It uses the `REDIS_URL` environment variable to connect to the Redis server.
"""
import typing

import dj_redis_url
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from settings import settings

redis_config: dict = dj_redis_url.config(default=settings.REDIS_URL)


def parse_config(config_to_parse: dict[str, typing.Any]) -> dict[str, typing.Any]:
    """
    Parse `redis_config` for `RedisStorage2` by `.lower()`ing the keys.

    Structure of `redis_config`:
        >>> redis_config.keys()
        dict_keys(['DB', 'PASSWORD', 'HOST', 'PORT'])
    """
    return dict((k.lower(), v) for k, v in config_to_parse.items())


# According to the structure above, it's better to write this expression
redis_storage = RedisStorage2(**parse_config(redis_config))
