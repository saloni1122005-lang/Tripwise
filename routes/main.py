import datetime
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from extensions import db
from models import Activity, Expense, Trip, TripMember

bp = Blueprint("main", __name__)


@bp.context_processor
def inject_user_data():
    return {
        "current_user": current_user,
        "is_authenticated": current_user.is_authenticated,
    }


@bp.route("/dashboard", endpoint="dashboard")
@login_required
def dashboard():
    trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.asc()).all()
    selected_trip = None
    if trips:
        selected_trip = trips[0]
        trip_id = request.args.get("trip_id")
        if trip_id:
            selected_trip = next((trip for trip in trips if str(trip.id) == trip_id), selected_trip)
    total_budget = sum(trip.budget for trip in trips)
    total_expenses = sum(exp.amount for trip in trips for exp in trip.expenses)
    remaining_budget = total_budget - total_expenses
    members_count = sum(len(trip.members) for trip in trips)
    recent_expenses = []
    for trip in trips:
        recent_expenses.extend(trip.expenses)
    recent_expenses = sorted(recent_expenses, key=lambda item: item.created_at, reverse=True)[:5]
    recent_activities = []
    for trip in trips:
        recent_activities.extend(trip.expenses)
    recent_activities = sorted(recent_activities, key=lambda item: item.created_at, reverse=True)[:5]
    return render_template(
        "dashboard.html",
        trips=trips,
        selected_trip=selected_trip,
        total_budget=total_budget,
        total_expenses=total_expenses,
        remaining_budget=remaining_budget,
        members_count=members_count,
        recent_expenses=recent_expenses,
        recent_activities=recent_activities,
    )


def seed_demo_data(user):
    if Trip.query.filter_by(user_id=user.id).count():
        return
    trip = Trip(
        name="Alpine Escape",
        destination="Swiss Alps",
        start_date=datetime.date(2026, 8, 15),
        end_date=datetime.date(2026, 8, 21),
        budget=6500.0,
        description="A premium mountain retreat for a close-knit friend group.",
        status="Planning",
        trip_type="group",
        user_id=user.id,
    )
    db.session.add(trip)
    db.session.flush()
    db.session.add_all([
        TripMember(trip_id=trip.id, user_id=user.id, role="Organizer", amount_paid=1800.0, balance=0.0, status="Active"),
        TripMember(trip_id=trip.id, user_id=user.id, role="Member", amount_paid=1200.0, balance=0.0, status="Active"),
    ])
    db.session.add_all([
        Activity(trip_id=trip.id, day=1, time="09:00", title="Flight", description="Morning departure"),
        Activity(trip_id=trip.id, day=1, time="11:00", title="Hotel Check-in", description="Lodge arrival"),
        Activity(trip_id=trip.id, day=2, time="08:00", title="Mountain Hike", description="Scenic trail"),
    ])
    db.session.add_all([
        Expense(trip_id=trip.id, title="Dinner", category="Food", amount=180.0, paid_by=user.full_name or user.username, split_between="Alex,Mina", date=datetime.date(2026, 8, 15), notes="Group dinner"),
        Expense(trip_id=trip.id, title="Cable Car", category="Activities", amount=120.0, paid_by=user.full_name or user.username, split_between="Alex,Mina", date=datetime.date(2026, 8, 16), notes="Hiking pass"),
    ])
    db.session.commit()
