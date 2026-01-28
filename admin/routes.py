
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from admin.models import Admin, Manager
from database.db import get_db_connection

admin_bp = Blueprint("admin", __name__)

# =========================
# AUTH
# =========================

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.authenticate(username, password)
        if admin:
            session["admin_id"] = admin.id
            session["admin_name"] = admin.name
            session["admin_username"] = admin.username
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid username or password", "error")

    return render_template("admin/admin_login.html")


@admin_bp.route("/dashboard")
def dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # TOTAL KYC VERIFICATIONS
    cursor.execute("SELECT COUNT(*) FROM kyc_verifications")
    total_kyc = cursor.fetchone()[0]

    # TODAY'S KYC VERIFICATIONS
    cursor.execute("""
        SELECT COUNT(*) FROM kyc_verifications
        WHERE DATE(created_at) = CURDATE()
    """)
    today_kyc = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin/admin_dashboard.html",
        total_kyc=total_kyc,
        today_kyc=today_kyc
    )



@admin_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))


# =========================
# HOTEL MANAGEMENT
# =========================

@admin_bp.route("/create-hotel", methods=["GET", "POST"])
def create_hotel():
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    if request.method == "POST":
        hotel_name = request.form.get("hotel_name")
        address = request.form.get("address")
        city = request.form.get("city")

        kyc_enabled = request.form.get("kyc") == "on"
        food_enabled = request.form.get("food") == "on"

        if not (kyc_enabled or food_enabled):
            flash("Please select at least one module", "error")
            return redirect(url_for("admin.create_hotel"))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert hotel
            cursor.execute(
                "INSERT INTO hotels (hotel_name, address, city) VALUES (%s, %s, %s)",
                (hotel_name, address, city)
            )
            hotel_id = cursor.lastrowid

            # Insert module permissions
            cursor.execute(
                """
                INSERT INTO hotel_modules (hotel_id, kyc_enabled, food_enabled)
                VALUES (%s, %s, %s)
                """,
                (hotel_id, kyc_enabled, food_enabled)
            )

            conn.commit()
            conn.close()

            flash("Hotel created successfully", "success")
            return redirect(url_for("admin.all_hotels"))

        except Exception as e:
            print(e)
            flash("Error creating hotel", "error")

    return render_template("admin/create_hotel.html")


@admin_bp.route("/all-hotels")
def all_hotels():
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            h.id, h.hotel_name, h.city,
            hm.kyc_enabled, hm.food_enabled
        FROM hotels h
        JOIN hotel_modules hm ON h.id = hm.hotel_id
        ORDER BY h.created_at DESC
    """)

    hotels = cursor.fetchall()
    conn.close()

    return render_template("admin/all_hotels.html", hotels=hotels)


@admin_bp.route("/edit-hotel/<int:hotel_id>", methods=["GET", "POST"])
def edit_hotel_modules(hotel_id):
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        kyc_enabled = request.form.get("kyc") == "on"
        food_enabled = request.form.get("food") == "on"

        if not (kyc_enabled or food_enabled):
            flash("At least one module must be enabled", "error")
            return redirect(url_for("admin.edit_hotel_modules", hotel_id=hotel_id))

        cursor.execute("""
            UPDATE hotel_modules
            SET kyc_enabled=%s, food_enabled=%s
            WHERE hotel_id=%s
        """, (kyc_enabled, food_enabled, hotel_id))

        conn.commit()
        conn.close()

        flash("Hotel modules updated", "success")
        return redirect(url_for("admin.all_hotels"))

    cursor.execute("""
        SELECT h.hotel_name, hm.kyc_enabled, hm.food_enabled
        FROM hotels h
        JOIN hotel_modules hm ON h.id = hm.hotel_id
        WHERE h.id=%s
    """, (hotel_id,))
    hotel = cursor.fetchone()

    conn.close()
    return render_template("admin/edit_hotel_modules.html", hotel=hotel, hotel_id=hotel_id)


# =========================
# MANAGER MANAGEMENT (STEP 5 FIXED)
# =========================

@admin_bp.route("/add-manager", methods=["GET", "POST"])
def add_manager():
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch hotels for dropdown
    cursor.execute("SELECT id, hotel_name FROM hotels")
    hotels = cursor.fetchall()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        hotel_id = request.form["hotel_id"]

        try:
            # Insert manager
            cursor.execute(
                """
                INSERT INTO managers (name, email, username, password)
                VALUES (%s, %s, %s, SHA2(%s,256))
                """,
                (name, email, username, password)
            )
            manager_id = cursor.lastrowid

            # Assign hotel
            cursor.execute(
                "INSERT INTO hotel_managers (hotel_id, manager_id) VALUES (%s, %s)",
                (hotel_id, manager_id)
            )

            conn.commit()
            flash("Manager added and assigned to hotel successfully!", "success")
            return redirect(url_for("admin.all_managers"))

        except Exception as e:
            conn.rollback()
            print(e)
            flash("Error adding manager", "error")

    conn.close()
    return render_template("admin/add_manager.html", hotels=hotels)


@admin_bp.route("/all-managers")
def all_managers():
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    managers = Manager.get_all_managers()
    return render_template("admin/all_managers.html", managers=managers)

@admin_bp.route("/edit-manager/<int:manager_id>", methods=["GET", "POST"])
def edit_manager(manager_id):
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))
    
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form.get("password")
        
        try:
            Manager.update_manager(manager_id, name, email, username, password if password else None)
            flash("Manager updated successfully!", "success")
            return redirect(url_for("admin.all_managers"))
        except Exception as e:
            flash("Error updating manager", "error")
    
    manager = Manager.get_manager_by_id(manager_id)
    return render_template("admin/edit_manager.html", manager=manager)

@admin_bp.route("/delete-manager/<int:manager_id>", methods=["POST"])
def delete_manager(manager_id):
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))
    
    try:
        Manager.delete_manager(manager_id)
        flash("Manager deleted successfully!", "success")
    except Exception as e:
        flash("Error deleting manager", "error")
    
    return redirect(url_for("admin.all_managers"))

@admin_bp.route("/change-username", methods=["GET", "POST"])
def change_username():
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))
    
    if request.method == "POST":
        new_username = request.form["username"]
        try:
            Admin.update_username(session["admin_id"], new_username)
            session["admin_username"] = new_username
            flash("Username updated successfully!", "success")
            return redirect(url_for("admin.dashboard"))
        except Exception as e:
            flash("Error updating username", "error")
    
    return render_template("admin/change_username.html")

@admin_bp.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))
    
    if request.method == "POST":
        new_password = request.form["password"]
        try:
            Admin.update_password(session["admin_id"], new_password)
            flash("Password updated successfully!", "success")
            return redirect(url_for("admin.dashboard"))
        except Exception as e:
            flash("Error updating password", "error")
    
    return render_template("admin/change_password.html")

from flask import request, jsonify, render_template
from . import admin_bp
from .models import Admin
from hotel_manager.models import HotelManager


@admin_bp.route('/login-page')
def login_page():
    return render_template('admin_login.html')


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    
    data = request.json
    result = Admin.login(data.get('username'), data.get('password'))
    return jsonify(result)


@admin_bp.route('/dashboard')
def dashboard():
    admin_id = request.args.get('id')
    admin_name = request.args.get('name')
    if not admin_id or not admin_name:
        return "Invalid access. Please login first.", 403

    # Get list of managers
    managers = HotelManager.get_all_managers()

    return render_template('admin_dashboard.html', admin_name=admin_name, managers=managers)


@admin_bp.route('/add-manager', methods=['POST'])
def add_manager():
    data = request.json
    result = HotelManager.create_account(
        data.get('name'), data.get('email'), data.get('username'), data.get('password')
    )
    return jsonify(result)


@admin_bp.route('/delete-manager', methods=['POST'])
def delete_manager():
    data = request.json
    result = HotelManager.delete_manager(data.get('manager_id'))
    return jsonify(result)

