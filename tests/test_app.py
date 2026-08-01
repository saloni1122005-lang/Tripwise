import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


def test_home_redirects_to_login():
    client = app.test_client()
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_login_page_loads():
    client = app.test_client()
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Welcome back" in response.data


def test_valid_login_redirects_to_dashboard():
    client = app.test_client()
    with app.app_context():
        from models import User, db

        db.drop_all()
        db.create_all()
        user = User(username="tester", email="tester@example.com", full_name="Tester")
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()

    login_page = client.get("/login")
    csrf_match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', login_page.get_data(as_text=True))
    assert csrf_match, "expected CSRF token in login page"

    response = client.post(
        "/login",
        data={
            "email": "tester@example.com",
            "password": "secret123",
            "csrf_token": csrf_match.group(1),
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")


def test_group_trip_creation_with_members_persists_trip_members():
    client = app.test_client()
    with app.app_context():
        from models import User, TripMember, db

        db.drop_all()
        db.create_all()
        user = User(username="tester3", email="tester3@example.com", full_name="Tester Three")
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()

    login_page = client.get("/login")
    csrf_match = re.search(r'name="csrf_token" type="hidden" value="([^\"]+)"', login_page.get_data(as_text=True))
    assert csrf_match, "expected CSRF token in login page"

    login_response = client.post(
        "/login",
        data={
            "email": "tester3@example.com",
            "password": "secret123",
            "csrf_token": csrf_match.group(1),
        },
        follow_redirects=True,
    )
    assert login_response.status_code == 200

    explore_page = client.get("/explore")
    csrf_match = re.search(r'name="csrf_token" type="hidden" value="([^\"]+)"', explore_page.get_data(as_text=True))
    assert csrf_match, "expected CSRF token in explorer page"

    create_response = client.post(
        "/explore",
        data={
            "csrf_token": csrf_match.group(1),
            "name": "Group Trip Test",
            "destination": "Goa",
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
            "budget": "1500",
            "status": "Planning",
            "trip_type": "group",
            "member_name_0": "Alice",
            "member_name_1": "Bob",
        },
        follow_redirects=True,
    )
    assert create_response.status_code == 200
    assert b"<!doctype html>" in create_response.data

    with app.app_context():
        from models import TripMember

        members = TripMember.query.order_by(TripMember.id).all()
        assert len(members) == 3
        assert any(m.display_name == "Alice" for m in members)
        assert any(m.display_name == "Bob" for m in members)
        assert any(m.role == "Organizer" for m in members)


def test_user_can_login_with_username():
    client = app.test_client()
    with app.app_context():
        from models import User, db

        db.drop_all()
        db.create_all()
        user = User(username="tester", email="tester@example.com", full_name="Tester")
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()

    login_page = client.get("/login")
    csrf_match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', login_page.get_data(as_text=True))
    assert csrf_match, "expected CSRF token in login page"

    response = client.post(
        "/login",
        data={
            "email": "tester",
            "password": "secret123",
            "csrf_token": csrf_match.group(1),
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")


def test_deleting_last_trip_leaves_dashboard_empty():
    client = app.test_client()
    with app.app_context():
        from datetime import date
        from models import Trip, User, db

        db.drop_all()
        db.create_all()
        user = User(username="tester2", email="tester2@example.com", full_name="Tester Two")
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()

        trip = Trip(
            name="Only Trip",
            destination="Paris",
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 5),
            budget=1000.0,
            description="One trip only",
            status="Planning",
            trip_type="group",
            user_id=user.id,
        )
        db.session.add(trip)
        db.session.commit()

    login_page = client.get("/login")
    csrf_match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', login_page.get_data(as_text=True))
    assert csrf_match, "expected CSRF token in login page"

    login_response = client.post(
        "/login",
        data={
            "email": "tester2@example.com",
            "password": "secret123",
            "csrf_token": csrf_match.group(1),
        },
        follow_redirects=False,
    )
    assert login_response.status_code == 302

    dashboard_response = client.get("/dashboard")
    assert dashboard_response.status_code == 200
    assert b"Only Trip" in dashboard_response.data

    delete_response = client.post("/trips/1/delete", follow_redirects=False)
    assert delete_response.status_code == 302

    dashboard_after_delete = client.get("/dashboard")
    assert dashboard_after_delete.status_code == 200
    assert b"No trips yet. Create one to get started." in dashboard_after_delete.data
    assert b"Alpine Escape" not in dashboard_after_delete.data


def test_new_account_can_login_again_after_registration():
    client = app.test_client()
    with app.app_context():
        from models import User, db

        db.drop_all()
        db.create_all()

    register_page = client.get("/register")
    csrf_match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', register_page.get_data(as_text=True))
    assert csrf_match, "expected CSRF token in register page"

    register_response = client.post(
        "/register",
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "secret123",
            "confirm_password": "secret123",
            "csrf_token": csrf_match.group(1),
        },
        follow_redirects=False,
    )
    assert register_response.status_code == 302

    logout_response = client.get("/logout", follow_redirects=False)
    assert logout_response.status_code == 302

    login_page = client.get("/login")
    csrf_match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', login_page.get_data(as_text=True))
    assert csrf_match, "expected CSRF token in login page"

    login_response = client.post(
        "/login",
        data={
            "email": "newuser@example.com",
            "password": "secret123",
            "csrf_token": csrf_match.group(1),
        },
        follow_redirects=False,
    )
    assert login_response.status_code == 302
    assert login_response.headers["Location"].endswith("/dashboard")


def test_explorer_helpers_use_hotel_and_shopping_categories():
    from data.destinations import _normalize_place_record

    place = {
        "name": "A Luxury Stay",
        "category": "Hotels",
        "price": "₹2,500/night",
        "image_url": "https://example.com/hotel.jpg",
    }
    normalized = _normalize_place_record(place, "goa", 0)
    assert normalized["category"] == "Hotels"
    assert normalized["price"] == "₹2,500/night"

    shopping_place = {
        "name": "A Trendy Bazaar",
        "category": "Shopping",
        "price": "Free to browse",
        "image_url": "https://example.com/shop.jpg",
    }
    shopping_normalized = _normalize_place_record(shopping_place, "goa", 1)
    assert shopping_normalized["category"] == "Shopping"
    assert shopping_normalized["price"] == "Free to browse"


def test_login_accepts_same_username_after_registration_when_cases_differ():
    client = app.test_client()
    with app.app_context():
        from models import User, db

        db.drop_all()
        db.create_all()

    register_page = client.get("/register")
    csrf_match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', register_page.get_data(as_text=True))
    assert csrf_match, "expected CSRF token in register page"

    register_response = client.post(
        "/register",
        data={
            "username": "NewUser",
            "email": "newusercase@example.com",
            "full_name": "New User",
            "password": "secret123",
            "confirm_password": "secret123",
            "csrf_token": csrf_match.group(1),
        },
        follow_redirects=False,
    )
    assert register_response.status_code == 302

    logout_response = client.get("/logout", follow_redirects=False)
    assert logout_response.status_code == 302

    login_page = client.get("/login")
    csrf_match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', login_page.get_data(as_text=True))
    assert csrf_match, "expected CSRF token in login page"

    login_response = client.post(
        "/login",
        data={
            "email": "newuser",
            "password": "secret123",
            "csrf_token": csrf_match.group(1),
        },
        follow_redirects=False,
    )
    assert login_response.status_code == 302
    assert login_response.headers["Location"].endswith("/dashboard")
