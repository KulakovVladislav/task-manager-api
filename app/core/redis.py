import redis

from app.config import settings

redis_client = None


def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True
        )
    return redis_client
