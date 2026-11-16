-- ============================================================================
-- VIVA - LIVE BETTER | Phase 2 Admin Migration
-- Database: smart_ecommerce_db
-- ============================================================================

USE smart_ecommerce_db;

-- 1. Create Admins Table
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('Super Admin', 'Sales Analyst', 'Inventory Manager') DEFAULT 'Super Admin',
    is_active TINYINT(1) DEFAULT 1,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_admin_email (email),
    INDEX idx_admin_username (username)
) ENGINE=InnoDB;

-- 2. Insert Super Admin User (password: Admin@2026)
INSERT INTO admins (username, email, password_hash, full_name, role)
SELECT 'admin', 'admin@viva.com', 
       'scrypt:32768:8:1$KrPp0BRl8jbRX3nz$d0e11b740853f1efeddb85147ae5c4e4a7a0a2dcdb8565165e831d3e48730df25c493c89c6baf2f7e40cddd028c256287b72b4a916f318522943fb4a15b31206',
       'VIVA Chief Administrator', 'Super Admin'
WHERE NOT EXISTS (SELECT 1 FROM admins WHERE username = 'admin');

-- 3. Enhance Inventory table with Reorder Point & Supplier Lead Time for MIS Decision Support
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS 
                   WHERE TABLE_SCHEMA = 'smart_ecommerce_db' 
                     AND TABLE_NAME = 'inventory' 
                     AND COLUMN_NAME = 'reorder_point');
SET @sql = IF(@col_exists = 0, 'ALTER TABLE inventory ADD COLUMN reorder_point INT DEFAULT 15 AFTER low_stock_threshold', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @col_exists2 = (SELECT COUNT(*) FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = 'smart_ecommerce_db' 
                      AND TABLE_NAME = 'inventory' 
                      AND COLUMN_NAME = 'lead_time_days');
SET @sql2 = IF(@col_exists2 = 0, 'ALTER TABLE inventory ADD COLUMN lead_time_days INT DEFAULT 5 AFTER reorder_point', 'SELECT 1');
PREPARE stmt2 FROM @sql2; EXECUTE stmt2; DEALLOCATE PREPARE stmt2;

-- 4. Add admin_id to inventory_transactions for audit trail
SET @col_exists3 = (SELECT COUNT(*) FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = 'smart_ecommerce_db' 
                      AND TABLE_NAME = 'inventory_transactions' 
                      AND COLUMN_NAME = 'admin_id');
SET @sql3 = IF(@col_exists3 = 0, 'ALTER TABLE inventory_transactions ADD COLUMN admin_id INT NULL AFTER reference_id', 'SELECT 1');
PREPARE stmt3 FROM @sql3; EXECUTE stmt3; DEALLOCATE PREPARE stmt3;

-- 5. Seed diverse historical orders if count is low (<10) so MIS Analytics charts display rich insights
INSERT INTO orders (order_number, customer_id, delivery_name, delivery_phone, delivery_email, delivery_address, delivery_city, delivery_state, delivery_pincode, subtotal, shipping_fee, discount, total, status, created_at)
SELECT 'VIVA-20261010-HIST01', 1, 'Rahul Sharma', '9876543210', 'rahul.sharma@email.com', '12 MG Road', 'Mumbai', 'Maharashtra', '400001', 7999.00, 0.00, 0.00, 7999.00, 'Delivered', '2026-10-10 11:30:00'
WHERE NOT EXISTS (SELECT 1 FROM orders WHERE order_number = 'VIVA-20261010-HIST01');

INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity, subtotal)
SELECT o.id, 1, 'Noise Cancelling Headphones', 7999.00, 1, 7999.00
FROM orders o WHERE o.order_number = 'VIVA-20261010-HIST01'
AND NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.order_id = o.id);

INSERT INTO payments (order_id, payment_method, amount, status, transaction_id, created_at)
SELECT o.id, 'Online', 7999.00, 'Completed', 'TXN-HIST01', '2026-10-10 11:32:00'
FROM orders o WHERE o.order_number = 'VIVA-20261010-HIST01'
AND NOT EXISTS (SELECT 1 FROM payments p WHERE p.order_id = o.id);

-- Second historical order (Electronics + Fashion)
INSERT INTO orders (order_number, customer_id, delivery_name, delivery_phone, delivery_email, delivery_address, delivery_city, delivery_state, delivery_pincode, subtotal, shipping_fee, discount, total, status, created_at)
SELECT 'VIVA-20261018-HIST02', 2, 'Priya Patel', '9876543211', 'priya.patel@email.com', '45 Park Street', 'Kolkata', 'West Bengal', '700016', 5998.00, 0.00, 0.00, 5998.00, 'Delivered', '2026-10-18 14:20:00'
WHERE NOT EXISTS (SELECT 1 FROM orders WHERE order_number = 'VIVA-20261018-HIST02');

INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity, subtotal)
SELECT o.id, 5, 'Linen Casual Shirt', 1499.00, 2, 2998.00
FROM orders o WHERE o.order_number = 'VIVA-20261018-HIST02'
AND NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.order_id = o.id AND oi.product_id = 5);

INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity, subtotal)
SELECT o.id, 2, 'Portable Bluetooth Speaker', 2499.00, 1, 2499.00
FROM orders o WHERE o.order_number = 'VIVA-20261018-HIST02'
AND NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.order_id = o.id AND oi.product_id = 2);

INSERT INTO payments (order_id, payment_method, amount, status, transaction_id, created_at)
SELECT o.id, 'Online', 5998.00, 'Completed', 'TXN-HIST02', '2026-10-18 14:22:00'
FROM orders o WHERE o.order_number = 'VIVA-20261018-HIST02'
AND NOT EXISTS (SELECT 1 FROM payments p WHERE p.order_id = o.id);

-- Third historical order (Home & Beauty)
INSERT INTO orders (order_number, customer_id, delivery_name, delivery_phone, delivery_email, delivery_address, delivery_city, delivery_state, delivery_pincode, subtotal, shipping_fee, discount, total, status, created_at)
SELECT 'VIVA-20261025-HIST03', 3, 'Amit Kumar', '9876543212', 'amit.kumar@email.com', '78 Sector 18', 'Noida', 'Uttar Pradesh', '201301', 4898.00, 0.00, 0.00, 4898.00, 'Delivered', '2026-10-25 16:45:00'
WHERE NOT EXISTS (SELECT 1 FROM orders WHERE order_number = 'VIVA-20261025-HIST03');

INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity, subtotal)
SELECT o.id, 9, 'Compact Coffee Maker', 4299.00, 1, 4299.00
FROM orders o WHERE o.order_number = 'VIVA-20261025-HIST03'
AND NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.order_id = o.id AND oi.product_id = 9);

INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity, subtotal)
SELECT o.id, 13, 'Minimalist Niacinamide Serum', 599.00, 1, 599.00
FROM orders o WHERE o.order_number = 'VIVA-20261025-HIST03'
AND NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.order_id = o.id AND oi.product_id = 13);

INSERT INTO payments (order_id, payment_method, amount, status, transaction_id, created_at)
SELECT o.id, 'COD', 4898.00, 'Completed', NULL, '2026-10-25 16:45:00'
FROM orders o WHERE o.order_number = 'VIVA-20261025-HIST03'
AND NOT EXISTS (SELECT 1 FROM payments p WHERE p.order_id = o.id);

-- Fourth order (Sports + Books)
INSERT INTO orders (order_number, customer_id, delivery_name, delivery_phone, delivery_email, delivery_address, delivery_city, delivery_state, delivery_pincode, subtotal, shipping_fee, discount, total, status, created_at)
SELECT 'VIVA-20261102-HIST04', 1, 'Rahul Sharma', '9876543210', 'rahul.sharma@email.com', '12 MG Road', 'Mumbai', 'Maharashtra', '400001', 3798.00, 0.00, 0.00, 3798.00, 'Delivered', '2026-11-02 09:15:00'
WHERE NOT EXISTS (SELECT 1 FROM orders WHERE order_number = 'VIVA-20261102-HIST04');

INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity, subtotal)
SELECT o.id, 17, 'Urban Travel Backpack', 2799.00, 1, 2799.00
FROM orders o WHERE o.order_number = 'VIVA-20261102-HIST04'
AND NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.order_id = o.id AND oi.product_id = 17);

INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity, subtotal)
SELECT o.id, 24, 'Bestseller Novel Collection', 999.00, 1, 999.00
FROM orders o WHERE o.order_number = 'VIVA-20261102-HIST04'
AND NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.order_id = o.id AND oi.product_id = 24);

INSERT INTO payments (order_id, payment_method, amount, status, transaction_id, created_at)
SELECT o.id, 'Online', 3798.00, 'Completed', 'TXN-HIST04', '2026-11-02 09:16:00'
FROM orders o WHERE o.order_number = 'VIVA-20261102-HIST04'
AND NOT EXISTS (SELECT 1 FROM payments p WHERE p.order_id = o.id);

-- Fifth order (Recent: Processing)
INSERT INTO orders (order_number, customer_id, delivery_name, delivery_phone, delivery_email, delivery_address, delivery_city, delivery_state, delivery_pincode, subtotal, shipping_fee, discount, total, status, created_at)
SELECT 'VIVA-20261110-HIST05', 4, 'Sneha Reddy', '9876543213', 'sneha.reddy@email.com', '24 Banjara Hills', 'Hyderabad', 'Telangana', '500034', 9999.00, 0.00, 0.00, 9999.00, 'Processing', '2026-11-10 13:00:00'
WHERE NOT EXISTS (SELECT 1 FROM orders WHERE order_number = 'VIVA-20261110-HIST05');

INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity, subtotal)
SELECT o.id, 3, 'Smart Watch Pro', 9999.00, 1, 9999.00
FROM orders o WHERE o.order_number = 'VIVA-20261110-HIST05'
AND NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.order_id = o.id);

INSERT INTO payments (order_id, payment_method, amount, status, transaction_id, created_at)
SELECT o.id, 'Online', 9999.00, 'Completed', 'TXN-HIST05', '2026-11-10 13:01:00'
FROM orders o WHERE o.order_number = 'VIVA-20261110-HIST05'
AND NOT EXISTS (SELECT 1 FROM payments p WHERE p.order_id = o.id);
