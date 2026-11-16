"""Customer model - database operations for customers."""

from app import mysql
from werkzeug.security import generate_password_hash, check_password_hash


class Customer:
    @staticmethod
    def create(full_name, email, phone, password):
        """Create a new customer."""
        password_hash = generate_password_hash(password)
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO customers (full_name, email, phone, password_hash) VALUES (%s, %s, %s, %s)",
            (full_name, email, phone, password_hash)
        )
        mysql.connection.commit()
        customer_id = cur.lastrowid
        cur.close()
        return customer_id

    @staticmethod
    def find_by_email(email):
        """Find customer by email."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM customers WHERE email = %s", (email,))
        customer = cur.fetchone()
        cur.close()
        return customer

    @staticmethod
    def find_by_id(customer_id):
        """Find customer by ID."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
        customer = cur.fetchone()
        cur.close()
        return customer

    @staticmethod
    def verify_password(stored_hash, password):
        """Verify password against hash."""
        return check_password_hash(stored_hash, password)

    @staticmethod
    def update_profile(customer_id, full_name, phone):
        """Update customer profile."""
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE customers SET full_name = %s, phone = %s WHERE id = %s",
            (full_name, phone, customer_id)
        )
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def change_password(customer_id, new_password):
        """Change customer password."""
        password_hash = generate_password_hash(new_password)
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE customers SET password_hash = %s WHERE id = %s",
            (password_hash, customer_id)
        )
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def email_exists(email):
        """Check if email already exists."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM customers WHERE email = %s", (email,))
        result = cur.fetchone()
        cur.close()
        return result is not None
