import logging
import time

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_booking_email(user_email, context):
    """
    Send booking confirmation email with retry logic.
    """

    max_retries = 3

    for attempt in range(max_retries):
        try:

            html_content = render_to_string(
                'emails/booking_confirmation.html',
                context
            )

            email = EmailMultiAlternatives(
                subject='Booking Confirmation',
                body='Your booking is confirmed.',
                to=[user_email]
            )

            email.attach_alternative(
                html_content,
                "text/html"
            )

            email.send()

            logger.info(
                f"Email sent successfully to {user_email}"
            )

            return True

        except Exception as e:

            logger.error(
                f"Attempt {attempt+1} failed: {str(e)}"
            )

            time.sleep(5)

    return False