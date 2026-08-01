from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    avatar = db.Column(db.String(255), nullable=True, default="/static/images/avatar.png")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self):
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return s.dumps(self.email, salt="password-reset-salt")

    @staticmethod
    def verify_reset_token(token, max_age=1800):
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            email = s.loads(token, salt="password-reset-salt", max_age=max_age)
        except (SignatureExpired, BadSignature):
            return None
        return User.query.filter_by(email=email).first()



class Trip(db.Model):
    __tablename__ = "trips"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    destination = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(30), default="Planning")
    trip_type = db.Column(db.String(10), nullable=False, default="group")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("trips", lazy=True))

    @property
    def days_left(self):
        from datetime import date
        today = date.today()
        if self.start_date < today:
            return 0
        return (self.start_date - today).days

    @property
    def current_status(self):
        from datetime import date
        today = date.today()
        if self.end_date < today:
            return "Completed"
        if self.start_date <= today <= self.end_date:
            return "Ongoing"
        return "Upcoming"

    @property
    def status_badge_class(self):
        if self.current_status == "Completed":
            return "bg-secondary text-white"
        if self.current_status == "Ongoing":
            return "bg-success text-white"
        return "bg-primary text-white"


class TripMember(db.Model):
    __tablename__ = "trip_members"
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    display_name = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(50), default="Member")
    amount_paid = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default="Active")
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    trip = db.relationship("Trip", backref=db.backref("members", lazy=True))
    user = db.relationship("User", backref=db.backref("trip_memberships", lazy=True))


class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    day = db.Column(db.Integer, nullable=False)
    time = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Expense(db.Model):
    __tablename__ = "expenses"
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    paid_by = db.Column(db.String(80), nullable=False)
    split_between = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    trip = db.relationship("Trip", backref=db.backref("expenses", lazy=True))


class ExpenseSplit(db.Model):
    __tablename__ = "expense_splits"
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey("expenses.id"), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("trip_members.id"), nullable=False)
    share_amount = db.Column(db.Float, default=0.0)
    split_percentage = db.Column(db.Float, nullable=True)
    
    member = db.relationship("TripMember", backref=db.backref("expense_splits", lazy=True, cascade="all, delete-orphan"))

class Settlement(db.Model):
    __tablename__ = "settlements"
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey("trip_members.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("trip_members.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), default="Completed")
    
    payer = db.relationship("TripMember", foreign_keys=[payer_id])
    receiver = db.relationship("TripMember", foreign_keys=[receiver_id])


class Report(db.Model):
    __tablename__ = "reports"
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=True)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Setting(db.Model):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    notification_email = db.Column(db.Boolean, default=True)
    notification_sms = db.Column(db.Boolean, default=False)
    theme = db.Column(db.String(20), default="Dark")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("settings", lazy=True))


class PackingItem(db.Model):
    __tablename__ = "packing_items"
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("trip_members.id"), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    is_essential = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default="Medium")
    is_packed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    trip = db.relationship("Trip", backref=db.backref("packing_items", lazy=True, cascade="all, delete-orphan"))
    member = db.relationship("TripMember", backref=db.backref("packing_items", lazy=True))
