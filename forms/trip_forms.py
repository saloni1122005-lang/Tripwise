from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, DateField, TextAreaField, SelectField, SelectMultipleField, SubmitField, widgets
from wtforms.validators import DataRequired, Length, Optional


class TripForm(FlaskForm):
    name = StringField("Trip Name", validators=[DataRequired(), Length(max=150)])
    destination = StringField("Destination", validators=[DataRequired(), Length(max=150)])
    start_date = DateField("Start Date", validators=[DataRequired()])
    end_date = DateField("End Date", validators=[DataRequired()])
    budget = FloatField("Budget", validators=[Optional()], default=0.0)
    description = TextAreaField("Description")
    status = SelectField("Status", choices=[("Planning", "Planning"), ("Confirmed", "Confirmed"), ("Ongoing", "Ongoing"), ("Completed", "Completed")], default="Planning")
    trip_type = SelectField("Trip Type", choices=[("solo", "👤 Solo Trip"), ("group", "👥 Group Trip")], default="group", validators=[DataRequired()])
    cover_image = FileField("Cover Image", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only!")])
    submit = SubmitField("Save Trip")


class ActivityForm(FlaskForm):
    day = StringField("Day", validators=[DataRequired()])
    time = StringField("Time", validators=[DataRequired()])
    title = StringField("Activity", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Description")
    submit = SubmitField("Save Activity")


class ExpenseForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    category = SelectField("Category", choices=[("Food", "Food"), ("Hotel", "Hotel"), ("Fuel", "Fuel"), ("Transport", "Transport"), ("Shopping", "Shopping"), ("Activities", "Activities"), ("Other", "Other")], validators=[DataRequired()])
    amount = FloatField("Amount", validators=[DataRequired()])
    paid_by = SelectField("Paid By", coerce=int, validators=[DataRequired()])
    split_type = SelectField("Split Type", choices=[("equal", "Equal Split"), ("percentage", "Percentage Split"), ("custom", "Custom Amount Split")], validators=[DataRequired()])
    split_between = SelectMultipleField("Split Between", coerce=int, validators=[DataRequired()], widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput())
    date = DateField("Date", validators=[DataRequired()])
    notes = TextAreaField("Notes")
    submit = SubmitField("Save Expense")


