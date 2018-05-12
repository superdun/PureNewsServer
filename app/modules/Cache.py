from flask import current_app
from werkzeug.contrib.cache import RedisCache
def getCache():
    host = current_app.config.get("REDIS_HOST")
    port = current_app.config.get("REDIS_PORT")
    return RedisCache(host, port)