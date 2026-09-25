from django.urls import path
from . import views


urlpatterns = [

    # ========================================================
    # MOVIES
    # ========================================================

    path(
        "movies/",
        views.movie_list,
        name="movie_list",
    ),

    path(
        "movie/<int:pk>/",
        views.movie_detail,
        name="movie_detail",
    ),

    # ========================================================
    # THEATERS
    # ========================================================

    path(
        "theaters/<int:movie_id>/",
        views.theater_list,
        name="theater_list",
    ),

    # ========================================================
    # SEAT BOOKING
    # ========================================================

    path(
        "book-seats/<int:theater_id>/",
        views.book_seats,
        name="book_seats",
    ),

    # ========================================================
    # TEMPORARY SEAT RESERVATION
    # ========================================================

    path(
        "reserve-seat/<int:seat_id>/",
        views.reserve_seat_view,
        name="reserve_seat",
    ),

    # ========================================================
    # PAYMENT
    # ========================================================

    path(
        "payment-success/",
        views.payment_success,
        name="payment_success",
    ),

    path(
        "payment-failed/",
        views.payment_failed,
        name="payment_failed",
    ),

    # ========================================================
    # RAZORPAY WEBHOOK
    # ========================================================

    path(
        "razorpay/webhook/",
        views.razorpay_webhook,
        name="razorpay_webhook",
    ),
    path(
    "admin-dashboard/",
    views.admin_dashboard,
    name="admin_dashboard"
),

path(
    "admin-dashboard/api/",
    views.admin_analytics_api,
    name="admin_analytics_api"
),
]
