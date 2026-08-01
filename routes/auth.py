from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, or_

from extensions import db
from forms.auth_forms import ChangePasswordForm, ForgotPasswordForm, LoginForm, ProfileForm, RegisterForm, SettingsForm, ResetPasswordForm
from models import Expense, Setting, Trip, User
import smtplib
from email.message import EmailMessage
from flask import current_app

bp = Blueprint("auth", __name__)


@bp.route("/", methods=["GET"], endpoint="home")
def home():
    return render_template("landing.html")


@bp.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.email.data.strip().lower()
        user = User.query.filter(
            or_(func.lower(User.email) == identifier, func.lower(User.username) == identifier)
        ).first()
        if user and user.check_password(form.password.data.strip()):
            login_user(user, remember=form.remember.data)
            flash("Welcome back!", "success")
            return redirect(url_for("main.dashboard"))
        flash("Invalid email or password", "danger")
    return render_template("login.html", form=form)


@bp.route("/register", methods=["GET", "POST"], endpoint="register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        # Use typed username or auto-generate from email prefix
        raw_username = form.username.data.strip() if form.username.data else ""
        username = raw_username.lower() if raw_username else email.split("@")[0].lower()

        # Ensure uniqueness of email
        if User.query.filter(func.lower(User.email) == email).first():
            flash("An account with that email already exists.", "danger")
            return render_template("register.html", form=form)
        # Ensure uniqueness of username (append number if auto-generated collides)
        if User.query.filter(func.lower(User.username) == username).first():
            if raw_username:
                flash("That username is already taken. Please choose another.", "danger")
                return render_template("register.html", form=form)
            # auto-resolve collision by appending a counter
            base = username
            counter = 1
            while User.query.filter(func.lower(User.username) == username).first():
                username = f"{base}{counter}"
                counter += 1

        user = User(username=username, email=email, full_name=form.full_name.data.strip())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        setting = Setting(user_id=user.id)
        db.session.add(setting)
        db.session.commit()
        login_user(user)
        flash("Account created successfully. Your trip dashboard is ready.", "success")
        return redirect(url_for("explorer.hub"))
    return render_template("register.html", form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    reset_url = url_for("auth.reset_password", token=token, _external=True)
    msg = EmailMessage()
    msg.set_content(f"To reset your password, visit the following link:\n{reset_url}\n\nIf you did not make this request then simply ignore this email and no changes will be made.")
    msg['Subject'] = 'Password Reset Request'
    msg['From'] = current_app.config.get("MAIL_DEFAULT_SENDER", "noreply@tripwise.com")
    msg['To'] = user.email

    try:
        if current_app.config.get("MAIL_SERVER"):
            server = smtplib.SMTP(current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"])
            server.starttls()
            if current_app.config.get("MAIL_USERNAME") and current_app.config.get("MAIL_PASSWORD"):
                server.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
            server.send_message(msg)
            server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")


@bp.route("/forgot-password", methods=["GET", "POST"], endpoint="forgot_password")
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter(func.lower(User.email) == form.email.data.lower().strip()).first()
        if user:
            send_reset_email(user)
        flash("If that email exists, a reset link has been sent.", "info")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html", form=form)


@bp.route("/reset-password/<token>", methods=["GET", "POST"], endpoint="reset_password")
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    user = User.verify_reset_token(token)
    if not user:
        flash("That is an invalid or expired token.", "warning")
        return redirect(url_for("auth.forgot_password"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been updated! You are now able to log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("reset_password.html", form=form)


@bp.route("/logout", endpoint="logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@bp.route("/profile", methods=["GET", "POST"], endpoint="profile")
@login_required
def profile():
    from models import Trip
    profile_form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()
    settings_form = SettingsForm()

    if request.method == "POST":
        if "current_password" in request.form and password_form.validate_on_submit():
            if not current_user.check_password(password_form.current_password.data):
                flash("Current password is incorrect.", "danger")
            else:
                current_user.set_password(password_form.new_password.data)
                db.session.commit()
                flash("Password updated successfully.", "success")
                return redirect(url_for("auth.profile"))

        elif "notification_email" in request.form and settings_form.validate_on_submit():
            setting = current_user.settings[0] if current_user.settings else Setting(user_id=current_user.id)
            setting.notification_email = settings_form.notification_email.data
            setting.notification_sms = settings_form.notification_sms.data
            setting.theme = settings_form.theme.data or "Dark"
            if not current_user.settings:
                db.session.add(setting)
            db.session.commit()
            flash("Settings saved.", "success")
            return redirect(url_for("auth.profile"))

        elif "full_name" in request.form and profile_form.validate_on_submit():
            current_user.full_name = profile_form.full_name.data
            current_user.email = profile_form.email.data.lower()
            current_user.username = profile_form.username.data.strip().lower()
            current_user.phone = profile_form.phone.data
            db.session.commit()
            flash("Profile updated successfully.", "success")
            return redirect(url_for("auth.profile"))

    current_setting = current_user.settings[0] if current_user.settings else None
    settings_form.notification_email.data = current_setting.notification_email if current_setting else True
    settings_form.notification_sms.data = current_setting.notification_sms if current_setting else False
    settings_form.theme.data = current_setting.theme if current_setting else "Dark"

    trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.desc()).all()
    
    total_trips = len(trips)
    total_budget = sum(trip.budget for trip in trips)
    total_expenses = sum(exp.amount for trip in trips for exp in trip.expenses)
    remaining_budget = total_budget - total_expenses
    
    return render_template(
        "profile.html",
        profile_form=profile_form,
        password_form=password_form,
        settings_form=settings_form,
        trips=trips,
        total_trips=total_trips,
        total_budget=total_budget,
        total_expenses=total_expenses,
        remaining_budget=remaining_budget,
    )

