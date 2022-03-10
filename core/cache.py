from cache_helper.cache import Cache


class AppCache(Cache):
    key_patterns = {
        "deleted_message": "deleted_{msg_id}_{user_id}",
        "pv_id": "pv_{}_{}",
        "guid": "guid_{}",
    }


cache = AppCache()
