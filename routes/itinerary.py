import re
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from extensions import db
from forms.trip_forms import ActivityForm
from models import Activity, Trip

bp = Blueprint("itinerary", __name__)


def parse_activity_time(value):
    if not value:
        return datetime.min.time()
    value = value.strip()
    for fmt in ("%I:%M %p", "%I:%M%p", "%H:%M", "%I %p", "%H:%M %p"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    return datetime.min.time()


@bp.route("/itinerary", methods=["GET", "POST"], endpoint="itinerary")
@login_required
def itinerary():
    trip_id = request.args.get("trip_id") or request.form.get("trip_id")
    trip = None
    if trip_id:
        trip = Trip.query.filter_by(id=int(trip_id), user_id=current_user.id).first()
    if not trip:
        trip = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.asc()).first()
    form = ActivityForm()
    activities = Activity.query.filter_by(trip_id=trip.id).all() if trip else []
    activities = sorted(activities, key=lambda act: (act.day, parse_activity_time(act.time)))
    if form.validate_on_submit() and trip:
        activity = Activity(
            trip_id=trip.id,
            day=int(re.sub(r'\D', '', str(form.day.data)) or 1),
            time=form.time.data,
            title=form.title.data,
            description=form.description.data,
        )
        db.session.add(activity)
        db.session.commit()
        flash("Activity added.", "success")
        return redirect(url_for("itinerary.itinerary", trip_id=trip.id))
    return render_template("itinerary.html", form=form, trip=trip, activities=activities, trips=Trip.query.filter_by(user_id=current_user.id).all())


@bp.route("/itinerary/<int:activity_id>/edit", methods=["GET", "POST"], endpoint="edit_activity")
@login_required
def edit_activity(activity_id):
    activity = Activity.query.join(Trip).filter(Activity.id == activity_id, Trip.user_id == current_user.id).first_or_404()
    form = ActivityForm(obj=activity)
    if form.validate_on_submit():
        activity.day = int(re.sub(r'\D', '', str(form.day.data)) or 1)
        activity.time = form.time.data
        activity.title = form.title.data
        activity.description = form.description.data
        db.session.commit()
        flash("Activity updated.", "success")
        return redirect(url_for("itinerary.itinerary", trip_id=activity.trip_id))
    return render_template("edit_activity.html", form=form, activity=activity)


@bp.route("/itinerary/<int:activity_id>/delete", methods=["POST"], endpoint="delete_activity")
@login_required
def delete_activity(activity_id):
    activity = Activity.query.join(Trip).filter(Activity.id == activity_id, Trip.user_id == current_user.id).first_or_404()
    trip_id = activity.trip_id
    db.session.delete(activity)
    db.session.commit()
    flash("Activity deleted.", "success")
    return redirect(url_for("itinerary.itinerary", trip_id=trip_id))


@bp.route("/itinerary/suggest", methods=["POST"], endpoint="suggest_itinerary")
@login_required
def suggest_itinerary():
    trip_id = request.form.get("trip_id")
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first()
    if not trip:
        flash("Trip not found.", "danger")
        return redirect(url_for("itinerary.itinerary"))
        
    duration = (trip.end_date - trip.start_date).days + 1
    if duration <= 0:
        duration = 1
    elif duration > 30: # Limit to 30 days max for safety
        duration = 30
    
    dest = trip.destination or "the city"
    added = 0
    
    # Avoid generating if it already has too many activities
    existing_count = Activity.query.filter_by(trip_id=trip.id).count()
    if existing_count > 0:
        flash("You already have activities planned. Edit them directly or remove them to suggest a clean itinerary.", "warning")
        return redirect(url_for("itinerary.itinerary", trip_id=trip.id))

    for day in range(1, duration + 1):
        if trip.trip_type == "group":
            afternoon_title = "Group Sightseeing / Tour"
            evening_title = "Group Dinner & Drinks"
        else:
            afternoon_title = "Explore Landmarks"
            evening_title = "Dinner & Relax"
            
        activities = [
            {"time": "09:00 AM", "title": f"Breakfast in {dest}", "desc": "Start the day with local breakfast."},
            {"time": "10:30 AM", "title": "Morning Activity", "desc": "Visit a popular local attraction."},
            {"time": "01:00 PM", "title": "Lunch Break", "desc": "Try some famous local cuisine."},
            {"time": "03:00 PM", "title": afternoon_title, "desc": "Continue exploring the area."},
            {"time": "07:30 PM", "title": evening_title, "desc": "Unwind and reflect on the day."}
        ]
        
        for act in activities:
            a = Activity(
                trip_id=trip.id,
                day=day,
                time=act["time"],
                title=act["title"],
                description=act["desc"]
            )
            db.session.add(a)
            added += 1
            
    db.session.commit()
    flash(f"Smart Itinerary generated! Added {added} activities across {duration} days.", "success")
    return redirect(url_for("itinerary.itinerary", trip_id=trip.id))
