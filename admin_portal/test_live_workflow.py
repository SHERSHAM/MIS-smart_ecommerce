"""
Deep Live Workflow Verification:
Cross-system actions between Admin Portal & Customer Purchasing Website
"""

import requests

BASE_URL = "http://127.0.0.1:5000"

def run_workflow_tests():
    print("=" * 60)
    print("STARTING CROSS-PORTAL INTEGRATION WORKFLOW TESTS")
    print("=" * 60)

    admin_session = requests.Session()
    cust_session = requests.Session()

    # 1. Login as Admin
    login_resp = admin_session.post(f"{BASE_URL}/admin/login", data={
        "identifier": "admin",
        "password": "Admin@2026"
    })
    assert login_resp.status_code == 200, "Admin login failed"
    print("[PASS] 1. Admin authenticated")

    # 2. Add New Product in Admin Portal
    product_data = {
        "name": "Executive Bamboo Ergonomic Desk",
        "brand": "VIVA Workspace",
        "category_id": 3,  # Home & Living
        "price": 18999.0,
        "discount_price": 15999.0,
        "stock": 25,
        "sku": "VIVA-DSK-099",
        "short_description": "Eco-friendly solid bamboo standing desk with dual motors.",
        "description": "Premium motorized adjustable height standing desk crafted from sustainable bamboo.",
        "image_url": "https://images.unsplash.com/photo-1595515106969-1ce29566ff1c?auto=format&fit=crop&w=600&q=80",
        "is_active": "on"
    }
    add_resp = admin_session.post(f"{BASE_URL}/admin/products/add", data=product_data, allow_redirects=True)
    assert add_resp.status_code == 200, "Add product POST failed"
    assert "Executive Bamboo Ergonomic Desk" in add_resp.text, "New product not listed in Admin"
    print("[PASS] 2. Product successfully created in Admin Portal")

    # 3. Verify Product is immediately visible on Customer Shop Page
    shop_resp = cust_session.get(f"{BASE_URL}/shop?q=Bamboo")
    assert shop_resp.status_code == 200, "Customer shop query failed"
    assert "Executive Bamboo Ergonomic Desk" in shop_resp.text, "New product not visible in Customer Shop"
    print("[PASS] 3. Newly created product instantly visible in Customer Store (/shop)")

    # 4. Perform Manual Stock Adjustment in Admin Inventory
    # Find the newly created product ID
    # Get product list
    import pymysql
    conn = pymysql.connect(host='localhost', user='root', password='Shersha123', database='smart_ecommerce_db')
    cur = conn.cursor()
    cur.execute("SELECT id, stock FROM products WHERE sku = 'VIVA-DSK-099'")
    prod_row = cur.fetchone()
    assert prod_row is not None, "Product not found in DB"
    product_id, initial_stock = prod_row[0], prod_row[1]

    # Adjust stock: Add 15 units via RESTOCK
    adj_resp = admin_session.post(f"{BASE_URL}/admin/inventory/adjust", data={
        "product_id": product_id,
        "adjustment_type": "RESTOCK",
        "quantity": 15,
        "notes": "Warehouse container #A-42 received from manufacturer"
    }, allow_redirects=True)
    assert adj_resp.status_code == 200, "Stock adjustment POST failed"

    # Verify updated stock in DB (commit to refresh snapshot in Repeatable Read isolation)
    conn.commit()
    cur.execute("SELECT stock FROM products WHERE id = %s", (product_id,))
    updated_stock = cur.fetchone()[0]
    assert updated_stock == initial_stock + 15, f"Stock mismatch: expected {initial_stock + 15}, got {updated_stock}"
    print(f"[PASS] 4. Stock Adjusted from {initial_stock} to {updated_stock} with live inventory sync")

    # 5. Verify Transaction Audit Trail Entry in Admin Portal
    audit_resp = admin_session.get(f"{BASE_URL}/admin/inventory/transactions")
    assert audit_resp.status_code == 200, "Audit trail route failed"
    assert "Warehouse container #A-42" in audit_resp.text, "Audit log note missing from ledger"
    assert "Executive Bamboo Ergonomic Desk" in audit_resp.text, "Product name missing in ledger"
    print("[PASS] 5. Stock transaction audit trail ledger recorded and displayed successfully")

    # 6. Verify Order Status Update (Admin Order -> Customer Track Order)
    # Pick first pending order
    cur.execute("SELECT id, order_number FROM orders WHERE status = 'Pending' LIMIT 1")
    order_row = cur.fetchone()
    if order_row:
        order_id, order_num = order_row[0], order_row[1]
        update_resp = admin_session.post(f"{BASE_URL}/admin/orders/update-status/{order_id}", data={
            "status": "Shipped"
        }, allow_redirects=True)
        assert update_resp.status_code == 200, "Order status update failed"

        # Check in Customer tracking
        track_resp = cust_session.get(f"{BASE_URL}/track-order?order_number={order_num}")
        assert track_resp.status_code == 200, "Track order request failed"
        assert "Shipped" in track_resp.text, "Updated status not shown on customer track order"
        print(f"[PASS] 6. Order {order_num} updated to 'Shipped' by Admin; reflected on Customer Order Tracker")
    else:
        print("[SKIP] 6. No pending order found to update")

    # 7. Test All 8 Report CSV Exports
    reports = [
        'daily_sales', 'monthly_sales', 'product_performance',
        'customer_purchase', 'inventory_status', 'low_stock',
        'best_sellers', 'order_status'
    ]
    for rtype in reports:
        csv_resp = admin_session.get(f"{BASE_URL}/admin/reports/export-csv?type={rtype}")
        assert csv_resp.status_code == 200, f"CSV export failed for {rtype}: {csv_resp.status_code}"
        assert len(csv_resp.text) > 10, f"CSV export empty for {rtype}"
    print("[PASS] 7. All 8 Business Report CSV Exports generated valid downloadable data")

    # Clean up test product
    cur.execute("DELETE FROM inventory_transactions WHERE product_id = %s", (product_id,))
    cur.execute("DELETE FROM inventory WHERE product_id = %s", (product_id,))
    cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    cur.close()
    conn.close()
    print("[PASS] 8. Temporary test product cleaned up cleanly")

    print("\n" + "=" * 60)
    print("ALL CROSS-PORTAL INTEGRATION WORKFLOW TESTS PASSED!")
    print("=" * 60)

if __name__ == '__main__':
    run_workflow_tests()
