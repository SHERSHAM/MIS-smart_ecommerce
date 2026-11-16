"""Admin model - database operations for administrators."""

from app import mysql
from werkzeug.security import check_password_hash, generate_password_hash


class Admin:
    @staticmethod
    def find_by_username_or_email(identifier):
        """Find admin by username or email."""
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM admins WHERE (username = %s OR email = %s) AND is_active = 1",
            (identifier, identifier)
        )
        admin = cur.fetchone()
        cur.close()
        return admin

    @staticmethod
    def find_by_id(admin_id):
        """Find admin by ID."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admins WHERE id = %s AND is_active = 1", (admin_id,))
        admin = cur.fetchone()
        cur.close()
        return admin

    @staticmethod
    def verify_password(stored_hash, password):
        """Verify password against secure hash."""
        return check_password_hash(stored_hash, password)

    @staticmethod
    def update_last_login(admin_id):
        """Update last login timestamp."""
        cur = mysql.connection.cursor()
        cur.execute("UPDATE admins SET last_login = CURRENT_TIMESTAMP WHERE id = %s", (admin_id,))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_all():
        """Get all administrators."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username, email, full_name, role, is_active, last_login, created_at FROM admins ORDER BY id ASC")
        admins = cur.fetchall()
        cur.close()
        return admins
