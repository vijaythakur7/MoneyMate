from django.core.cache import cache
from django.test import SimpleTestCase

from apps.accounts.services.account_summary_cache import (
    get_cached_summary,
    invalidate_summary_cache,
    set_cached_summary,
)


class AccountSummaryCacheTests(SimpleTestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_summary_can_be_cached_and_retrieved(self):
        summary = {"account_count": 3, "currency": "INR"}

        set_cached_summary(101, summary)

        self.assertEqual(get_cached_summary(101), summary)

    def test_users_have_separate_summary_keys(self):
        set_cached_summary(101, {"account_count": 3})
        set_cached_summary(202, {"account_count": 8})

        self.assertEqual(
            get_cached_summary(101),
            {"account_count": 3},
        )
        self.assertEqual(
            get_cached_summary(202),
            {"account_count": 8},
        )

    def test_invalidation_removes_summary(self):
        set_cached_summary(101, {"account_count": 3})

        invalidate_summary_cache(101)

        self.assertIsNone(get_cached_summary(101))