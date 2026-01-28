import os
import mysql.connector
from flask import Flask, render_template, request, jsonify
from mysql.connector import Error
from hotel_manager import hotel_manager_bp
from admin import admin_bp
from guest_verification import guest_verification_bp
from menu import menu_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(hotel_manager_bp, url_prefix='/hotel-manager')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(guest_verification_bp, url_prefix='/guest-verification')
app.register_blueprint(menu_bp)

def get_db_connection():
    """Create a MySQL connection using environment variables."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "mysql123"),
        database=os.getenv("MYSQL_DATABASE", "test"),
    )

def init_db():
    """Initialize database tables"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Create managers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS managers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create waiters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS waiters (
                id INT AUTO_INCREMENT PRIMARY KEY,
                manager_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (manager_id) REFERENCES managers(id) ON DELETE CASCADE
            )
        """)

        # Create admins table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create default admin if not exists
        import hashlib
        cursor.execute("SELECT * FROM admins WHERE username = 'admin'")
        if not cursor.fetchone():
            default_password = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute(
                "INSERT INTO admins (name, username, password) VALUES (%s, %s, %s)",
                ('Administrator', 'admin', default_password)
            )
            print("Default admin created - Username: admin, Password: admin123")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # Initialize guest verification table
        from guest_verification.models import GuestVerification
        GuestVerification.create_table()
        
        print("Database initialized successfully")
    except Error as exc:
        print(f"Error initializing database: {exc}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/db-test")
def db_test():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        current_db = cursor.fetchone()
        cursor.close()
        connection.close()
        return jsonify({
            "status": "success",
            "database": current_db[0] if current_db else None,
        })
    except Error as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500

if __name__ == "__main__":
    app.run(debug=True)
