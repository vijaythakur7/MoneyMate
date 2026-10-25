from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_monthly_report(user_id):
    logger.info(
        "Preparing monthly report for user ID %s",
        user_id,
    )

    try:
        # Replace this with the real report-generation logic.
        result = {
            "status": "completed",
            "user_id": user_id,
        }

        logger.info(
            "Monthly report task completed for user ID %s",
            user_id,
        )

        return result

    except Exception:
        logger.exception(
            "Monthly report task failed for user ID %s",
            user_id,
        )
        raise