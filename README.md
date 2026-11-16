# VIVA – LIVE BETTER
## Smart E-Commerce Decision Support System (SEDSS)
### A Full-Stack Enterprise MIS Web Platform (Phase 1 & Phase 2)

---

## 1. Project Overview

**VIVA – LIVE BETTER** is an enterprise-grade Smart E-Commerce Decision Support System (SEDSS) developed using Python Flask, MySQL, and modern responsive front-end technologies. 

The system unifies two complementary subsystems running seamlessly on a single Flask instance and shared relational database:
1. **Phase 1 – Customer Purchasing Website**: A minimalist, high-conversion e-commerce storefront inspired by modern lifestyle aesthetics.
2. **Phase 2 – Executive Admin & MIS Decision Support System (DSS)**: A dark-themed management dashboard providing business intelligence, inventory reorder point (ROP) calculations, live sales velocity tracking, customer lifetime analytics, and automated decision-support recommendations.

---

## 2. Technology Stack

- **Backend:** Python 3.11+, Flask 3.1
- **Database:** MySQL 8.0+ / 9.0+ (`smart_ecommerce_db`)
- **Connector:** PyMySQL (pure-Python connector with `DictCursor` and ACID transactions)
- **Security:** Werkzeug password hashing (`generate_password_hash`, `check_password_hash`), parameterized SQL queries, separate admin/customer session management
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons 1.11, Chart.js 4
- **Typography:** Plus Jakarta Sans & JetBrains Mono (Google Fonts)

---

## 3. Quick Start & Execution

### Prerequisites
- Python 3.11+
- MySQL Server 8.0+ or 9.0+ running on `localhost:3306`

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/SHERSHAM/MIS-smart_ecommerce.git
cd MIS-smart_ecommerce

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env
# Edit .env to set your MySQL password and Secret Key
```

### Database Setup
Import the complete, pre-seeded database dump:
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS smart_ecommerce_db;"
mysql -u root -p smart_ecommerce_db < database.sql
```

### Running the Web Server
```bash
python app.py
```

- **Customer Purchasing Website:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Admin Management & MIS Portal:** [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)

#### Default Administrator Credentials
- **Username / Email:** `admin` (or `admin@viva.com`)
- **Password:** `Admin@2026`
- **Role:** Super Admin

#### Default Customer Test Account
- **Email:** `academic_tester@viva.com`
- **Password:** `VivaPass@2026`

---

## 4. System Architecture & Features

### A. Customer Purchasing Website (Phase 1)
- **Storefront & Navigation:** Announcement banner, responsive hero slider, circular category taxonomy, promotional collection cards, and customer testimonials.
- **Product Discovery:** Real-time search, price filter, brand filter, stock availability filter, and multi-criteria sorting.
- **Cart & Wishlist:** AJAX add-to-cart, quantity adjustments, threshold-based free shipping calculator (orders > ₹999), and wishlist-to-cart movement.
- **Checkout & Payment:** Multi-address selector, address creation modal, simulated COD & Online payment gateways with atomic stock deduction.
- **Order Tracking:** Visual milestone order progress timeline (*Pending &rarr; Confirmed &rarr; Processing &rarr; Shipped &rarr; Delivered*).
- **Customer Account:** Profile management, password changes, and saved address book.

### B. Admin MIS Decision Support System (Phase 2)
The Admin Portal resides in `admin_portal/` with a modular architecture:
- **Executive Overview Dashboard (`/admin/dashboard`):** Real-time KPI summary cards (Net Revenue, Total Orders, Customer Count, Active SKUs, Low Stock alerts, and MoM growth percentage), 12-month revenue trajectory chart, and category revenue share donut.
- **MIS Decision Analytics (`/admin/analytics`):**
  - **Top 10 Best Sellers:** Rank products by total sales volume and gross revenue with velocity status indicators.
  - **30-Day Slow-Moving Inventory:** Identifies stagnant stock holding working capital with prescriptive liquidation guidance (e.g. flash sales, bundle promotions).
- **Strategic Decision Support System (`/admin/insights`):** Automated deterministic business rule engine that monitors stockout risks on top performers, capital allocation imbalances, category revenue concentration, and customer retention metrics.
- **Inventory Control & Reorder Point (`/admin/inventory`):**
  - Mathematical Reorder Point formula:
    $$\text{ROP} = (\text{Average Daily Sales} \times \text{Lead Time}) + \text{Safety Stock}$$
  - Dynamic restock recommendations with calculated order quantities.
  - Manual stock adjustment modal with support for `RESTOCK`, `RETURN`, `DAMAGE`, and `CORRECTION`.
  - **Audit Trail Ledger (`/admin/inventory/transactions`):** Complete immutable record of all product stock movements.
- **Catalog & Orders Management (`/admin/products`, `/admin/categories`, `/admin/orders`):**
  - Full CRUD for products with image upload and validation.
  - Category manager with real-time product count protection against accidental deletion.
  - Order status updater with automatic stock restoration upon cancellation.
- **Customer Intelligence (`/admin/customers`):** Lifetime value metrics, order history, and behavioral customer segmentation (*VIP High-Value, Repeat Customer, First-Time Buyer, Lead*).
- **Executive Reports & CSV Exporter (`/admin/reports`):**
  - Interactive tabular viewer with date range filtering.
  - 8 Standard Reports: Daily Sales, Monthly Sales, Product Performance, Customer Purchase, Inventory Status, Low Stock Alert, Best Sellers, and Order Status.
  - One-click RFC 4180-compliant CSV download.

---

## 5. Automated Verification Suites

The codebase includes two automated test suites:
```bash
# Run 20-point portal security and route verification
python admin_portal/test_admin_portal.py

# Run cross-portal live interaction and workflow tests
python admin_portal/test_live_workflow.py
```

---

## 6. Directory Structure

```
smart_ecommerce/
├── app.py                         # Application factory, Jinja ChoiceLoader, blueprint mounting
├── config.py                      # Development, Testing, Production configurations
├── database.sql                   # Complete unified MySQL database dump
├── requirements.txt               # Python package dependencies
├── .env.example                   # Environment variable template
├── admin_portal/                  # Phase 2: Admin & MIS DSS Module
│   ├── routes/                    # 10 Admin Blueprints
│   ├── services/                  # Analytical & DSS business logic services
│   ├── static/                    # Dark theme CSS & Chart.js controllers
│   ├── templates/admin/           # 15 Dark MIS dashboard templates
│   ├── migrations/                # Schema enhancement SQL scripts
│   ├── test_admin_portal.py       # 20-point verification script
│   └── test_live_workflow.py      # Cross-system live integration test
├── models/                        # Data access models (Customer, Product, Order, Admin, etc.)
├── routes/                        # Customer storefront route blueprints
├── static/                        # Customer storefront CSS, JS, and product imagery
└── templates/                     # Customer storefront HTML templates
```

---

## 7. License

Academic & Educational Project – VIVA Smart E-Commerce Decision Support System (SEDSS).
