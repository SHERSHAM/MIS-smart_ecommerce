import os
import sys
import time
from pathlib import Path
from PIL import Image
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_DIR = Path('d:/file/mis/smart_ecommerce')
OUTPUT_DIR = BASE_DIR / 'report_screenshots'
BOARDS_DIR = OUTPUT_DIR / 'boards'

os.makedirs(OUTPUT_DIR, exist_ok=True)
print("=== VIVA SEDSS Automated Screenshot Suite for Final Year Report ===")

# 1. Obtain Customer and Admin Authenticated Session Cookies via requests
print("\n[1/3] Generating authenticated sessions...")
s_cust = requests.Session()
r_cust = s_cust.post("http://127.0.0.1:5000/login", data={
    "email": "academic_tester@viva.com",
    "password": "VivaPass@2026"
})
cust_cookie = s_cust.cookies.get("session")
print(f"Customer session acquired: {cust_cookie[:20]}...")

s_admin = requests.Session()
r_admin = s_admin.post("http://127.0.0.1:5000/admin/login", data={
    "identifier": "admin",
    "password": "Admin@2026"
})
admin_cookie = s_admin.cookies.get("session")
print(f"Admin session acquired: {admin_cookie[:20]}...")

# 2. Configure Headless Chrome
opts = Options()
opts.add_argument('--headless')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-gpu')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--window-size=1920,1080')
opts.add_argument('--force-device-scale-factor=1')

driver = webdriver.Chrome(options=opts)
driver.set_window_size(1920, 1080)

captured = []

def take_shot(filename, sleep_time=2.0):
    target = OUTPUT_DIR / filename
    time.sleep(sleep_time)
    driver.save_screenshot(str(target))
    size_kb = target.stat().st_size / 1024
    print(f"Saved: {filename:<38} ({size_kb:6.1f} KB) | '{driver.title}'")
    captured.append((filename, str(target), size_kb, driver.title))

try:
    # =========================================================================
    # AGILE SPRINT BOARDS (4 screenshots)
    # =========================================================================
    print("\n[2/3] Capturing Agile Project & Sprint Boards...")
    
    # Fig 1.1: Full backlog board (all 12 stories)
    driver.get(f"file:///{BOARDS_DIR / 'board_full_backlog.html'}".replace("\\", "/"))
    take_shot("Fig_1.1_Full_Backlog_Board.png", sleep_time=1.0)

    # Fig 2.1: Sprint 1 stories (1, 2, 3, 4)
    driver.get(f"file:///{BOARDS_DIR / 'board_sprint_1.html'}".replace("\\", "/"))
    take_shot("Fig_2.1_Sprint_1_Board.png", sleep_time=1.0)

    # Fig 2.6: Sprint 2 stories (5, 7, 8, 9)
    driver.get(f"file:///{BOARDS_DIR / 'board_sprint_2.html'}".replace("\\", "/"))
    take_shot("Fig_2.6_Sprint_2_Board.png", sleep_time=1.0)

    # Fig 2.11: Sprint 3 stories (6, 10, 11, 12)
    driver.get(f"file:///{BOARDS_DIR / 'board_sprint_3.html'}".replace("\\", "/"))
    take_shot("Fig_2.11_Sprint_3_Board.png", sleep_time=1.0)

    # =========================================================================
    # CUSTOMER STOREFRONT (Fig 2.2, Fig 2.3)
    # =========================================================================
    print("\n[3/3] Capturing Customer Storefront Views...")
    driver.get("http://127.0.0.1:5000/")
    driver.delete_all_cookies()
    driver.add_cookie({'name': 'session', 'value': cust_cookie, 'path': '/'})

    # Fig 2.2: Shop page (/shop) with filter sidebar and product grid visible
    driver.get("http://127.0.0.1:5000/shop")
    take_shot("Fig_2.2_Shop_Page.png", sleep_time=2.0)

    # Fig 2.3: Checkout page (/checkout)
    driver.get("http://127.0.0.1:5000/checkout")
    take_shot("Fig_2.3_Checkout_Page.png", sleep_time=2.0)

    # Fig 2.3 Options: Cart page and Order Tracking page
    driver.get("http://127.0.0.1:5000/cart")
    take_shot("Fig_2.3_Cart_Page.png", sleep_time=2.0)

    driver.get("http://127.0.0.1:5000/track-order?order_number=VIVA-20261117-ACAD01")
    take_shot("Fig_2.3_Order_Tracking_Page.png", sleep_time=2.0)

    # Generate high quality side-by-side composite of Cart + Track Order
    try:
        cart_img = Image.open(OUTPUT_DIR / "Fig_2.3_Cart_Page.png")
        track_img = Image.open(OUTPUT_DIR / "Fig_2.3_Order_Tracking_Page.png")
        w, h = 960, 1080
        c_crop = cart_img.resize((w, h), Image.Resampling.LANCZOS)
        t_crop = track_img.resize((w, h), Image.Resampling.LANCZOS)
        comp = Image.new('RGB', (1920, 1080), (11, 17, 24))
        comp.paste(c_crop, (0, 0))
        comp.paste(t_crop, (960, 0))
        comp_target = OUTPUT_DIR / "Fig_2.3_Cart_and_Tracking_Composite.png"
        comp.save(comp_target, quality=95)
        sz = comp_target.stat().st_size / 1024
        print(f"Saved: {'Fig_2.3_Cart_and_Tracking_Composite.png':<38} ({sz:6.1f} KB) | 'Cart & Order Tracking Side-by-Side'")
        captured.append(("Fig_2.3_Cart_and_Tracking_Composite.png", str(comp_target), sz, "Cart & Order Tracking Side-by-Side Composite"))
    except Exception as ce:
        print("Composite error:", ce)

    # =========================================================================
    # ADMIN PORTAL & MIS DSS (Fig 2.7, Fig 2.8, Fig 3.1, Fig 3.3, Fig 3.4, Fig 3.5, Fig 3.6)
    # =========================================================================
    print("\nCapturing Admin Portal & MIS Decision Support Views...")
    driver.delete_all_cookies()
    driver.add_cookie({'name': 'session', 'value': admin_cookie, 'path': '/'})

    # Fig 2.7: Products list (/admin/products)
    driver.get("http://127.0.0.1:5000/admin/products")
    take_shot("Fig_2.7_Products_List.png", sleep_time=2.0)

    # Fig 2.8: Orders queue (/admin/orders)
    driver.get("http://127.0.0.1:5000/admin/orders")
    take_shot("Fig_2.8_Orders_Queue.png", sleep_time=2.0)

    # Order details with status stepper (/admin/orders/1)
    driver.get("http://127.0.0.1:5000/admin/orders/1")
    take_shot("Fig_2.8_Order_Detail_Stepper.png", sleep_time=2.0)

    # Fig 3.1: Dashboard (/admin/dashboard) with KPI cards, revenue line chart, category donut
    driver.get("http://127.0.0.1:5000/admin/dashboard")
    take_shot("Fig_3.1_Dashboard.png", sleep_time=3.0)

    # Fig 3.3: Analytics page (/admin/analytics) with top sellers and slow movers
    driver.get("http://127.0.0.1:5000/admin/analytics")
    take_shot("Fig_3.3_Analytics.png", sleep_time=3.0)

    # Fig 3.4: Insights page (/admin/insights) with the four advisory cards
    driver.get("http://127.0.0.1:5000/admin/insights")
    take_shot("Fig_3.4_Insights.png", sleep_time=2.5)

    # Fig 3.5: Inventory page (/admin/inventory) showing the ROP restock table
    driver.get("http://127.0.0.1:5000/admin/inventory")
    take_shot("Fig_3.5_Inventory.png", sleep_time=2.0)

    # Fig 3.6: Reports page (/admin/reports) with a report on screen and the CSV export button
    driver.get("http://127.0.0.1:5000/admin/reports?type=daily_sales")
    take_shot("Fig_3.6_Reports.png", sleep_time=2.0)

finally:
    driver.quit()
    print("\nWebDriver closed.")

print(f"\n========================================================")
print(f"COMPLETE: {len(captured)} screenshot files generated in {OUTPUT_DIR}")
print(f"========================================================")
for name, pth, sz, title in captured:
    print(f"  • {name:<38} | {sz:6.1f} KB | {title}")
