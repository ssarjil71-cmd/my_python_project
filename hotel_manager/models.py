import mysql.connector
import hashlib

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Neha@123",
        database="test"
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class HotelManager:

    @staticmethod
    def create_account(name, email, username, password):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM managers WHERE username=%s OR email=%s",
            (username, email)
        )
        if cursor.fetchone():
            conn.close()
            return {"success": False, "message": "Username or email already exists"}

        cursor.execute(
            "INSERT INTO managers (name, email, username, password) VALUES (%s,%s,%s,%s)",
            (name, email, username, hash_password(password))
        )

        conn.commit()
        conn.close()
        return {"success": True, "message": "Account created successfully"}

    @staticmethod
    def login(username, password):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, name, password FROM managers WHERE username=%s",
            (username,)
        )
        manager = cursor.fetchone()
        conn.close()

        if not manager:
            return {"success": False, "message": "Username not found"}

        if manager[2] != hash_password(password):
            return {"success": False, "message": "Incorrect password"}

        return {
            "success": True,
            "message": "Login successful",
            "id": manager[0],
            "name": manager[1]
        }


class Waiter:

    @staticmethod
    def get_waiters_by_manager(manager_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, phone, created_at FROM waiters WHERE manager_id=%s",
            (manager_id,)
        )
        data = cursor.fetchall()
        conn.close()
        return data
