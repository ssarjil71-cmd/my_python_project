from flask import render_template, request, jsonify, session, redirect, url_for, send_file
from . import orders_bp
from .services import OrderService
import os

try:
    order_service = OrderService()
except:
    order_service = None

# API ENDPOINTS FOR DASHBOARD
@orders_bp.route('/api/tables/<int:manager_id>', methods=['GET'])
def api_get_tables(manager_id):
    tables = []
    if order_service:
        tables = order_service.get_manager_tables(manager_id)
    return jsonify({'tables': tables})

@orders_bp.route('/api/orders/<int:manager_id>', methods=['GET'])
def api_get_orders(manager_id):
    orders = []
    if order_service:
        orders = order_service.get_manager_orders(manager_id)
    return jsonify({'orders': orders})

@orders_bp.route('/api/add-table', methods=['POST'])
def api_add_table():
    try:
        data = request.get_json()
        manager_id = data.get('manager_id')
        
        if not manager_id:
            return jsonify({'success': False, 'message': 'Manager ID required'})
        
        if not order_service:
            return jsonify({'success': False, 'message': 'Order service not available'})
        
        new_table = order_service.create_new_table(manager_id)
        if new_table:
            return jsonify({'success': True, 'table': new_table})
        else:
            return jsonify({'success': False, 'message': 'Failed to create table - database error'})
    
    except Exception as e:
        print(f"API add table error: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

# 1️⃣ MANAGE TABLES - GET (show page) + POST (add table)
@orders_bp.route('/manage-tables', methods=['GET', 'POST'])
def manage_tables():
    if 'manager_id' not in session:
        return redirect(url_for('hotel_manager.login'))
    
    manager_id = session['manager_id']
    
    if request.method == 'POST':
        # Handle Add Table form submission
        if order_service:
            new_table = order_service.create_new_table(manager_id)
        return redirect(url_for('orders.manage_tables'))
    
    # GET - Show manage tables page
    tables = []
    if order_service:
        tables = order_service.get_manager_tables(manager_id)
    return render_template('orders/manage_tables.html', tables=tables)

# 2️⃣ VIEW QR ORDERS - GET only (view page)
@orders_bp.route('/qr-orders', methods=['GET'])
def qr_orders():
    if 'manager_id' not in session:
        return redirect(url_for('hotel_manager.login'))
    
    manager_id = session['manager_id']
    orders = []
    if order_service:
        orders = order_service.get_manager_orders(manager_id)
    return render_template('orders/qr_orders.html', orders=orders)

# 3️⃣ GUEST ORDER SUBMIT - POST only
@orders_bp.route('/submit-order/<int:table_id>', methods=['POST'])
def submit_order(table_id):
    data = request.get_json()
    items = data.get('items', [])
    total_amount = data.get('total_amount', 0)
    
    if not items:
        return jsonify({'success': False, 'message': 'No items selected'})
    
    if order_service:
        order_id = order_service.place_order_by_table_id(table_id, items, total_amount)
        if order_id:
            return jsonify({'success': True, 'order_id': order_id})
    
    return jsonify({'success': False, 'message': 'Failed to place order'})

# Download QR Code - GET only
@orders_bp.route('/download_qr/<int:table_number>', methods=['GET'])
def download_qr(table_number):
    if 'manager_id' not in session:
        return redirect(url_for('hotel_manager.login'))
    
    qr_path = f"static/uploads/qr/table_{table_number}.png"
    if os.path.exists(qr_path):
        return send_file(qr_path, as_attachment=True, download_name=f"Table_{table_number}_QR.png")
    return "QR code not found", 404

# Guest Menu - GET only (from QR scan)
@orders_bp.route('/menu/<qr_code>', methods=['GET'])
def guest_menu(qr_code):
    table_info = None
    if order_service:
        table_info = order_service.get_table_by_qr(qr_code)
    
    if not table_info:
        return "Invalid QR code", 400
    
    return render_template('orders/guest_menu.html', 
                         qr_code=qr_code, 
                         table_number=table_info['table_number'],
                         table_id=table_info['id'])