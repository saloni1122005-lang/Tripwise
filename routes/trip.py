from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from extensions import db
from forms.trip_forms import TripForm
from models import Trip

bp = Blueprint("trips", __name__)


@bp.route("/trips", methods=["GET", "POST"], endpoint="trips")
@login_required
def trips():
    return redirect(url_for("explorer.hub"))


@bp.route("/trips/<int:trip_id>", endpoint="trip_detail")
@login_required
def trip_detail(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    return render_template("trip_detail.html", trip=trip)


@bp.route("/trips/<int:trip_id>/edit", methods=["GET", "POST"], endpoint="edit_trip")
@login_required
def edit_trip(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    form = TripForm(obj=trip)
    if form.validate_on_submit():
        trip.name = form.name.data
        trip.destination = form.destination.data
        trip.start_date = form.start_date.data
        trip.end_date = form.end_date.data
        trip.budget = form.budget.data
        trip.description = form.description.data
        trip.status = form.status.data
        trip.trip_type = form.trip_type.data
        
        # same as create
        image = form.cover_image.data

        if image and hasattr(image, "filename") and image.filename:
            filename = secure_filename(image.filename)
            image.save(f"static/images/{filename}")
            trip.cover_image = f"/static/images/{filename}"

        db.session.commit()
        flash("Trip updated successfully.", "success")
        return redirect(url_for("trips.trips"))
    return render_template("edit_trip.html", form=form, trip=trip)


@bp.route("/trips/<int:trip_id>/members/<int:member_id>/delete", methods=["POST"], endpoint="delete_member")
@login_required
def delete_member(trip_id, member_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    from models import TripMember
    member = TripMember.query.filter_by(id=member_id, trip_id=trip.id).first_or_404()
    db.session.delete(member)
    db.session.commit()
    flash('Member removed.', 'success')
    return redirect(url_for('trips.edit_trip', trip_id=trip.id))


@bp.route("/trips/<int:trip_id>/delete", methods=["POST"], endpoint="delete_trip")
@login_required
def delete_trip(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()

    from models import TripMember, Activity, Expense, ExpenseSplit, Settlement, Report

    expenses = Expense.query.filter_by(trip_id=trip.id).all()
    for exp in expenses:
        db.session.query(ExpenseSplit).filter_by(expense_id=exp.id).delete()

    db.session.query(Expense).filter_by(trip_id=trip.id).delete()
    db.session.query(Settlement).filter_by(trip_id=trip.id).delete()
    db.session.query(TripMember).filter_by(trip_id=trip.id).delete()
    db.session.query(Activity).filter_by(trip_id=trip.id).delete()
    db.session.query(Report).filter_by(trip_id=trip.id).delete()

    db.session.delete(trip)
    db.session.commit()
    flash("Trip removed.", "success")
    return redirect(url_for("main.dashboard"))
