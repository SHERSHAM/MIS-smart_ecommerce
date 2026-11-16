"""
VIVA - Route & Template Render Verification Test
Tests all HTTP endpoints:
- Homepage (/)
- Shop catalogue (/shop)
- Product details (/product/1)
- Category filter (/category/1)
- Search (/search?q=headphones)
- Deals (/deals)
- Registration (/register)
- Login (/login)
- Static informational pages (/about, /contact, /faq, /shipping-info, /returns, /privacy, /terms)
"""

import sys
sys.path.insert(0, 'd:/file/mis/smart_ecommerce')

from app import create_app

app = create_app('development')
client = app.test_client()

routes_to_test = [
    ('/', 200, 'Homepage'),
    ('/shop', 200, 'Product Catalogue'),
    ('/product/1', 200, 'Product Details'),
    ('/category/1', 302, 'Category Redirect to Shop'),
    ('/deals', 200, 'Deals Page'),
    ('/search?q=Noise', 302, 'Search Redirect to Shop'),
    ('/register', 200, 'Registration Page'),
    ('/login', 200, 'Login Page'),
    ('/forgot-password', 200, 'Forgot Password Page'),
    ('/about', 200, 'About Us'),
    ('/contact', 200, 'Contact Us'),
    ('/faq', 200, 'FAQ'),
    ('/shipping-info', 200, 'Shipping Info'),
    ('/returns', 200, 'Returns & Refunds'),
    ('/privacy', 200, 'Privacy Policy'),
    ('/terms', 200, 'Terms of Service'),
    ('/track-order', 200, 'Track Order')
]

print("==================================================")
print("     VIVA: HTTP ROUTE & TEMPLATE TESTING          ")
print("==================================================")

failures = 0
for route, expected_status, name in routes_to_test:
    res = client.get(route)
    if res.status_code == expected_status:
        print(f" [PASS] {name:<30} -> {route} ({res.status_code})")
    else:
        print(f" [FAIL] {name:<30} -> {route} (Expected {expected_status}, got {res.status_code})")
        failures += 1

print("==================================================")
if failures == 0:
    print(" ALL 17 HTTP ENDPOINTS RENDERED WITH STATUS 200/302!")
else:
    print(f" {failures} ROUTE(S) FAILED")
print("==================================================")
