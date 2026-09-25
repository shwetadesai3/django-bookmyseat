from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import Seat


# ============================================================
# RESERVATION SETTINGS
# ============================================================

RESERVATION_TIME = timedelta(minutes=2)


# ============================================================
# CUSTOM EXCEPTION
# ============================================================

class SeatReservationError(Exception):
    pass


# ============================================================
# RESERVE SEAT
# ============================================================

@transaction.atomic
def reserve_seat(seat_id, user):
    """
    Atomically reserve one seat for 2 minutes.

    select_for_update() locks the database row so that
    two users cannot reserve the same seat simultaneously.
    """

    # --------------------------------------------------------
    # Lock the seat row
    # --------------------------------------------------------

    seat = (
        Seat.objects
        .select_for_update()
        .select_related("theater")
        .get(id=seat_id)
    )

    now = timezone.now()

    # --------------------------------------------------------
    # Already permanently booked
    # --------------------------------------------------------

    if seat.is_booked:
        raise SeatReservationError(
            "This seat has already been booked."
        )

    # --------------------------------------------------------
    # Remove expired reservation
    # --------------------------------------------------------

    if (
        seat.reserved_until
        and seat.reserved_until <= now
    ):

        seat.reserved_by = None
        seat.reserved_until = None

        seat.save(
            update_fields=[
                "reserved_by",
                "reserved_until",
            ]
        )

    # --------------------------------------------------------
    # Check active reservation
    # --------------------------------------------------------

    if (
        seat.reserved_by_id is not None
        and seat.reserved_until is not None
        and seat.reserved_until > now
    ):

        # Another user owns the reservation
        if seat.reserved_by_id != user.id:

            raise SeatReservationError(
                "This seat is temporarily reserved "
                "by another user."
            )

    # --------------------------------------------------------
    # Reserve seat for current user
    # --------------------------------------------------------

    seat.reserved_by = user

    seat.reserved_until = (
        now + RESERVATION_TIME
    )

    seat.save(
        update_fields=[
            "reserved_by",
            "reserved_until",
        ]
    )

    return seat


# ============================================================
# CHECK RESERVATION OWNER
# ============================================================

def reservation_belongs_to_user(seat, user):
    """
    Check whether the seat is currently reserved
    by the given user and the reservation has not expired.
    """

    now = timezone.now()

    return (
        seat.reserved_by_id == user.id
        and seat.reserved_until is not None
        and seat.reserved_until > now
        and not seat.is_booked
    )


# ============================================================
# CHECK WHETHER RESERVATION IS ACTIVE
# ============================================================

def reservation_is_active(seat):
    """
    Returns True when the seat has an active
    temporary reservation.
    """

    now = timezone.now()

    return (
        seat.reserved_by_id is not None
        and seat.reserved_until is not None
        and seat.reserved_until > now
        and not seat.is_booked
    )


# ============================================================
# RELEASE RESERVATION
# ============================================================

@transaction.atomic
def release_seat_reservation(seat_id):

    seat = (
        Seat.objects
        .select_for_update()
        .get(id=seat_id)
    )

    seat.reserved_by = None
    seat.reserved_until = None

    seat.save(
        update_fields=[
            "reserved_by",
            "reserved_until",
        ]
    )

    return seat