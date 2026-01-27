import mysql.connector
from datetime import datetime
import json
import os

class Database:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST", "localhost"),
                port=int(os.getenv("MYSQL_PORT", "3306")),
                user=os.getenv("MYSQL_USER", "root"),
                password=os.getenv("MYSQL_PASSWORD", "Dattu@1234"),
                database=os.getenv("MYSQL_DATABASE", "hotelease")
            )
            self.cursor = self.connection.cursor()
            self.create_tables()
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def create_tables(self):
        try:
            # Create tables table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS tables (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    manager_id INT NOT NULL,
                    table_number INT NOT NULL,
                    qr_code_no VARCHAR(20) NOT NULL,
                    qr_image_path VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create orders table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    table_id INT,
                    qr_code_no VARCHAR(20),
                    items TEXT,
                    total_amount DECIMAL(10,2),
                    status VARCHAR(20) DEFAULT 'New',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()
            print("Orders tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")

class TableModel:
    def __init__(self):
        self.db = Database()
    
    def add_table(self, manager_id):
        try:
            # Get next table number
            self.db.cursor.execute("SELECT MAX(table_number) FROM tables WHERE manager_id = %s", (manager_id,))
            result = self.db.cursor.fetchone()
            next_table_num = (result[0] or 0) + 1
            
            qr_code_no = f"QR-{next_table_num:03d}"
            qr_image_path = f"static/uploads/qr/table_{next_table_num}.png"
            
            self.db.cursor.execute("""
                INSERT INTO tables (manager_id, table_number, qr_code_no, qr_image_path)
                VALUES (%s, %s, %s, %s)
            """, (manager_id, next_table_num, qr_code_no, qr_image_path))
            
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Exception as e:
            print(f"Error adding table: {e}")
            return None
    
    def get_tables(self, manager_id):
        self.db.cursor.execute("""
            SELECT id, table_number, qr_code_no, qr_image_path, created_at
            FROM tables WHERE manager_id = %s ORDER BY table_number
        """, (manager_id,))
        return self.db.cursor.fetchall()
    
    def get_table_by_qr(self, qr_code_no):
        self.db.cursor.execute("""
            SELECT id, table_number, qr_code_no FROM tables WHERE qr_code_no = %s
        """, (qr_code_no,))
        return self.db.cursor.fetchone()

class OrderModel:
    def __init__(self):
        self.db = Database()
    
    def create_order_by_table_id(self, table_id, items, total_amount):
        items_json = json.dumps(items)
        # Get QR code for this table
        self.db.cursor.execute("SELECT qr_code_no FROM tables WHERE id = %s", (table_id,))
        result = self.db.cursor.fetchone()
        qr_code_no = result[0] if result else f"QR-{table_id:03d}"
        
        self.db.cursor.execute("""
            INSERT INTO orders (table_id, qr_code_no, items, total_amount, status)
            VALUES (%s, %s, %s, %s, 'New')
        """, (table_id, qr_code_no, items_json, total_amount))
        
        self.db.connection.commit()
        return self.db.cursor.lastrowid
    
    def get_orders(self, manager_id=None):
        if manager_id:
            self.db.cursor.execute("""
                SELECT o.id, t.table_number, o.qr_code_no, o.items, o.total_amount, 
                       o.status, o.created_at
                FROM orders o
                JOIN tables t ON o.table_id = t.id
                WHERE t.manager_id = %s
                ORDER BY o.created_at DESC
            """, (manager_id,))
        else:
            self.db.cursor.execute("""
                SELECT o.id, t.table_number, o.qr_code_no, o.items, o.total_amount, 
                       o.status, o.created_at
                FROM orders o
                JOIN tables t ON o.table_id = t.id
                ORDER BY o.created_at DESC
            """)
        return self.db.cursor.fetchall()
    
    def update_order_status(self, order_id, status):
        self.db.cursor.execute("""
            UPDATE orders SET status = %s WHERE id = %s
        """, (status, order_id))
        self.db.connection.commit()