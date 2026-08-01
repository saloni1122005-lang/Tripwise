from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for, current_app
from flask_login import current_user, login_required
import requests
from extensions import db
from models import Activity, Trip, Expense, ExpenseSplit, Settlement, TripMember, Report, PackingItem
from data.destinations import get_nearby_attractions, get_nearby_hotels, get_nearby_shopping, get_supported_destinations, get_destination_info
from forms.trip_forms import TripForm
from werkzeug.utils import secure_filename

bp = Blueprint("explorer", __name__)


@bp.app_template_global("dest_gradient")
def dest_gradient(destination: str) -> str:
    """Return a vivid CSS gradient string keyed by the first letter of the destination."""
    _map = {
        'a': 'linear-gradient(135deg,#f97316,#eab308)',
        'b': 'linear-gradient(135deg,#ec4899,#8b5cf6)',
        'c': 'linear-gradient(135deg,#06b6d4,#3b82f6)',
        'd': 'linear-gradient(135deg,#374151,#6366f1)',
        'e': 'linear-gradient(135deg,#059669,#0ea5e9)',
        'f': 'linear-gradient(135deg,#f59e0b,#ef4444)',
        'g': 'linear-gradient(135deg,#06b6d4,#0891b2)',
        'h': 'linear-gradient(135deg,#84cc16,#16a34a)',
        'i': 'linear-gradient(135deg,#6366f1,#8b5cf6)',
        'j': 'linear-gradient(135deg,#f59e0b,#dc2626)',
        'k': 'linear-gradient(135deg,#16a34a,#065f46)',
        'l': 'linear-gradient(135deg,#7c3aed,#ec4899)',
        'm': 'linear-gradient(135deg,#3b82f6,#6366f1)',
        'n': 'linear-gradient(135deg,#f97316,#ec4899)',
        'o': 'linear-gradient(135deg,#0ea5e9,#6366f1)',
        'p': 'linear-gradient(135deg,#10b981,#0ea5e9)',
        'q': 'linear-gradient(135deg,#8b5cf6,#06b6d4)',
        'r': 'linear-gradient(135deg,#0891b2,#0e7490)',
        's': 'linear-gradient(135deg,#10b981,#059669)',
        't': 'linear-gradient(135deg,#a855f7,#6366f1)',
        'u': 'linear-gradient(135deg,#8b5cf6,#ec4899)',
        'v': 'linear-gradient(135deg,#d97706,#92400e)',
        'w': 'linear-gradient(135deg,#0ea5e9,#3b82f6)',
        'x': 'linear-gradient(135deg,#6366f1,#8b5cf6)',
        'y': 'linear-gradient(135deg,#eab308,#f97316)',
        'z': 'linear-gradient(135deg,#06b6d4,#10b981)',
    }
    if not destination:
        return 'linear-gradient(135deg,#059669,#0EA5E9)'
    return _map.get(destination[0].lower(), 'linear-gradient(135deg,#059669,#0EA5E9)')


@bp.app_template_global("dest_image")
def dest_image(destination: str) -> str:
    """Return a destination-specific image fallback."""
    if not destination:
        return 'https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=1400&auto=format&fit=crop'

    images = {
        'manali': 'https://images.unsplash.com/photo-1605649487212-4d4ce7c6883e?w=1400&auto=format&fit=crop',
        'udaipur': 'https://images.unsplash.com/photo-1615966650071-855b15fba392?w=1400&auto=format&fit=crop',
        'goa': 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=1400&auto=format&fit=crop',
        'jaipur': 'https://images.unsplash.com/photo-1477587458883-47145ed94245?w=1400&auto=format&fit=crop',
        'paris': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1400&auto=format&fit=crop',
        'london': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=1400&auto=format&fit=crop',
    }

    found = images.get(destination.strip().lower())
    if found:
        return found

    from urllib.parse import quote
    return f"https://loremflickr.com/1200/800/{quote(destination.strip())},city,landscape/all"


# ── Unified Hub ────────────────────────────────────────────────────────────────

@bp.route("/explore", methods=["GET", "POST"], endpoint="hub")
@login_required
def hub():
    form = TripForm()
    show_modal = False

    if request.method == "POST":
        if form.validate_on_submit():
            trip = Trip(
                name=form.name.data,
                destination=form.destination.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                budget=form.budget.data or 0.0,
                description=form.description.data,
                status=form.status.data,
                trip_type=form.trip_type.data,
                user_id=current_user.id,
            )
            if form.cover_image.data and hasattr(form.cover_image.data, "filename") and form.cover_image.data.filename:
                filename = secure_filename(form.cover_image.data.filename)
                form.cover_image.data.save(f"static/images/{filename}")
                trip.cover_image = f"/static/images/{filename}"
            db.session.add(trip)
            db.session.commit()
            # Always add the trip organizer as a member for group trips.
            if trip.trip_type == 'group':
                from models import TripMember
                organizer_name = current_user.full_name or current_user.username
                organizer_member = TripMember(
                    trip_id=trip.id,
                    user_id=current_user.id,
                    display_name=organizer_name,
                    role='Organizer',
                )
                db.session.add(organizer_member)

            # process any modal member inputs (member_name_0, member_name_1, ...)
            members = []
            for key, val in request.form.items():
                if key.startswith('member_name_') and val.strip():
                    members.append(val.strip())
            # create TripMember rows for submitted member names
            from models import TripMember
            for name in members:
                tm = TripMember(trip_id=trip.id, user_id=current_user.id, display_name=name, role='Member')
                db.session.add(tm)
            db.session.commit()
            flash(f"🎉 Trip '{trip.name}' created! Start exploring.", "success")
            return redirect(url_for("explorer.hub"))
        else:
            show_modal = True
            for errors in form.errors.values():
                for err in errors:
                    flash(err, "danger")

    trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.desc()).all()
    dest = request.args.get("dest", "").strip()
    dest_info = get_destination_info(dest) if dest else {}
    supported = get_supported_destinations()

    return render_template(
        "explorer.html",
        form=form,
        trips=trips,
        dest=dest,
        dest_info=dest_info,
        supported=supported,
        show_modal=show_modal,
    )


@bp.route("/explore/api/attractions")
@login_required
def api_attractions():
    dest = request.args.get("dest", "").strip()
    category_filter = request.args.get("category", "").strip()
    query = request.args.get("query", "").strip()

    if not dest:
        return jsonify([])

    places = get_nearby_attractions(dest)

    if query:
        query = query.lower()
        places = [
            place for place in places
            if query in place.get("name", "").lower() or query in place.get("description", "").lower()
        ]

    if category_filter and category_filter.lower() != "all":
        places = [
            place for place in places
            if place.get("category", "").lower() == category_filter.lower()
        ]

    return jsonify(places)




# ── Explore Destination (3-tab: Attractions / Hotels / Restaurants) ────────────

def get_google_places(destination: str, query: str, tab: str) -> list:
    """Fetch places from Google Text Search API."""
    import os
    from dotenv import load_dotenv
    load_dotenv()  # Reloads .env in case the key was added without restarting the server

    api_key = os.getenv("GOOGLE_PLACES_API_KEY") or current_app.config.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("DEBUG: GOOGLE_PLACES_API_KEY is missing!")
        return []

    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{query} in {destination}",
        "key": api_key
    }

    places = []
    try:
        resp = requests.get(search_url, params=params, timeout=8)
        data = resp.json()
        status = data.get("status")
        if status != "OK":
            if status != "ZERO_RESULTS":
                print(f"Google Places API returned {status} for {destination}: {data.get('error_message')}")
            return []

        for idx, result in enumerate(data.get("results", [])[:12]):
            photo_ref = ""
            if result.get("photos"):
                photo_ref = result["photos"][0].get("photo_reference", "")

            image_url = (
                f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={photo_ref}&key={api_key}"
                if photo_ref else ""
            )

            category_label = "Tourist Attraction"
            if tab == "hotels":
                category_label = "Hotel"
            elif tab == "shopping":
                category_label = "Shopping"
            elif result.get("types"):
                category_label = " ".join(result.get("types")[:2]).title()

            places.append({
                "id": result.get("place_id", f"google_{idx}"),
                "place_id": str(result.get("place_id", f"google_{idx}")),
                "name": result.get("name"),
                "description": result.get("formatted_address", ""),
                "best_time": "Year-round",
                "duration": "Variable",
                "category": category_label,
                "rating": result.get("rating", 4.0),
                "address": result.get("formatted_address", ""),
                "opening_status": "Open Now" if result.get("opening_hours", {}).get("open_now") else "",
                "image_url": image_url,
                "distance": "",
                "maps_url": f"https://www.google.com/maps/place/?q=place_id:{result.get('place_id')}",
            })
    except Exception as e:
        print(f"Google Places Text Search API Error for {destination}: {e}")

    return places


def get_osm_places(destination: str, tab: str) -> list:
    """Fetch real places from OpenStreetMap (Overpass API) as a free fallback."""
    import requests
    from urllib.parse import quote
    
    tags = {
        "attractions": 'node["tourism"~"attraction|museum"]["name"](area.searchArea); way["tourism"~"attraction|museum"]["name"](area.searchArea); node["historic"]["name"](area.searchArea); way["historic"]["name"](area.searchArea);',
        "hotels": 'node["tourism"="hotel"]["name"](area.searchArea); way["tourism"="hotel"]["name"](area.searchArea);',
        "shopping": 'node["shop"~"mall|department_store"]["name"](area.searchArea); way["shop"~"mall|department_store"]["name"](area.searchArea);'
    }
    
    tag_query = tags.get(tab, tags["attractions"])
    
    overpass_query = f"""
    [out:json][timeout:10];
    area["name"="{destination.title()}"]->.searchArea;
    (
      {tag_query}
    );
    out center 12;
    """
    
    url = "https://overpass-api.de/api/interpreter"
    places = []
    try:
        resp = requests.post(url, data={"data": overpass_query}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for idx, element in enumerate(data.get("elements", [])[:12]):
                tags_data = element.get("tags", {})
                name = tags_data.get("name")
                if not name:
                    continue
                
                street = tags_data.get("addr:street", "")
                city = tags_data.get("addr:city", "")
                address = f"{street}, {city}".strip(", ") if street else destination.title()
                
                places.append({
                    "id": f"osm_{element.get('id', idx)}",
                    "name": name,
                    "description": tags_data.get("description") or f"A notable {tab[:-1] if tab.endswith('s') else tab} in {destination.title()}.",
                    "best_time": "Year-round",
                    "duration": "Variable",
                    "category": tab.title(),
                    "rating": 4.0 + (idx % 10) * 0.1,
                    "address": address,
                    "opening_status": "Open",
                    "image_url": f"https://loremflickr.com/1200/800/{quote(name)},landscape/all",
                    "maps_url": f"https://www.google.com/maps/search/?api=1&query={quote(name + ' ' + destination)}",
                    "place_id": str(element.get('id', idx))
                })
    except Exception as e:
        print(f"OSM Overpass API Error for {destination}: {e}")
    
    return places


@bp.route("/explore/api/explore-destination", endpoint="api_explore_destination")
@login_required
def api_explore_destination():
    dest = request.args.get("dest", "").strip()
    tab  = request.args.get("tab", "attractions").strip().lower()
    if not dest:
        return jsonify([])

    # Use Google Places API for accurate data if key is available
    import os
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GOOGLE_PLACES_API_KEY") or current_app.config.get("GOOGLE_PLACES_API_KEY")
    if api_key:
        query_map = {
            "attractions": "Tourist attractions",
            "hotels": "Hotels",
            "shopping": "Shopping malls"
        }
        query = query_map.get(tab, "Tourist attractions")
        places = get_google_places(dest, query, tab)
        if places:
            # Fallback for empty images to generic loremflickr
            from urllib.parse import quote
            for p in places:
                if not p.get("image_url"):
                    p["image_url"] = f"https://loremflickr.com/1200/800/{quote(p['name'])},landscape/all"
            return jsonify(places)

    # 1st Fallback: Free OpenStreetMap API (Overpass) for real places
    places = get_osm_places(dest, tab)
    if places:
        return jsonify(places)

    # 2nd Fallback to local hardcoded data if all APIs fail
    if tab == "hotels":
        places = get_nearby_hotels(dest)
    elif tab == "shopping":
        places = get_nearby_shopping(dest)
    else:
        places = get_nearby_attractions(dest)

    # Fill in empty images
    from urllib.parse import quote
    for p in places:
        if not p.get("image_url"):
            p["image_url"] = f"https://loremflickr.com/1200/800/{quote(p['name'])},landscape/all"

    return jsonify(places)


# ── Delete Trip from Hub ───────────────────────────────────────────────────────

@bp.route("/explore/<int:trip_id>/delete", methods=["POST"], endpoint="delete_trip_hub")
@login_required
def delete_trip_hub(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    expenses = Expense.query.filter_by(trip_id=trip.id).all()
    for exp in expenses:
        db.session.query(ExpenseSplit).filter_by(expense_id=exp.id).delete()
    db.session.query(Expense).filter_by(trip_id=trip.id).delete()
    db.session.query(Settlement).filter_by(trip_id=trip.id).delete()
    db.session.query(PackingItem).filter_by(trip_id=trip.id).delete()
    db.session.query(TripMember).filter_by(trip_id=trip.id).delete()
    db.session.query(Activity).filter_by(trip_id=trip.id).delete()
    db.session.query(Report).filter_by(trip_id=trip.id).delete()
    db.session.delete(trip)
    db.session.commit()
    flash("Trip deleted.", "success")
    return redirect(url_for("explorer.hub"))


@bp.route("/explore/favorite", methods=["POST"], endpoint="toggle_favorite")
@login_required
def toggle_favorite():
    place_id = request.form.get("place_id", "").strip()
    if not place_id:
        return jsonify({"success": False, "message": "Place id is required."}), 400

    favorites = session.get("favorite_places", [])
    if place_id in favorites:
        favorites = [item for item in favorites if item != place_id]
    else:
        favorites.append(place_id)
    session["favorite_places"] = favorites
    session.modified = True
    return jsonify({"success": True, "message": "Favorite updated.", "favorited": place_id in session["favorite_places"]})


@bp.route("/explore/group-trip", endpoint="group_trip")
@login_required
def group_trip():
    return redirect(url_for("explorer.hub"))


# ── Add Place to Itinerary (Hub — trip picker) ────────────────────────────────

@bp.route("/explore/add", methods=["POST"], endpoint="add_place_hub")
@login_required
def add_place_hub():
    trip_id = request.form.get("trip_id", "")
    if not trip_id:
        return jsonify({"success": False, "message": "Select a trip first."}), 400
    trip = Trip.query.filter_by(id=int(trip_id), user_id=current_user.id).first()
    if not trip:
        return jsonify({"success": False, "message": "Trip not found."}), 404

    place_name = request.form.get("place_name", "").strip()
    place_desc = request.form.get("place_desc", "").strip()
    best_time  = request.form.get("best_time", "").strip()
    duration   = request.form.get("duration", "").strip()
    category   = request.form.get("category", "").strip()

    if not place_name:
        return jsonify({"success": False, "message": "Place name required."}), 400

    if Activity.query.filter_by(trip_id=trip.id, title=place_name).first():
        return jsonify({"success": False, "message": f"'{place_name}' already in '{trip.name}'!", "duplicate": True})

    from sqlalchemy import func
    max_day = db.session.query(func.max(Activity.day)).filter_by(trip_id=trip.id).scalar()
    day = (max_day or 0) + 1
    
    combined_desc = f"{place_desc} | Best Time: {best_time} | Duration: {duration} | Category: {category}"
    if len(combined_desc) > 250:
        combined_desc = combined_desc[:247] + "..."
        
    db.session.add(Activity(
        trip_id=trip.id, day=day, time="10:00 AM", title=place_name,
        description=combined_desc,
    ))
    db.session.commit()
    return jsonify({"success": True, "message": f"✅ '{place_name}' added to Day {day} of '{trip.name}'!"})


# ── Legacy routes (backward compat — redirect to hub) ─────────────────────────

@bp.route("/explorer/<int:trip_id>", endpoint="explorer")
@login_required
def explorer(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    return redirect(url_for("explorer.hub", dest=trip.destination))


@bp.route("/explorer/<int:trip_id>/add", methods=["POST"], endpoint="add_place")
@login_required
def add_place(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first()
    if not trip:
        return jsonify({"success": False, "message": "Trip not found."}), 404
    place_name = request.form.get("place_name", "").strip()
    place_desc = request.form.get("place_desc", "").strip()
    best_time  = request.form.get("best_time", "").strip()
    duration   = request.form.get("duration", "").strip()
    category   = request.form.get("category", "").strip()
    if not place_name:
        return jsonify({"success": False, "message": "Place name required."}), 400
    if Activity.query.filter_by(trip_id=trip_id, title=place_name).first():
        return jsonify({"success": False, "message": f"'{place_name}' already in itinerary!", "duplicate": True})
    from sqlalchemy import func
    max_day = db.session.query(func.max(Activity.day)).filter_by(trip_id=trip_id).scalar()
    day = (max_day or 0) + 1
    db.session.add(Activity(
        trip_id=trip_id, day=day, time="10:00 AM", title=place_name,
        description=f"{place_desc} | Best Time: {best_time} | Duration: {duration} | Category: {category}",
    ))
    db.session.commit()
    return jsonify({"success": True, "message": f"✅ '{place_name}' added to Day {day}!"})
