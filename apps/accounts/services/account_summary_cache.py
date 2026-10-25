from django.core.cache import cache

ACCOUNT_SUMMARY_TIMEOUT = 60


def get_summary_cache_key(user_id):
    return f"account-summary:user:{user_id}"


def get_cached_summary(user_id):
    key = get_summary_cache_key(user_id)
    return cache.get(key)


def set_cached_summary(user_id, summary):
    key = get_summary_cache_key(user_id)
    cache.set(
        key,
        summary,
        timeout=ACCOUNT_SUMMARY_TIMEOUT,
    )


def invalidate_summary_cache(user_id):
    key = get_summary_cache_key(user_id)
    cache.delete(key)