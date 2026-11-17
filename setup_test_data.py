import os
import pymysql
import dotenv
from werkzeug.security import generate_password_hash

dotenv.load_dotenv('d:/file/mis/smart_ecommerce/.env')
conn = pymysql.connect(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    db=os.getenv('MYSQL_DB'),
    port=int(os.getenv('MYSQL_PORT')),
    cursorclass=pymysql.cursors.DictCursor
)

cur = conn.cursor()
cur.execute("SELECT id FROM customers WHERE email = %s", ('academic_tester@viva.com',))
row = cur.fetchone()
if not row:
    cur.execute(
        "INSERT INTO customers (full_name, email, phone, password_hash) VALUES (%s, %s, %s, %s)",
        ('Academic Tester', 'academic_tester@viva.com', '9876543210', generate_password_hash('VivaPass@2026'))
    )
    conn.commit()
    cust_id = cur.lastrowid
else:
    cust_id = row['id']
    cur.execute("UPDATE customers SET password_hash=%s WHERE id=%s", (generate_password_hash('VivaPass@2026'), cust_id))
    conn.commit()

print(f"Customer ID: {cust_id}")

# Ensure customer has a cart
cur.execute("SELECT id FROM cart WHERE customer_id = %s", (cust_id,))
cart_row = cur.fetchone()
if not cart_row:
    cur.execute("INSERT INTO cart (customer_id) VALUES (%s)", (cust_id,))
    conn.commit()
    cart_id = cur.lastrowid
else:
    cart_id = cart_row['id']

print(f"Cart ID: {cart_id}")

# Populate cart items
cur.execute("DELETE FROM cart_items WHERE cart_id = %s", (cart_id,))
cur.execute("INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (%s, 1, 1), (%s, 2, 2)", (cart_id, cart_id))

# Also ensure customer has an address for checkout
cur.execute("SELECT id FROM customer_addresses WHERE customer_id = %s", (cust_id,))
addr = cur.fetchone()
if not addr:
    cur.execute("""
        INSERT INTO customer_addresses (customer_id, recipient_name, phone, address_line1, city, state, pincode, is_default)
        VALUES (%s, 'Academic Tester', '9876543210', '42 Campus Tech Park, Innovation Way', 'Bengaluru', 'Karnataka', '560001', 1)
    """, (cust_id,))

# Ensure customer has an order for order tracking
cur.execute("SELECT id, order_number FROM orders WHERE customer_id = %s", (cust_id,))
ord_row = cur.fetchone()
if not ord_row:
    cur.execute("""
        INSERT INTO orders (order_number, customer_id, delivery_name, delivery_phone, delivery_email, delivery_address, delivery_city, delivery_state, delivery_pincode, subtotal, shipping_fee, discount, total, status)
        VALUES ('VIVA-20261117-ACAD01', %s, 'Academic Tester', '9876543210', 'academic_tester@viva.com', '42 Campus Tech Park', 'Bengaluru', 'Karnataka', '560001', 10497.00, 0.00, 500.00, 9997.00, 'Shipped')
    """, (cust_id,))
    order_id = cur.lastrowid
    cur.execute("INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (%s, 1, 1, 7999.00, 7999.00), (%s, 2, 1, 2498.00, 2498.00)", (order_id, order_id))

conn.commit()
print("Setup completed successfully!")
