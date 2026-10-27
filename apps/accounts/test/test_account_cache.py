from django.core.cache import cache
from django.test import SimpleTestCase

from apps.accounts.services.account_cache import (
    get_cached_accounts,
    invalidate_account_cache,
    set_cached_accounts,
)


class AccountCacheTests(SimpleTestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_cached_accounts_can_be_retrieved(self):
        user_id = 101
        account_data = [
            {"id": 1, "name": "Salary Account", "currency": "INR"}
        ]

        set_cached_accounts(user_id, account_data)

        result = get_cached_accounts(user_id)

        self.assertEqual(result, account_data)

    def test_users_have_separate_cache_entries(self):
        set_cached_accounts(101, [{"name": "User A Account"}])
        set_cached_accounts(202, [{"name": "User B Account"}])

        self.assertEqual(
            get_cached_accounts(101),
            [{"name": "User A Account"}],
        )
        self.assertEqual(
            get_cached_accounts(202),
            [{"name": "User B Account"}],
        )

    def test_invalidation_removes_cached_accounts(self):
        set_cached_accounts(101, [{"name": "Salary Account"}])

        invalidate_account_cache(101)

        self.assertIsNone(get_cached_accounts(101))