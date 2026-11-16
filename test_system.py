"""
VIVA - Comprehensive System Verification Test
Tests all customer workflows:
- Categories and Products loading
- Customer Authentication
- Cart Management
- Wishlist Management
- Checkout & Order Placement
- Safe Stock Decrement & Transactional Integrity
- Order Retrieval and Tracking
"""

import sys
import os

from app import create_app, mysql
from models.customer import Customer
from models.category import Category
from models.product import Product
from models.cart import Cart
from models.wishlist import Wishlist
from models.order import Order
from models.address import Address

app = create_app('development')

with app.app_context():
    print("==================================================")
    print("  VIVA - LIVE BETTER: SYSTEM VERIFICATION TESTS   ")
    print("==================================================")

    # 1. Categories
    print("\n[1] Testing Database & Categories...")
    cats = Category.get_all()
    print(f"    Loaded {len(cats)} categories from MySQL.")
    assert len(cats) >= 7, f"Expected >= 7 categories, got {len(cats)}"
    for c in cats:
        print(f"    - [{c['id']}] {c['name']} (slug: {c['slug']})")

    # 2. Products
    print("\n[2] Testing Product Catalogue...")
    prods, total = Product.get_all(page=1, per_page=12)
    print(f"    Total active products: {total}")
    assert total >= 25, f"Expected >= 25 products, got {total}"
    first_product = prods[0]
    initial_stock = first_product['stock']
    print(f"    Sample product: '{first_product['name']}' (Price: Rs.{first_product['price']}, Stock: {initial_stock})")

    # 3. Customer Authentication
    print("\n[3] Testing Customer Registration & Login...")
    test_email = "academic_tester@viva.com"
    existing = Customer.find_by_email(test_email)
    if not existing:
        cust_id = Customer.create("Academic Tester", test_email, "9876543210", "VivaPass@2026")
        print(f"    New customer registered with ID: {cust_id}")
    else:
        cust_id = existing['id']
        print(f"    Existing test customer found with ID: {cust_id}")
    
    cust = Customer.find_by_email(test_email)
    assert cust is not None
    assert Customer.verify_password(cust['password_hash'], "VivaPass@2026")
    print("    Password hash verification: PASSED")

    # 4. Cart Operations
    print("\n[4] Testing Shopping Cart Operations...")
    Cart.clear(cust_id)
    Cart.add_item(cust_id, first_product['id'], 2)
    items = Cart.get_items(cust_id)
    assert len(items) == 1, "Expected 1 item in cart"
    assert items[0]['quantity'] == 2, "Expected quantity 2"
    subtotal = float(items[0]['item_total'])
    print(f"    Cart subtotal: Rs.{subtotal:.2f}")

    # 5. Wishlist
    print("\n[5] Testing Wishlist Operations...")
    Wishlist.add_item(cust_id, first_product['id'])
    assert Wishlist.is_in_wishlist(cust_id, first_product['id']), "Product should be in wishlist"
    print("    Wishlist add and verification: PASSED")

    # 6. Order Placement & Transaction
    print("\n[6] Testing Checkout & Order Placement...")
    addr_data = {
        'full_name': 'Academic Tester',
        'phone': '9876543210',
        'email': test_email,
        'address_line1': '42 Prestige Tech Park',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'pincode': '560103'
    }
    shipping = 0.0 if subtotal >= 999 else 49.0
    total_val = subtotal + shipping

    order_id, order_no = Order.create(
        customer_id=cust_id,
        address_data=addr_data,
        cart_items=items,
        subtotal=subtotal,
        shipping_fee=shipping,
        discount=0.0,
        total=total_val,
        payment_method='COD'
    )
    print(f"    Order generated successfully: {order_no} (ID: {order_id})")

    # Verify inventory was safely decremented
    updated_prod = Product.get_by_id(first_product['id'])
    expected_stock = initial_stock - 2
    assert updated_prod['stock'] == expected_stock, f"Expected stock {expected_stock}, got {updated_prod['stock']}"
    print(f"    Inventory stock decrement: {initial_stock} -> {updated_prod['stock']} (PASSED)")

    # 7. Order History & Tracking
    print("\n[7] Testing Order History & Real-Time Tracking...")
    customer_orders = Order.get_by_customer(cust_id)
    assert len(customer_orders) > 0, "Customer should have at least one order"
    
    tracked_order = Order.get_by_order_number(order_no, cust_id)
    assert tracked_order is not None
    assert tracked_order['status'] == 'Confirmed'
    print(f"    Tracked order status: '{tracked_order['status']}'")

    print("\n==================================================")
    print("  ALL TESTS COMPLETED & VERIFIED SUCCESSFULLY!   ")
    print("==================================================")
