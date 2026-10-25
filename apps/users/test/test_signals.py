from django.test import TestCase

from apps.users.models import User


class UserSignalTests(TestCase):

    def test_user_creation_is_logged(self):
        with self.assertLogs(
            "apps.users.signals",
            level="INFO",
        ) as captured:
            User.objects.create_user(
                username="signaluser",
                email="signal@example.com",
                password="StrongTestPass123!",
            )

        self.assertTrue(
            any(
                "A new MoneyMate user was created" in message
                for message in captured.output
            )
        )