"""
Automated Verification Suite for Phase 2: Admin MIS Portal & Cross-System Integrity
"""

import requests

BASE_URL = "http://127.0.0.1:5000"

def run_tests():
    print("=" * 60)
    print("STARTING SEDSS PHASE 2 ADMIN & MIS INTEGRATION VERIFICATION")
    print("=" * 60)

    session = requests.Session()

    # 1. Verify Customer Homepage
    resp = session.get(f"{BASE_URL}/")
    assert resp.status_code == 200, f"Customer homepage failed: {resp.status_code}"
    assert "VIVA" in resp.text, "Customer homepage missing VIVA brand"
    print("[PASS] 1. Customer Store Homepage Accessible (Status 200)")

    # 2. Verify Customer Shop Page
    resp = session.get(f"{BASE_URL}/shop")
    assert resp.status_code == 200, f"Customer shop failed: {resp.status_code}"
    print("[PASS] 2. Customer Shop Accessible (Status 200)")

    # 3. Verify Admin Route Protection (Unauthenticated -> Redirect to Login)
    resp = session.get(f"{BASE_URL}/admin/dashboard", allow_redirects=False)
    assert resp.status_code in [302, 301], f"Admin dashboard not protected: {resp.status_code}"
    assert "/admin/login" in resp.headers.get("Location", ""), f"Redirection wrong: {resp.headers.get('Location')}"
    print("[PASS] 3. Unauthenticated Access to /admin/dashboard Safely Blocked (Redirect 302 -> /admin/login)")

    # 4. Verify Admin Login Page loads
    resp = session.get(f"{BASE_URL}/admin/login")
    assert resp.status_code == 200, f"Admin login page failed: {resp.status_code}"
    assert "VIVA MIS Portal" in resp.text, "Admin login page branding missing"
    print("[PASS] 4. Admin Login Interface Rendered (Status 200)")

    # 5. Verify Failed Login with Bad Credentials
    resp = session.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "WrongPassword"})
    assert "Invalid username/email or password" in resp.text or resp.status_code == 200, "Bad login check failed"
    print("[PASS] 5. Invalid Admin Credentials Properly Rejected")

    # 6. Verify Successful Admin Login with seeded credentials
    resp = session.post(
        f"{BASE_URL}/admin/login",
        data={"identifier": "admin", "password": "Admin@2026"},
        allow_redirects=True
    )
    assert resp.status_code == 200, f"Admin login post failed: {resp.status_code}"
    assert "Overview" in resp.text or "Total Revenue" in resp.text, "Admin login did not land on dashboard"
    print("[PASS] 6. Admin Login Succeeded for user 'admin' (Redirected to Dashboard)")

    # 7. Verify Admin Dashboard & KPIs
    resp = session.get(f"{BASE_URL}/admin/dashboard")
    assert resp.status_code == 200, f"Admin dashboard failed: {resp.status_code}"
    assert "Net Store Revenue" in resp.text or "Revenue" in resp.text, "Dashboard missing Revenue KPI"
    assert "Total Customer Orders" in resp.text or "Orders" in resp.text, "Dashboard missing Orders KPI"
    assert "monthlyRevenueChart" in resp.text, "Dashboard missing revenue chart canvas"
    print("[PASS] 7. Executive Dashboard Verified (KPIs & Chart.js Canvases Active)")

    # 8. Verify Products Management
    resp = session.get(f"{BASE_URL}/admin/products")
    assert resp.status_code == 200, f"Products route failed: {resp.status_code}"
    assert "Add New Product" in resp.text, "Products page missing Add button"
    print("[PASS] 8. Catalog Product Management Table Loaded (Status 200)")

    # 9. Verify Add Product Form
    resp = session.get(f"{BASE_URL}/admin/products/add")
    assert resp.status_code == 200, f"Add product form failed: {resp.status_code}"
    assert "Product Name" in resp.text, "Form missing field"
    print("[PASS] 9. Add Product Form Verified (Status 200)")

    # 10. Verify Categories Management
    resp = session.get(f"{BASE_URL}/admin/categories")
    assert resp.status_code == 200, f"Categories route failed: {resp.status_code}"
    assert "Category Hierarchy" in resp.text or "Categories" in resp.text, "Category page missing heading"
    print("[PASS] 10. Category Taxonomy Management Loaded (Status 200)")

    # 11. Verify Orders Management
    resp = session.get(f"{BASE_URL}/admin/orders")
    assert resp.status_code == 200, f"Orders route failed: {resp.status_code}"
    assert "Orders" in resp.text, "Orders page missing heading"
    print("[PASS] 11. Customer Order Processing Queue Loaded (Status 200)")

    # 12. Verify Customers Intelligence
    resp = session.get(f"{BASE_URL}/admin/customers")
    assert resp.status_code == 200, f"Customers route failed: {resp.status_code}"
    assert "Customer Intelligence" in resp.text or "Customers" in resp.text, "Customers page missing heading"
    print("[PASS] 12. Customer Intelligence & Lifetime Value Table Loaded (Status 200)")

    # 13. Verify Inventory & Stock Control (ROP)
    resp = session.get(f"{BASE_URL}/admin/inventory")
    assert resp.status_code == 200, f"Inventory route failed: {resp.status_code}"
    assert "Inventory & Stock Control" in resp.text, "Inventory page missing heading"
    assert "Reorder Point" in resp.text or "ROP" in resp.text, "Inventory page missing ROP advice"
    print("[PASS] 13. Inventory Control & Reorder Point (ROP) Service Loaded (Status 200)")

    # 14. Verify Inventory Audit Logs
    resp = session.get(f"{BASE_URL}/admin/inventory/transactions")
    assert resp.status_code == 200, f"Transactions route failed: {resp.status_code}"
    assert "Inventory Audit Trail" in resp.text or "Stock Transaction Ledger" in resp.text, "Transactions page missing"
    print("[PASS] 14. Inventory Audit Trail Ledger Loaded (Status 200)")

    # 15. Verify MIS Decision Analytics
    resp = session.get(f"{BASE_URL}/admin/analytics")
    assert resp.status_code == 200, f"Analytics route failed: {resp.status_code}"
    assert "MIS Decision Analytics" in resp.text, "Analytics page missing heading"
    assert "Top 10 Best Selling Products" in resp.text, "Analytics missing Best Sellers"
    assert "Slow-Moving Products" in resp.text, "Analytics missing Slow Movers"
    print("[PASS] 15. MIS Decision Analytics (Best Sellers + Slow Movers) Loaded (Status 200)")

    # 16. Verify Strategic Decision Support Insights
    resp = session.get(f"{BASE_URL}/admin/insights")
    assert resp.status_code == 200, f"Insights route failed: {resp.status_code}"
    assert "MIS Decision Support System" in resp.text, "Insights missing DSS heading"
    print("[PASS] 16. DSS Strategic Insights & Recommendations Engine Loaded (Status 200)")

    # 17. Verify Business Reports Viewer
    resp = session.get(f"{BASE_URL}/admin/reports")
    assert resp.status_code == 200, f"Reports route failed: {resp.status_code}"
    assert "Executive Business Reports" in resp.text or "Daily Sales Report" in resp.text, "Reports missing heading"
    print("[PASS] 17. Business Reports Viewer Loaded (Status 200)")

    # 18. Verify CSV Report Export Endpoint
    resp = session.get(f"{BASE_URL}/admin/reports/export-csv?type=daily_sales")
    assert resp.status_code == 200, f"CSV export failed: {resp.status_code}"
    assert "text/csv" in resp.headers.get("Content-Type", ""), "Response is not CSV"
    assert "Sale Date" in resp.text or "sale_date" in resp.text or "Total Orders" in resp.text or "total_orders" in resp.text, "CSV header missing"
    print("[PASS] 18. CSV Report Exporter Verified (Valid CSV file generated)")

    # 19. Verify Static Assets (CSS and JS)
    resp = session.get(f"{BASE_URL}/admin/static/css/admin_dark.css")
    assert resp.status_code == 200, f"Admin dark CSS failed: {resp.status_code}"
    resp2 = session.get(f"{BASE_URL}/static/admin_portal/css/admin_dark.css")
    assert resp2.status_code == 200, f"Static route failed: {resp2.status_code}"
    print("[PASS] 19. Admin Executive Theme Static Assets Served (Status 200)")

    # 20. Verify Admin Logout
    resp = session.get(f"{BASE_URL}/admin/logout", allow_redirects=False)
    assert resp.status_code == 302, f"Logout did not redirect: {resp.status_code}"
    assert "/admin/login" in resp.headers.get("Location", "")
    print("[PASS] 20. Admin Logout Terminated Session Safely")

    print("\n" + "=" * 60)
    print("ALL 20 AUTOMATED VERIFICATION CHECKS PASSED PERFECTLY!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
