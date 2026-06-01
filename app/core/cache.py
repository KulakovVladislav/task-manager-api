import json
from typing import Optional
from app.core.redis import redis_client

from app.config import settings


def cache_key(user_id: int, completed: Optional[bool], priority: Optional[int], limit: int, offset: int, sort_by: str,
              order: str):
    return f"tasks:user:{user_id}:comp:{completed}:prio:{priority}:lim:{limit}:off:{offset}:sb:{sort_by}:ord:{order}"


def invalidate_user_tasks_cache(user_id: int, redis_client):
    pattern = f"tasks:user:{user_id}:*"
    cursor = 0
    while True:
        cursor, keys_list = redis_client.scan(
            cursor=cursor,
            match=pattern,
            count=100
        )
        if keys_list:
            redis_client.delete(*keys_list)
        if cursor == 0:
            break


def get_cached_data(redis_client, key):
    cached = redis.get(key)
    if cached is not None:
        data = json.loads(cached)
        return data


def set_cached_data(redis_client, key, data):
    data = [TaskResponse.model_validate(task).model_dump() for task in db_tasks]
    serialized = json.dumps(data)
    redis.set(key, serialized, ex=settings.tasks_cache_ttl)
