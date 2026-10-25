import logging

from django.test import SimpleTestCase


def log_report_failure(user_id):
    logger = logging.getLogger(__name__)
    logger.error(
        "Monthly report failed for user ID %s",
        user_id,
    )


class ReportLoggingTests(SimpleTestCase):

    def test_report_failure_is_logged(self):
        with self.assertLogs(
            level="ERROR"
        ) as captured:
            log_report_failure(123)

        self.assertIn(
            "Monthly report failed for user ID 123",
            captured.output[0],
        )