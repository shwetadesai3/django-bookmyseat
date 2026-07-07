import logging

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def send_booking_email(
        self,
        booking_id
):
    try:

        from .models import Booking

        booking = Booking.objects.select_related(
            'user',
            'show'
        ).get(id=booking_id)

        html_content = render_to_string(
            'emails/booking_confirmation.html',
            {
                'booking': booking,
                'user': booking.user,
                'seats': booking.seat_numbers,
                'payment_id': booking.payment_id
            }
        )

        email = EmailMultiAlternatives(
            subject='Ticket Booking Confirmation',
            body='Your booking is confirmed.',
            to=[booking.user.email]
        )

        email.attach_alternative(
            html_content,
            "text/html"
        )

        email.send()

        logger.info(
            f"Booking email sent: {booking.id}"
        )

    except Exception as exc:

        logger.error(
            f"Email failed for booking {booking_id}: {exc}"
        )

        raise self.retry(exc=exc)