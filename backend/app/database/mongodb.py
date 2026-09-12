from functools import lru_cache

from pymongo import MongoClient

from app.config import get_settings


@lru_cache
def get_mongo_client() -> MongoClient:
    """Create the shared client lazily so health checks do not require MongoDB."""
    settings = get_settings()
    return MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)


def get_database():
    settings = get_settings()
    return get_mongo_client()[settings.mongodb_database]


def close_mongo_client() -> None:
    if get_mongo_client.cache_info().currsize:
        get_mongo_client().close()
        get_mongo_client.cache_clear()