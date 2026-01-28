from flask import request, jsonify, render_template, redirect
from . import hotel_manager_bp
from .models import HotelManager, Waiter

@hotel_manager_bp.route("/hotel-manager/login-page")
def login_page():
    return render_template("manager_login.html")

@hotel_manager_bp.route("/hotel-manager/signup-page")
def signup_page():
    return render_template("manager_signup.html")

@hotel_manager_bp.route("/hotel-manager/login", methods=["POST"])
def login():
    data = request.json
    return jsonify(HotelManager.login(
        data.get("username"),
        data.get("password")
    ))

@hotel_manager_bp.route("/hotel-manager/dashboard")
def dashboard():
    manager_id = request.args.get("id")
    manager_name = request.args.get("name")

    if not manager_id:
        return redirect("/")

    waiters = Waiter.get_waiters_by_manager(manager_id)
    return render_template(
        "manager_dashboard.html",
        manager_id=manager_id,
        manager_name=manager_name,
        waiters=waiters,
        waiters_count=len(waiters) if waiters else 0
    )

@hotel_manager_bp.route("/hotel-manager/add-waiter", methods=["POST"])
def add_waiter():
    data = request.json
    return jsonify(Waiter.create_waiter(
        data["manager_id"],
        data["name"],
        data["email"],
        data["phone"]
    ))

@hotel_manager_bp.route("/hotel-manager/delete-waiter", methods=["POST"])
def delete_waiter():
    data = request.json
    return jsonify(Waiter.delete_waiter(
        data["waiter_id"],
        data["manager_id"]
    ))

@hotel_manager_bp.route("/hotel-manager/logout")
def logout():
    return redirect("/")
