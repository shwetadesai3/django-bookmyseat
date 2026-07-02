from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Booking
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_booking_email(self, booking_id):

    try:
        booking = Booking.objects.select_related(
            'user',
            'movie',
            'theater'
        ).get(id=booking_id)

        seats = booking.seat.seat_number

        html_content = render_to_string(
            'emails/booking_confirmation.html',
            {
                'booking': booking,
                'user': booking.user,
                'seats': seats,
            }
        )

        email = EmailMultiAlternatives(
            subject="Booking Confirmation",
            body="Your booking has been confirmed.",
            from_email=None,
            to=[booking.user.email]
        )

        email.attach_alternative(
            html_content,
            "text/html"
        )

        email.send()

        logger.info(
            f"Booking email sent successfully. Booking ID: {booking.id}"
        )

    except Booking.DoesNotExist:
        logger.error(
            f"Booking not found. Booking ID: {booking_id}"
        )

    except Exception as exc:

        logger.error(
            f"Email failed for booking {booking_id}: {exc}"
        )

        raise self.retry(
            exc=exc,
            countdown=60
        )