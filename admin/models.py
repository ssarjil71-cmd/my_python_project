import mysql.connector
from mysql.connector import Error
import hashlib

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="mysql123",
        database="test",
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class Admin:
    @staticmethod
    def create_account(name, username, password):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return {'success': False, 'message': 'Username already exists!'}

            hashed = hash_password(password)
            cursor.execute(
                "INSERT INTO admins (name, username, password) VALUES (%s, %s, %s)",
                (name, username, hashed)
            )
            connection.commit()
            cursor.close()
            connection.close()
            return {'success': True, 'message': 'Admin account created successfully!'}
        except Error as exc:
            return {'success': False, 'message': f'Database error: {str(exc)}'}

    @staticmethod
    def login(username, password):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
            admin = cursor.fetchone()
            cursor.close()
            connection.close()

            if not admin:
                return {'success': False, 'message': 'Username not found!'}

            hashed = hash_password(password)
            if admin[3] != hashed:  # password column index
                return {'success': False, 'message': 'Incorrect password!'}

            return {'success': True, 'message': 'Login successful!', 'name': admin[1], 'id': admin[0]}
        except Error as exc:
            return {'success': False, 'message': f'Database error: {str(exc)}'}