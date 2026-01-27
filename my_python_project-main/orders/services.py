from .models import TableModel, OrderModel
from .utils import generate_qr_code
import json

class OrderService:
    def __init__(self):
        try:
            self.table_model = TableModel()
            self.order_model = OrderModel()
        except Exception as e:
            print(f"OrderService initialization error: {e}")
            self.table_model = None
            self.order_model = None
    
    def create_new_table(self, manager_id):
        try:
            if not self.table_model:
                return None
                
            # Add table to database
            table_id = self.table_model.add_table(manager_id)
            
            if not table_id:
                return None
            
            # Get table details
            tables = self.table_model.get_tables(manager_id)
            new_table = next((t for t in tables if t[0] == table_id), None)
            
            if new_table:
                table_number = new_table[1]
                qr_code_no = new_table[2]
                
                # Generate QR code
                qr_path = generate_qr_code(table_number, qr_code_no)
                
                return {
                    'id': table_id,
                    'table_number': table_number,
                    'qr_code_no': qr_code_no,
                    'qr_image_path': qr_path
                }
            return None
        except Exception as e:
            print(f"Error creating table: {e}")
            return None
    
    def get_manager_tables(self, manager_id):
        tables = self.table_model.get_tables(manager_id)
        return [{
            'id': t[0],
            'table_number': t[1],
            'qr_code_no': t[2],
            'qr_image_path': t[3],
            'created_at': t[4]
        } for t in tables]
    
    def get_table_by_qr(self, qr_code_no):
        table_info = self.table_model.get_table_by_qr(qr_code_no)
        if table_info:
            return {
                'id': table_info[0],
                'table_number': table_info[1],
                'qr_code_no': table_info[2]
            }
        return None
    
    def place_order_by_table_id(self, table_id, items, total_amount):
        # Create order using table_id directly
        order_id = self.order_model.create_order_by_table_id(table_id, items, total_amount)
        return order_id
    
    def get_manager_orders(self, manager_id):
        orders = self.order_model.get_orders(manager_id)
        return [{
            'id': o[0],
            'table_number': o[1],
            'qr_code_no': o[2],
            'items': json.loads(o[3]) if o[3] else [],
            'total_amount': float(o[4]),
            'status': o[5],
            'created_at': o[6]
        } for o in orders]