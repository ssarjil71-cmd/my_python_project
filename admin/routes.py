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
