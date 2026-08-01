from flask import request
from flask_login import current_user

from extensions import db
from models import Trip, TripMember


def get_active_trip(trip_id=None):
    """Resolve the current user's trip from query/form param or first trip."""
    if trip_id:
        trip = Trip.query.filter_by(id=int(trip_id), user_id=current_user.id).first()
        if trip:
            return trip
    return Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.asc()).first()


def get_active_trip_from_request():
    trip_id = request.args.get("trip_id") or request.form.get("trip_id")
    return get_active_trip(int(trip_id) if trip_id else None)


def ensure_group_organizer(trip):
    """Add trip owner as Organizer member for group trips."""
    if trip.trip_type != "group":
        return None
    existing = TripMember.query.filter_by(trip_id=trip.id, user_id=trip.user_id).first()
    if existing:
        if existing.role != "Organizer":
            existing.role = "Organizer"
            db.session.commit()
        return existing
    member = TripMember(
        trip_id=trip.id,
        user_id=trip.user_id,
        role="Organizer",
        amount_paid=0.0,
        balance=0.0,
        status="Active",
    )
    db.session.add(member)
    db.session.commit()
    return member


def group_member_count(trip):
    return TripMember.query.filter_by(trip_id=trip.id).count()
