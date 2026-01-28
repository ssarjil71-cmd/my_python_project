from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from admin.models import Manager

manager_bp = Blueprint("manager", __name__)

@manager_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        manager = Manager.authenticate(username, password)
        if manager:
            session["manager_id"] = manager.id
            session["manager_name"] = manager.name
            session["manager_username"] = manager.username
            session["manager_email"] = manager.email
            return redirect(url_for("manager.dashboard"))
        else:
            flash("Invalid username or password", "error")
    
    return render_template("manager/manager_login.html")

@manager_bp.route("/dashboard")
def dashboard():
    if "manager_id" not in session:
        return redirect(url_for("manager.login"))
    return render_template("manager/manager_dashboard.html")

@manager_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("manager.login"))