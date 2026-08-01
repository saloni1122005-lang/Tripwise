from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from extensions import db
from forms.auth_forms import ChangePasswordForm, ProfileForm, SettingsForm
from models import Setting

bp = Blueprint("settings", __name__)


@bp.route("/settings", methods=["GET", "POST"], endpoint="settings")
@login_required
def settings():
    profile_form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()
    settings_form = SettingsForm()

    if request.method == "POST" and "current_password" in request.form:
        if password_form.validate_on_submit():
            if not current_user.check_password(password_form.current_password.data):
                flash("Current password is incorrect.", "danger")
            else:
                current_user.set_password(password_form.new_password.data)
                db.session.commit()
                flash("Password updated successfully.", "success")
                return redirect(url_for("settings.settings"))

    if request.method == "POST" and "notification_email" in request.form:
        if settings_form.validate_on_submit():
            setting = current_user.settings[0] if current_user.settings else Setting(user_id=current_user.id)
            setting.notification_email = settings_form.notification_email.data
            setting.notification_sms = settings_form.notification_sms.data
            setting.theme = settings_form.theme.data or "Dark"
            if not current_user.settings:
                db.session.add(setting)
            db.session.commit()
            flash("Settings saved.", "success")
            return redirect(url_for("settings.settings"))

    if request.method == "POST" and "full_name" in request.form:
        if profile_form.validate_on_submit():
            current_user.full_name = profile_form.full_name.data
            current_user.email = profile_form.email.data.lower()
            current_user.username = profile_form.username.data
            current_user.phone = profile_form.phone.data
            db.session.commit()
            flash("Profile updated successfully.", "success")
            return redirect(url_for("settings.settings"))

    current_setting = current_user.settings[0] if current_user.settings else None
    settings_form.notification_email.data = current_setting.notification_email if current_setting else True
    settings_form.notification_sms.data = current_setting.notification_sms if current_setting else False
    settings_form.theme.data = current_setting.theme if current_setting else "Dark"
    return render_template("settings.html", profile_form=profile_form, password_form=password_form, settings_form=settings_form)
