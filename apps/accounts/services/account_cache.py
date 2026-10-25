from django.core.cache import cache

ACCOUNT_CACHE_TIMEOUT = 60


def get_account_cache_key(user_id):
    return f"financial_accounts:user:{user_id}"


def get_cached_accounts(user_id):
    cache_key = get_account_cache_key(user_id)
    return cache.get(cache_key)


def set_cached_accounts(user_id, account_data):
    cache_key = get_account_cache_key(user_id)
    cache.set(
        cache_key,
        account_data,
        timeout=ACCOUNT_CACHE_TIMEOUT,
    )


def invalidate_account_cache(user_id):
    cache_key = get_account_cache_key(user_id)
    cache.delete(cache_key)