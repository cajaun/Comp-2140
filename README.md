
# Braeton Gate Wholesale Inventory Management System

A streamlined inventory control system designed for wholesale businesses. It provides efficient product management, stock tracking, condition logging, reporting, and automated slow-moving/overstock detection. The system is built on a clean, scalable relational database to ensure accuracy, traceability, and performance.

---

# Key Functional Modules

## 1. Item Management
- Add, edit, delete, and categorize products.
- Track price, quantity, unit type, and reorder levels.
- Search and filter items quickly across categories and attributes.

## 2. Stock Adjustment Log
- Record deliveries, sales, returns, and manual stock corrections.
- Each entry includes date, quantity, and reason.
- Maintains a complete audit trail for accountability and reconciliation.

## 3. Condition Tracking
- Log damaged, expired, spoiled, or otherwise compromised inventory.
- Captures quantity affected, cause, and financial impact.
- Monthly summaries reveal operational issues and prevent repeat losses.

## 4. Reporting & Insights
- Generate daily, weekly, or monthly inventory and sales reports.
- Supports informed restocking, budgeting, and purchasing decisions.

## 5. Slow-Moving & Overstock Monitoring
- Flags items that remain unsold for long periods or exceed threshold quantities.
- Provides suggested actions (discounting, bundling, discontinuation).
- Improves inventory turnover and reduces storage costs.

---

# Database Design Overview

The system uses a relational database to maintain strong data integrity, enforce relationships, and support detailed historical tracking. The design focuses on normalization, auditability, and expandability.

---

## Categories
Stores product classifications.
- category_id (PK)
- name
- description

## Items
Central table for all inventory products.
- item_id (PK)
- name
- category_id (FK → categories)
- price
- quantity
- current_stock
- unit
- reorder_level
- created_at, updated_at

## Users
Manages authentication and user permissions.
- user_id (PK)
- username
- password_hash
- role

## Stock Adjustments
Tracks every item quantity change.
- adjust_id (PK)
- item_id (FK → items)
- user_id (FK → users)
- adjust_type (add/remove)
- quantity
- reason
- created_at, adjusted_at

## Item Conditions
Logs issues such as damage or spoilage.
- condition_id (PK)
- item_id (FK)
- condition_type
- quantity
- reason, cause
- cost_impact
- recorded_at

## Reports
Stores report metadata and output.
- report_id (PK)
- report_type
- start_date, end_date
- generated_at
- user_id (FK)
- parameters
- report_data

## Slow-Moving & Overstock
Monitors inventory health.
- sm_id (PK)
- item_id (FK)
- last_adjust_id (FK)
- flagged_at
- last_sold_date
- stock_quantity
- threshold_days, threshold_quantity
- suggested_action

## Config
System-wide settings.
- parameter_name
- parameter_value
- updated_at

---


