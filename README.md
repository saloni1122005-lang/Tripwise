# TripWise

TripWise is a polished Flask-based web application for group travel planning. It includes authentication, trip management, itinerary planning, expense tracking, member management, reports, and settings.

## Features
- Register, login, logout, forgot password, and profile management
- Create, edit, delete, and view trips
- Day-wise itinerary planning
- Expense tracking with budgeting and split logic
- Member management
- Charts and PDF report export
- Premium responsive UI

## Tech Stack
- Flask
- Flask SQLAlchemy
- Flask Login
- Flask WTForms
- MySQL
- Bootstrap 5
- Font Awesome

## Setup
1. Create a MySQL database named `tripwise`.
2. Update the database connection in `config.py` if needed.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Run the app:
   `python app.py`

## Notes
- The app seeds demo trip content for a first-time logged-in user.
- Ensure MySQL is running before launching the app.
