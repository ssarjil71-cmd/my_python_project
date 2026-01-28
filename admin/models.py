from database.db import get_db_connection
import hashlib

class Admin:
    def __init__(self, id=None, name=None, username=None, password=None):
        self.id = id
        self.name = name
        self.username = username
        self.password = password

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def authenticate(username, password):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, username FROM admins WHERE username = %s AND password = SHA2(%s, 256)",
                (username, password)
            )
            admin_data = cursor.fetchone()
            conn.close()

            if admin_data:
                return Admin(
                    id=admin_data[0],
                    name=admin_data[1],
                    username=admin_data[2]
                )
            return None

        except Exception as e:
            print(f"Database error: {e}")
            return None

    @staticmethod
    def update_username(admin_id, new_username):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE admins SET username = %s WHERE id = %s", (new_username, admin_id))
        conn.commit()
        conn.close()

    @staticmethod
    def update_password(admin_id, new_password):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE admins SET password = SHA2(%s, 256) WHERE id = %s", (new_password, admin_id))
        conn.commit()
        conn.close()


class Manager:
    def __init__(self, id=None, name=None, email=None, username=None, password=None):
        self.id = id
        self.name = name
        self.email = email
        self.username = username
        self.password = password

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def authenticate(username, password):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, username FROM managers WHERE username = %s AND password = SHA2(%s, 256)",
            (username, password)
        )
        manager_data = cursor.fetchone()
        conn.close()

        if manager_data:
            return Manager(
                id=manager_data[0],
                name=manager_data[1],
                email=manager_data[2],
                username=manager_data[3]
            )
        return None

    # 🔹 UPDATED: creates manager AND assigns hotel
    @staticmethod
    def create_manager(name, email, username, password, hotel_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert manager
        cursor.execute(
            """
            INSERT INTO managers (name, email, username, password)
            VALUES (%s, %s, %s, SHA2(%s, 256))
            """,
            (name, email, username, password)
        )

        manager_id = cursor.lastrowid

        # Map manager to hotel
        cursor.execute(
            """
            INSERT INTO hotel_managers (hotel_id, manager_id)
            VALUES (%s, %s)
            """,
            (hotel_id, manager_id)
        )

        conn.commit()
        conn.close()

    # 🔹 UPDATED: fetch managers WITH hotel name
    @staticmethod
    def get_all_managers():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                m.id,
                m.name,
                m.email,
                m.username,
                h.hotel_name,
                m.created_at
            FROM managers m
            LEFT JOIN hotel_managers hm ON m.id = hm.manager_id
            LEFT JOIN hotels h ON hm.hotel_id = h.id
            ORDER BY m.created_at DESC
            """
        )

        managers = cursor.fetchall()
        conn.close()
        return managers

    @staticmethod
    def get_manager_by_id(manager_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, username FROM managers WHERE id = %s", (manager_id,))
        manager = cursor.fetchone()
        conn.close()
        return manager

    @staticmethod
    def update_manager(manager_id, name, email, username, password=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        if password:
            cursor.execute("UPDATE managers SET name = %s, email = %s, username = %s, password = SHA2(%s, 256) WHERE id = %s", (name, email, username, password, manager_id))
        else:
            cursor.execute("UPDATE managers SET name = %s, email = %s, username = %s WHERE id = %s", (name, email, username, manager_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_manager(manager_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM managers WHERE id = %s", (manager_id,))
        conn.commit()
        conn.close()
