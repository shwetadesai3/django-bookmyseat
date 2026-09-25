from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from urllib.parse import urlparse, parse_qs


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    name = models.CharField(max_length=200)

    image = models.ImageField(upload_to='movies/')

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1
    )

    cast = models.TextField()

    description = models.TextField(
        blank=True,
        null=True
    )

    genres = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='movies'
    )

    language = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movies'
    )

    trailer_url = models.URLField(
        blank=True,
        null=True,
        help_text="Paste YouTube Watch URL"
    )

    def clean(self):
        super().clean()

        if not self.trailer_url:
            return

        try:
            parsed_url = urlparse(
                self.trailer_url.strip()
            )
        except Exception:
            raise ValidationError({
                "trailer_url": "Invalid YouTube URL."
            })

        if parsed_url.scheme != "https":
            raise ValidationError({
                "trailer_url":
                "फक्त HTTPS YouTube URL वापरा."
            })

        allowed_domains = {
            "youtube.com",
            "www.youtube.com",
            "youtu.be",
            "www.youtu.be",
        }

        if parsed_url.netloc.lower() not in allowed_domains:
            raise ValidationError({
                "trailer_url":
                "फक्त YouTube URL allowed आहे."
            })

        video_id = None

        if parsed_url.netloc.lower() in {
            "youtube.com",
            "www.youtube.com"
        }:
            if parsed_url.path == "/watch":
                video_id = parse_qs(
                    parsed_url.query
                ).get("v", [None])[0]

        elif parsed_url.netloc.lower() in {
            "youtu.be",
            "www.youtu.be"
        }:
            video_id = parsed_url.path.strip("/")

        if not video_id:
            raise ValidationError({
                "trailer_url":
                "Valid YouTube video URL द्या."
            })

        if not video_id.replace(
            "-", ""
        ).replace(
            "_", ""
        ).isalnum():
            raise ValidationError({
                "trailer_url":
                "Invalid YouTube video ID."
            })

        if len(video_id) != 11:
            raise ValidationError({
                "trailer_url":
                "Invalid YouTube video ID."
            })

    def __str__(self):
        return self.name


class Theater(models.Model):
    name = models.CharField(max_length=255)

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='theaters'
    )

    time = models.DateTimeField()

    def __str__(self):
        return (
            f'{self.name} - '
            f'{self.movie.name} at {self.time}'
        )


class Seat(models.Model):

    theater = models.ForeignKey(
        Theater,
        on_delete=models.CASCADE
    )

    seat_number = models.CharField(
        max_length=10
    )

    is_booked = models.BooleanField(
        default=False
    )

    reserved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reserved_seats"
    )

    reserved_until = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "theater",
                    "seat_number"
                ],
                name="unique_seat_per_theater"
            )
        ]

        indexes = [
            models.Index(
                fields=[
                    "theater",
                    "is_booked"
                ]
            ),
            models.Index(
                fields=[
                    "reserved_until"
                ]
            ),
            models.Index(
                fields=[
                    "theater",
                    "reserved_until"
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.theater.name} - "
            f"{self.seat_number}"
        )


class Booking(models.Model):

    BOOKING_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("EXPIRED", "Expired"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    seat = models.ForeignKey(
        Seat,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE
    )

    theater = models.ForeignKey(
        Theater,
        on_delete=models.CASCADE
    )

    booked_at = models.DateTimeField(
        auto_now_add=True
    )

    booking_status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS_CHOICES,
        default="PENDING"
    )

    def __str__(self):
        return f"{self.user} - {self.seat.seat_number}"


class Payment(models.Model):

    PAYMENT_METHODS = [
        ('UPI', 'UPI'),
        ('CARD', 'Card'),
        ('NETBANKING', 'Net Banking'),
    ]

    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('TIMEOUT', 'Timeout'),
        ('REFUNDED', 'Refunded'),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    payment_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        blank=True,
        null=True
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='PENDING'
    )

    idempotency_key = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    razorpay_signature = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        indexes = [
            models.Index(
                fields=["payment_status"]
            ),
            models.Index(
                fields=["updated_at"]
            ),
            models.Index(
                fields=["created_at"]
            ),
            models.Index(
                fields=[
                    "payment_status",
                    "updated_at"
                ]
            ),
            models.Index(
                fields=[
                    "payment_status",
                    "created_at"
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.booking.id} - "
            f"{self.razorpay_order_id} - "
            f"{self.payment_status}"
        )


class RazorpayWebhookEvent(models.Model):

    event_id = models.CharField(
        max_length=150,
        unique=True
    )

    event_type = models.CharField(
        max_length=100
    )

    processed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return (
            f"{self.event_type} - "
            f"{self.event_id}"
        )