from flask import current_app
from wechatpy.session.redisstorage import RedisStorage
import Redis
session_interface = RedisStorage(
    Redis.redis_client,
    prefix="wechatpy"
)