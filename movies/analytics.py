from decimal import Decimal

from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncHour
from django.utils import timezone

from .models import Booking, Payment, Theater


def get_admin_analytics():

    now = timezone.now()

    # ==================================================
    # REVENUE
    # ==================================================

    successful_payments = Payment.objects.filter(
        payment_status="SUCCESS"
    )

    # Daily revenue
    daily_revenue = (
        successful_payments
        .filter(
            updated_at__date=now.date()
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    # Weekly revenue
    weekly_revenue = (
        successful_payments
        .filter(
            updated_at__gte=(
                now - timezone.timedelta(days=7)
            )
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    # Monthly revenue
    monthly_revenue = (
        successful_payments
        .filter(
            updated_at__gte=(
                now - timezone.timedelta(days=30)
            )
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    # ==================================================
    # MOST POPULAR MOVIES
    # ==================================================

    popular_movies = list(
        Booking.objects
        .filter(
            booking_status="CONFIRMED"
        )
        .values(
            "movie_id",
            "movie__name"
        )
        .annotate(
            total_bookings=Count("id")
        )
        .order_by(
            "-total_bookings"
        )[:10]
    )

    # ==================================================
    # BUSIEST THEATERS
    # ==================================================

    theater_data = list(
        Theater.objects
        .annotate(
            total_seats=Count(
                "seat",
                distinct=True
            ),

            booked_seats=Count(
                "seat",
                filter=Q(
                    seat__booking__booking_status=
                    "CONFIRMED"
                ),
                distinct=True
            )
        )
        .values(
            "id",
            "name",
            "movie__name",
            "total_seats",
            "booked_seats"
        )
    )

    for theater in theater_data:

        total = (
            theater["total_seats"] or 0
        )

        booked = (
            theater["booked_seats"] or 0
        )

        if total > 0:

            theater["occupancy_rate"] = round(
                (booked / total) * 100,
                2
            )

        else:

            theater["occupancy_rate"] = 0

    busiest_theaters = sorted(
        theater_data,
        key=lambda x:
        x["occupancy_rate"],
        reverse=True
    )[:10]

    # ==================================================
    # PEAK BOOKING HOURS
    # ==================================================

    peak_hours = list(
        Booking.objects
        .filter(
            booking_status="CONFIRMED"
        )
        .annotate(
            hour=TruncHour("booked_at")
        )
        .values("hour")
        .annotate(
            total_bookings=Count("id")
        )
        .order_by(
            "-total_bookings"
        )[:10]
    )

    for item in peak_hours:

        if item["hour"]:

            item["hour"] = (
                item["hour"]
                .strftime("%H:00")
            )

    # ==================================================
    # CANCELLATION RATE
    # ==================================================

    total_bookings = (
        Booking.objects.count()
    )

    cancelled_bookings = (
        Booking.objects
        .filter(
            booking_status="CANCELLED"
        )
        .count()
    )

    if total_bookings > 0:

        cancellation_rate = round(
            (
                cancelled_bookings
                / total_bookings
            ) * 100,
            2
        )

    else:

        cancellation_rate = 0

    # ==================================================
    # BOOKING STATUS SUMMARY
    # ==================================================

    status_summary = list(
        Booking.objects
        .values(
            "booking_status"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total"
        )
    )

    # ==================================================
    # FINAL RESULT
    # ==================================================

    return {

        "revenue": {

            "daily":
                float(daily_revenue),

            "weekly":
                float(weekly_revenue),

            "monthly":
                float(monthly_revenue),
        },

        "popular_movies":
            popular_movies,

        "busiest_theaters":
            busiest_theaters,

        "peak_hours":
            peak_hours,

        "cancellation": {

            "total_bookings":
                total_bookings,

            "cancelled_bookings":
                cancelled_bookings,

            "rate":
                cancellation_rate,
        },

        "status_summary":
            status_summary,
    }