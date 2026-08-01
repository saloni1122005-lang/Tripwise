from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from extensions import db
from forms.trip_forms import ExpenseForm
from models import Expense, ExpenseSplit, Settlement, Trip, TripMember, User
from collections import defaultdict
import datetime

bp = Blueprint("expenses", __name__)


def calculate_balances(trip_id):
    expenses = Expense.query.filter_by(trip_id=trip_id).all()
    settlements = Settlement.query.filter_by(trip_id=trip_id, status="Completed").all()
    
    balances = defaultdict(float) # + means they are owed, - means they owe
    paid = defaultdict(float)
    share = defaultdict(float)
    
    trip_members = TripMember.query.filter_by(trip_id=trip_id).all()
    name_to_id = {}
    for m in trip_members:
        name = m.user.full_name or m.user.username
        name_to_id[name] = m.id

    for exp in expenses:
        try:
            paid_by_id = int(exp.paid_by)
        except ValueError:
            # Fallback for old legacy expenses stored as names
            paid_by_id = name_to_id.get(exp.paid_by)
            
        if not paid_by_id:
            continue
            
        paid[paid_by_id] += exp.amount
        balances[paid_by_id] += exp.amount
        
        splits = ExpenseSplit.query.filter_by(expense_id=exp.id).all()
        for split in splits:
            share[split.member_id] += split.share_amount
            balances[split.member_id] -= split.share_amount
            
    for s in settlements:
        # Payer reduces their negative balance (they owe less)
        balances[s.payer_id] += s.amount
        # Receiver reduces their positive balance (they are owed less)
        balances[s.receiver_id] -= s.amount
        
    # Simplify debts
    debtors = []
    creditors = []
    for member_id, balance in balances.items():
        # Update db record
        member = TripMember.query.get(member_id)
        if member:
            member.amount_paid = paid[member_id]
            member.balance = balance
            db.session.add(member)
        
        if balance < -0.01:
            debtors.append([member_id, -balance])
        elif balance > 0.01:
            creditors.append([member_id, balance])
            
    db.session.commit()
    
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)
    
    transactions = []
    i = 0
    j = 0
    while i < len(debtors) and j < len(creditors):
        debt_amount = debtors[i][1]
        credit_amount = creditors[j][1]
        
        min_amount = min(debt_amount, credit_amount)
        
        transactions.append({
            "payer_id": debtors[i][0],
            "receiver_id": creditors[j][0],
            "amount": min_amount
        })
        
        debtors[i][1] -= min_amount
        creditors[j][1] -= min_amount
        
        if debtors[i][1] < 0.01:
            i += 1
        if creditors[j][1] < 0.01:
            j += 1
            
    return transactions, paid, share, balances


@bp.route("/expenses", methods=["GET", "POST"], endpoint="expenses")
@login_required
def expenses():
    trip_id = request.args.get("trip_id") or request.form.get("trip_id")
    trip = None
    if trip_id:
        trip = Trip.query.filter_by(id=int(trip_id), user_id=current_user.id).first()
    if not trip:
        trip = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.asc()).first()
        
    form = ExpenseForm()
    
    expenses = []
    transactions = []
    total_expense = 0
    remaining_budget = 0
    my_paid = 0
    my_owe = 0
    my_owed = 0
    pending_settlements = 0
    members_map = {}
    my_member_id = None
    trip_members = []
    is_solo = trip.trip_type == 'solo' if trip else False
    
    if trip:
        trip_members = TripMember.query.filter_by(trip_id=trip.id).all()
        member_choices = []
        for m in trip_members:
            name = m.user.full_name or m.user.username
            member_choices.append((m.id, name))
            members_map[m.id] = name
            if m.user_id == current_user.id:
                my_member_id = m.id
                
        if not is_solo:
            form.paid_by.choices = member_choices
            form.split_between.choices = member_choices
            
            if request.method == "GET":
                form.paid_by.data = my_member_id
                form.split_between.data = [m.id for m in trip_members]
        else:
            # Solo: set dummy choices so validation passes
            form.paid_by.choices = member_choices if member_choices else [(0, 'You')]
            form.split_between.choices = member_choices if member_choices else [(0, 'You')]
            if request.method == "GET":
                form.paid_by.data = my_member_id
                form.split_between.data = [my_member_id] if my_member_id else []
            
        expenses = Expense.query.filter_by(trip_id=trip.id).order_by(Expense.date.desc()).all()
        total_expense = sum(exp.amount for exp in expenses)
        remaining_budget = trip.budget - total_expense
        
        if not is_solo:
            transactions, paid, share, balances = calculate_balances(trip.id)
            
            if my_member_id:
                my_paid = paid[my_member_id]
                bal = balances[my_member_id]
                if bal < 0:
                    my_owe = -bal
                else:
                    my_owed = bal
            
            pending_settlements = sum(t["amount"] for t in transactions)

    # Handle form submission
    is_form_valid = False
    if is_solo and trip:
        # For solo trips, skip paid_by/split_between validation
        if request.method == 'POST' and form.title.data and form.amount.data and form.date.data:
            is_form_valid = True
    elif form.validate_on_submit() and trip:
        is_form_valid = True
        
    if is_form_valid:
        paid_by_val = str(my_member_id) if is_solo else str(form.paid_by.data)
        split_val = str(my_member_id) if is_solo else ','.join(map(str, form.split_between.data))
        expense = Expense(
            trip_id=trip.id,
            title=form.title.data,
            category=form.category.data,
            amount=form.amount.data,
            paid_by=paid_by_val,
            split_between=split_val,
            date=form.date.data,
            notes=form.notes.data,
        )
        new_total = total_expense + float(form.amount.data)

        if new_total > trip.budget:
            exceeded = new_total - trip.budget
            flash(
                f"⚠ Warning! You are exceeding the trip budget by ₹{exceeded:.2f}.",
                "warning"
            )   
        db.session.add(expense)
        db.session.flush()
        
        if not is_solo:
            split_type = form.split_type.data
            selected_members = form.split_between.data
            
            if selected_members:
                if split_type == "equal":
                    share_amt = expense.amount / len(selected_members)
                    for m_id in selected_members:
                        db.session.add(ExpenseSplit(expense_id=expense.id, member_id=m_id, share_amount=share_amt))
                elif split_type == "percentage":
                    for m_id in selected_members:
                        pct = float(request.form.get(f"split_pct_{m_id}", 0))
                        share_amt = expense.amount * (pct / 100.0)
                        db.session.add(ExpenseSplit(expense_id=expense.id, member_id=m_id, share_amount=share_amt, split_percentage=pct))
                elif split_type == "custom":
                    for m_id in selected_members:
                        amt = float(request.form.get(f"split_amt_{m_id}", 0))
                        db.session.add(ExpenseSplit(expense_id=expense.id, member_id=m_id, share_amount=amt))
                    
        db.session.commit()
        if not is_solo:
            calculate_balances(trip.id)
        flash("Expense added.", "success")
        return redirect(url_for("expenses.expenses", trip_id=trip.id))
        
    return render_template(
        "expenses.html", 
        form=form, 
        trip=trip, 
        trip_members=trip_members,
        expenses=expenses, 
        total_expense=total_expense, 
        remaining_budget=remaining_budget, 
        my_paid=my_paid,
        my_owe=my_owe,
        my_owed=my_owed,
        pending_settlements=pending_settlements,
        transactions=transactions,
        members_map=members_map,
        trips=Trip.query.filter_by(user_id=current_user.id).all()
    )


@bp.route("/expenses/<int:expense_id>/edit", methods=["GET", "POST"], endpoint="edit_expense")
@login_required
def edit_expense(expense_id):
    expense = Expense.query.join(Trip).filter(Expense.id == expense_id, Trip.user_id == current_user.id).first_or_404()
    form = ExpenseForm(obj=expense)
    
    trip_members = TripMember.query.filter_by(trip_id=expense.trip_id).all()
    member_choices = [(m.id, m.user.full_name or m.user.username) for m in trip_members]
    form.paid_by.choices = member_choices
    form.split_between.choices = member_choices

    if form.validate_on_submit():
        expense.title = form.title.data
        expense.category = form.category.data
        expense.amount = form.amount.data
        expense.paid_by = str(form.paid_by.data)
        expense.split_between = ','.join(map(str, form.split_between.data))
        expense.date = form.date.data
        expense.notes = form.notes.data
        db.session.query(ExpenseSplit).filter_by(expense_id=expense.id).delete()
        
        split_type = form.split_type.data
        selected_members = form.split_between.data
        if selected_members:
            if split_type == "equal":
                share_amt = expense.amount / len(selected_members)
                for m_id in selected_members:
                    db.session.add(ExpenseSplit(expense_id=expense.id, member_id=m_id, share_amount=share_amt))
            elif split_type == "percentage":
                for m_id in selected_members:
                    pct = float(request.form.get(f"split_pct_{m_id}", 0))
                    share_amt = expense.amount * (pct / 100.0)
                    db.session.add(ExpenseSplit(expense_id=expense.id, member_id=m_id, share_amount=share_amt, split_percentage=pct))
            elif split_type == "custom":
                for m_id in selected_members:
                    amt = float(request.form.get(f"split_amt_{m_id}", 0))
                    db.session.add(ExpenseSplit(expense_id=expense.id, member_id=m_id, share_amount=amt))
        db.session.commit()
        calculate_balances(expense.trip_id)
        flash("Expense updated.", "success")
        return redirect(url_for("expenses.expenses", trip_id=expense.trip_id))
        
    if request.method == "GET":
        try:
            form.paid_by.data = int(expense.paid_by)
        except ValueError:
            pass
        form.split_between.data = [int(x) for x in expense.split_between.split(',')] if expense.split_between else []
        form.split_type.data = "equal"
        
    return render_template("edit_expense.html", form=form, expense=expense, trip_members=trip_members)


@bp.route("/expenses/<int:expense_id>/delete", methods=["POST"], endpoint="delete_expense")
@login_required
def delete_expense(expense_id):
    expense = Expense.query.join(Trip).filter(Expense.id == expense_id, Trip.user_id == current_user.id).first_or_404()
    trip_id = expense.trip_id
    db.session.delete(expense)
    db.session.commit()
    calculate_balances(trip_id)
    flash("Expense deleted.", "success")
    return redirect(url_for("expenses.expenses", trip_id=trip_id))


@bp.route("/settle", methods=["POST"], endpoint="settle")
@login_required
def settle():
    trip_id = request.form.get("trip_id")
    payer_id = request.form.get("payer_id")
    receiver_id = request.form.get("receiver_id")
    amount = float(request.form.get("amount", 0))
    
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    
    settlement = Settlement(
        trip_id=trip.id,
        payer_id=payer_id,
        receiver_id=receiver_id,
        amount=amount,
        status="Completed"
    )
    db.session.add(settlement)
    db.session.commit()
    
    calculate_balances(trip.id)
    flash("Settlement recorded.", "success")
    return redirect(url_for("expenses.expenses", trip_id=trip.id))
