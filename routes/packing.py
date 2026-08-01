from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required
from models import Trip, TripMember, PackingItem
from extensions import db

bp = Blueprint("packing", __name__)

@bp.route("/packing", endpoint="packing")
@login_required
def packing():
    trip_id = request.args.get("trip_id")
    trip = None
    if trip_id:
        trip = Trip.query.filter_by(id=int(trip_id), user_id=current_user.id).first()
    
    if not trip:
        trip = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.asc()).first()
    
    trips = Trip.query.filter_by(user_id=current_user.id).all()
    
    packing_items = []
    members = []
    if trip:
        packing_items = PackingItem.query.filter_by(trip_id=trip.id).all()
        if trip.trip_type == 'group':
            members = TripMember.query.filter_by(trip_id=trip.id).all()
    
    total_items = len(packing_items)
    packed_items = sum(1 for item in packing_items if item.is_packed)
    remaining_items = total_items - packed_items
    progress = int((packed_items / total_items * 100) if total_items > 0 else 0)

    # Group items by category for easy display
    categories = ["Clothes", "Toiletries", "Electronics", "Medicines & First Aid", "Travel Documents", "Personal Essentials", "Footwear", "Food", "Other"]
    items_by_category = {cat: [] for cat in categories}
    for item in packing_items:
        cat = item.category if item.category in categories else "Other"
        items_by_category[cat].append(item)

    return render_template(
        "packing.html",
        trip=trip,
        trips=trips,
        items=packing_items,
        items_by_category=items_by_category,
        categories=categories,
        members=members,
        total_items=total_items,
        packed_items=packed_items,
        remaining_items=remaining_items,
        progress=progress
    )

@bp.route("/packing/add", methods=["POST"])
@login_required
def add_item():
    trip_id = request.form.get("trip_id")
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first()
    if not trip:
        flash("Trip not found.", "danger")
        return redirect(url_for("packing.packing"))
    
    name = request.form.get("name")
    category = request.form.get("category")
    quantity = request.form.get("quantity", 1, type=int)
    is_essential = request.form.get("is_essential") == "on"
    priority = request.form.get("priority", "Medium")
    assigned_to = request.form.get("assigned_to")
    
    if assigned_to == "":
        assigned_to = None

    item = PackingItem(
        trip_id=trip.id,
        name=name,
        category=category,
        quantity=quantity,
        is_essential=is_essential,
        priority=priority,
        assigned_to=assigned_to
    )
    db.session.add(item)
    db.session.commit()
    
    flash("Item added to packing list.", "success")
    return redirect(url_for("packing.packing", trip_id=trip.id))

@bp.route("/packing/toggle/<int:item_id>", methods=["POST"])
@login_required
def toggle_item(item_id):
    item = PackingItem.query.get_or_404(item_id)
    if item.trip.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    item.is_packed = not item.is_packed
    db.session.commit()
    return jsonify({"success": True, "is_packed": item.is_packed})

@bp.route("/packing/delete/<int:item_id>", methods=["POST"])
@login_required
def delete_item(item_id):
    item = PackingItem.query.get_or_404(item_id)
    trip_id = item.trip_id
    if item.trip.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("packing.packing", trip_id=trip_id))
    
    db.session.delete(item)
    db.session.commit()
    flash("Item removed from packing list.", "success")
    return redirect(url_for("packing.packing", trip_id=trip_id))

@bp.route("/packing/edit/<int:item_id>", methods=["POST"])
@login_required
def edit_item(item_id):
    item = PackingItem.query.get_or_404(item_id)
    trip_id = item.trip_id
    if item.trip.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("packing.packing", trip_id=trip_id))
        
    item.name = request.form.get("name")
    item.category = request.form.get("category")
    item.quantity = request.form.get("quantity", 1, type=int)
    item.is_essential = request.form.get("is_essential") == "on"
    item.priority = request.form.get("priority", "Medium")
    assigned_to = request.form.get("assigned_to")
    item.assigned_to = assigned_to if assigned_to != "" else None
    
    db.session.commit()
    flash("Item updated.", "success")
    return redirect(url_for("packing.packing", trip_id=trip_id))

@bp.route("/packing/suggest", methods=["POST"])
@login_required
def suggest_items():
    trip_id = request.form.get("trip_id")
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first()
    if not trip:
        flash("Trip not found.", "danger")
        return redirect(url_for("packing.packing"))
        
    duration = (trip.end_date - trip.start_date).days + 1
    if duration <= 0:
        duration = 1
        
    clothes_qty = duration + 1
    socks_qty = duration + 2
    
    suggestions = [
        {"name": "Passport & ID", "category": "Travel Documents", "is_essential": True, "priority": "High"},
        {"name": "Travel Insurance Info", "category": "Travel Documents", "is_essential": True, "priority": "High"},
        {"name": "Phone & Charger", "category": "Electronics", "is_essential": True, "priority": "High"},
        {"name": "Power Bank", "category": "Electronics", "is_essential": False, "priority": "Medium"},
        {"name": "Earphones/Headphones", "category": "Electronics", "is_essential": False, "priority": "Medium"},
        {"name": "Toothbrush & Toothpaste", "category": "Toiletries", "is_essential": True, "priority": "High"},
        {"name": "Deodorant & Skincare", "category": "Toiletries", "is_essential": False, "priority": "Medium"},
        {"name": "Painkillers & Band-Aids", "category": "Medicines & First Aid", "is_essential": True, "priority": "Medium"},
        {"name": "T-Shirts / Tops", "category": "Clothes", "quantity": clothes_qty, "is_essential": True, "priority": "Medium"},
        {"name": "Underwear & Socks", "category": "Clothes", "quantity": socks_qty, "is_essential": True, "priority": "High"},
        {"name": "Pants / Shorts", "category": "Clothes", "quantity": max(1, duration // 2), "is_essential": True, "priority": "Medium"},
        {"name": "Comfortable Walking Shoes", "category": "Footwear", "quantity": 1, "is_essential": True, "priority": "High"},
        {"name": "Wallet / Cash / Cards", "category": "Personal Essentials", "is_essential": True, "priority": "High"},
        {"name": "Sunglasses & Sunscreen", "category": "Personal Essentials", "is_essential": False, "priority": "Medium"}
    ]
    
    # Add context specific items
    dest = (trip.destination or "").lower()
    if trip.trip_type == "group":
        suggestions.append({"name": "Shared Snacks", "category": "Food", "is_essential": False, "priority": "Low"})
        suggestions.append({"name": "Cards / Board Game", "category": "Personal Essentials", "is_essential": False, "priority": "Low"})
        
    if "beach" in dest or "sea" in dest or "ocean" in dest or "island" in dest:
        suggestions.append({"name": "Swimsuit & Towel", "category": "Clothes", "is_essential": True, "priority": "High"})
        
    if "winter" in dest or "snow" in dest or "ski" in dest or trip.start_date.month in [11, 12, 1, 2]:
        suggestions.append({"name": "Heavy Jacket & Gloves", "category": "Clothes", "is_essential": True, "priority": "High"})
    
    added_count = 0
    for s in suggestions:
        existing = PackingItem.query.filter_by(trip_id=trip.id, name=s["name"]).first()
        if not existing:
            item = PackingItem(
                trip_id=trip.id,
                name=s["name"],
                category=s["category"],
                quantity=s.get("quantity", 1),
                is_essential=s.get("is_essential", False),
                priority=s.get("priority", "Medium")
            )
            db.session.add(item)
            added_count += 1
            
    db.session.commit()
    flash(f"Added {added_count} suggested items to your packing list.", "success")
    return redirect(url_for("packing.packing", trip_id=trip.id))


