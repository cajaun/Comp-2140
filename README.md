# Braeton Gate Wholesale Inventory System

A comprehensive Inventory Management System built with Python's Tkinter for the GUI and PostgreSQL for data persistence. This application is designed to help manage inventory, track stock levels, handle user management, and generate reports.

## Features

- **Dashboard**: Overview of key metrics like total inventory value, low stock items, and recent activity.
- **Inventory Management**: Add, update, delete, and view inventory items.
- **Category Management**: Organize items into categories.
- **Stock Adjustments**: Record stock increases or decreases (e.g., new shipments, shrinkage).
- **Damaged/Expired Tracking**: Manage items that are no longer sellable.
- **User Management**: Manage system users and their roles.
- **Reports**: Generate reports on inventory status and movements.
- **Settings**: Configure application settings.

## Prerequisites

- **Python 3.8+**: Ensure you have Python installed.
- **PostgreSQL**: This application requires a PostgreSQL database.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd Comp-2140
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Database Setup:**
    - Ensure PostgreSQL is running.
    - Create a database named `inventory_db`:
      ```sql
      CREATE DATABASE inventory_db;
      ```
    - **Configuration**: The database connection string is located in `data/db.py`. By default, it is set to:
      ```python
      DATABASE_URL = "postgresql://localhost/inventory_db"
      ```
      If your PostgreSQL configuration (username, password, host, port) is different, please update this line in `data/db.py`. For example:
      ```python
      DATABASE_URL = "postgresql://user:password@localhost:5432/inventory_db"
      ```

## Running the Application

To start the application, run the `main.py` file from the root directory:

```bash
python main.py
```

The application window should appear, defaulting to the Dashboard view.

## Project Structure

- `main.py`: Entry point of the application.
- `ui/`: Contains all user interface code (Views, Components, Styles).
- `data/`: Contains database models, connection logic, and mock data.
- `assets/`: Contains static assets (images, icons).
