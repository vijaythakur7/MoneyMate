from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_monthly_report(user_id):
    logger.info(
        "Preparing monthly report for user ID %s",
        user_id,
    )

    return {
        "status": "completed",
        "user_id": user_id,
        "report_type": "monthly",
    }