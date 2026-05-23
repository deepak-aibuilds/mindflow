import redis.asyncio as redis
import os
from app.core import settings

redis_client = redis.from_url(settings.redis_url)

async def get_cache(key:str):
    result = await redis_client.get(key)
    return result.decode('utf-8') if result else None

async def set_cache(key:str, value:str, ttl:int = 60):
    await redis_client.setex(key,ttl,value)

async def delete_cache(key:str):
    await redis_client.delete(key)