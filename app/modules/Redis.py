from flask import current_app
import redis

host = current_app.config.get("REDIS_HOST")
port = current_app.config.get("REDIS_PORT")
redis_client =  redis.StrictRedis(host=host, port=port, db=0)