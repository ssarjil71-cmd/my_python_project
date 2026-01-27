import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_orders_db():
    """Initialize orders database tables"""
    try:
        from orders.models import Database
        
        print("Initializing orders database...")
        db = Database()
        print("Orders database initialized successfully")
        
        # Test table creation
        db.cursor.execute("SHOW TABLES LIKE 'tables'")
        if db.cursor.fetchone():
            print("Tables table exists")
        else:
            print("Tables table missing")
            
        db.cursor.execute("SHOW TABLES LIKE 'orders'")
        if db.cursor.fetchone():
            print("Orders table exists")
        else:
            print("Orders table missing")
            
        db.connection.close()
        
    except Exception as e:
        print(f"Database initialization failed: {e}")

if __name__ == "__main__":
    init_orders_db()