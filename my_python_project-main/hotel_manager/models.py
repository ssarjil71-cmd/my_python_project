import mysql.connector
from mysql.connector import Error
import hashlib

def get_db_connection():
    """Create a MySQL connection"""
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Dattu@1234",
        database="hotelease",
    )

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

class HotelManager:
    @staticmethod
    def create_account(name, email, username, password):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Check if username or email already exists
            cursor.execute("SELECT * FROM managers WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return {'success': False, 'message': 'Username or email already exists!'}
            
            # Insert new manager
            hashed_password = hash_password(password)
            cursor.execute(
                "INSERT INTO managers (name, email, username, password) VALUES (%s, %s, %s, %s)",
                (name, email, username, hashed_password)
            )
            connection.commit()
            cursor.close()
            connection.close()
            
            return {'success': True, 'message': 'Account created successfully!'}
        except Error as exc:
            return {'success': False, 'message': f'Database error: {str(exc)}'}
    
    @staticmethod
    def login(username, password):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Find manager by username
            cursor.execute("SELECT * FROM managers WHERE username = %s", (username,))
            manager = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if not manager:
                return {'success': False, 'message': 'Username not found!'}
            
            # Check password
            hashed_password = hash_password(password)
            if manager[4] != hashed_password:  # manager[4] is the password column
                return {'success': False, 'message': 'Incorrect password!'}
            
            return {'success': True, 'message': 'Login successful!', 'name': manager[1], 'id': manager[0]}
        except Error as exc:
            return {'success': False, 'message': f'Database error: {str(exc)}'}
    
    @staticmethod
    def get_all_managers():
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, email, username, created_at FROM managers")
            managers = cursor.fetchall()
            cursor.close()
            connection.close()
            return managers
        except Error as exc:
            return None

    @staticmethod
    def delete_manager(manager_id):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Verify manager exists
            cursor.execute("SELECT * FROM managers WHERE id = %s", (manager_id,))
            if not cursor.fetchone():
                cursor.close()
                connection.close()
                return {'success': False, 'message': 'Manager not found!'}

            # Delete manager (waiters will cascade)
            cursor.execute("DELETE FROM managers WHERE id = %s", (manager_id,))
            connection.commit()
            cursor.close()
            connection.close()

            return {'success': True, 'message': 'Manager deleted successfully!'}
        except Error as exc:
            return {'success': False, 'message': f'Database error: {str(exc)}'}

class Waiter:
    @staticmethod
    def create_waiter(manager_id, name, email, phone):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT * FROM waiters WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return {'success': False, 'message': 'Email already exists!'}
            
            # Insert new waiter
            cursor.execute(
                "INSERT INTO waiters (manager_id, name, email, phone) VALUES (%s, %s, %s, %s)",
                (manager_id, name, email, phone)
            )
            connection.commit()
            cursor.close()
            connection.close()
            
            return {'success': True, 'message': 'Waiter created successfully!'}
        except Error as exc:
            return {'success': False, 'message': f'Database error: {str(exc)}'}
    
    @staticmethod
    def get_waiters_by_manager(manager_id):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, email, phone, created_at FROM waiters WHERE manager_id = %s", (manager_id,))
            waiters = cursor.fetchall()
            cursor.close()
            connection.close()
            return waiters
        except Error as exc:
            return None
    
    @staticmethod
    def delete_waiter(waiter_id, manager_id):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Verify waiter belongs to this manager
            cursor.execute("SELECT * FROM waiters WHERE id = %s AND manager_id = %s", (waiter_id, manager_id))
            if not cursor.fetchone():
                cursor.close()
                connection.close()
                return {'success': False, 'message': 'Waiter not found!'}
            
            cursor.execute("DELETE FROM waiters WHERE id = %s", (waiter_id,))
            connection.commit()
            cursor.close()
            connection.close()
            
            return {'success': True, 'message': 'Waiter deleted successfully!'}
        except Error as exc:
            return {'success': False, 'message': f'Database error: {str(exc)}'}