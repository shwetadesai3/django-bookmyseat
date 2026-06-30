from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import Booking


@shared_task(bind=True, max_retries=3)
def send_booking_email(self, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)

        html_message = render_to_string(
            "emails/booking_confirmation.html",
            {
                "user": booking.user,
                "movie": booking.movie.name,
                "theater": booking.theater.name,
                "show_time": booking.show_time,
                "seats": booking.seat_numbers,
                "payment_id": booking.payment_id,
            },
        )

        email = EmailMessage(
            subject="BookMySeat Ticket Confirmation",
            body=html_message,
            to=[booking.user.email],
        )

        email.content_subtype = "html"
        email.send()

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)