import logging

from django.core.mail import send_mail
from celery_tasks.main import app

logger = logging.getLogger(__name__)


@app.task
def celery_send_email(subject, message, from_email, recipient_list, html_message):
    sent_count = send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        html_message=html_message,
    )
    logger.info('Email task completed; sent to %s recipient(s)', sent_count)
    return sent_count
