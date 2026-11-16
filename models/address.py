"""Address model - database operations for customer addresses."""

from app import mysql


class Address:
    @staticmethod
    def get_by_customer(customer_id):
        """Get all addresses for a customer."""
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM customer_addresses WHERE customer_id = %s ORDER BY is_default DESC, created_at DESC",
            (customer_id,)
        )
        addresses = cur.fetchall()
        cur.close()
        return addresses

    @staticmethod
    def get_by_id(address_id, customer_id=None):
        """Get address by ID."""
        cur = mysql.connection.cursor()
        query = "SELECT * FROM customer_addresses WHERE id = %s"
        params = [address_id]
        if customer_id:
            query += " AND customer_id = %s"
            params.append(customer_id)
        cur.execute(query, params)
        address = cur.fetchone()
        cur.close()
        return address

    @staticmethod
    def create(customer_id, full_name, phone, address_line1, address_line2, city, state, pincode, is_default=False):
        """Create a new address."""
        cur = mysql.connection.cursor()
        if is_default:
            # Unset other default addresses
            cur.execute(
                "UPDATE customer_addresses SET is_default = 0 WHERE customer_id = %s",
                (customer_id,)
            )
        cur.execute("""
            INSERT INTO customer_addresses 
            (customer_id, full_name, phone, address_line1, address_line2, city, state, pincode, is_default)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (customer_id, full_name, phone, address_line1, address_line2, city, state, pincode, is_default))
        mysql.connection.commit()
        address_id = cur.lastrowid
        cur.close()
        return address_id

    @staticmethod
    def update(address_id, customer_id, full_name, phone, address_line1, address_line2, city, state, pincode, is_default=False):
        """Update an address."""
        cur = mysql.connection.cursor()
        if is_default:
            cur.execute(
                "UPDATE customer_addresses SET is_default = 0 WHERE customer_id = %s",
                (customer_id,)
            )
        cur.execute("""
            UPDATE customer_addresses 
            SET full_name=%s, phone=%s, address_line1=%s, address_line2=%s, 
                city=%s, state=%s, pincode=%s, is_default=%s
            WHERE id = %s AND customer_id = %s
        """, (full_name, phone, address_line1, address_line2, city, state, pincode, is_default, address_id, customer_id))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def delete(address_id, customer_id):
        """Delete an address."""
        cur = mysql.connection.cursor()
        cur.execute(
            "DELETE FROM customer_addresses WHERE id = %s AND customer_id = %s",
            (address_id, customer_id)
        )
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_default(customer_id):
        """Get default address for a customer."""
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM customer_addresses WHERE customer_id = %s AND is_default = 1",
            (customer_id,)
        )
        address = cur.fetchone()
        cur.close()
        return address
