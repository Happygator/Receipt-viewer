import sqlite3
import os
from datetime import datetime

DB_NAME = "receipts.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    """Creates the necessary tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Receipts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            merchant TEXT,
            address TEXT,
            date TEXT,
            total_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if address column exists (migration for existing DBs)
    cursor.execute("PRAGMA table_info(receipts)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'address' not in columns:
        print("Migrating database: Adding address column to receipts table...")
        cursor.execute("ALTER TABLE receipts ADD COLUMN address TEXT")

    # Check if currency column exists (migration for multi-currency)
    if 'currency' not in columns:
        print("Migrating database: Adding currency column to receipts table...")
        cursor.execute("ALTER TABLE receipts ADD COLUMN currency TEXT DEFAULT 'USD'")
    
    # Items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id INTEGER,
            name TEXT,
            price REAL,
            FOREIGN KEY (receipt_id) REFERENCES receipts (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    #print(f"Database initialized: {DB_NAME}")

def save_receipt(data):
    """
    Saves receipt data to the database.
    
    Args:
        data (dict): Expected format:
            {
                'merchant': 'Target',
                'address': '123 Main St',
                'date': '2023-10-27',
                'currency': 'USD',
                'items': [
                    {'name': 'Milk', 'price': 3.99},
                    ...
                ]
            }
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        merchant = data.get('merchant', 'Unknown')
        address = data.get('address')
        date = data.get('date')
        currency = data.get('currency', 'USD')
        items = data.get('items', [])
        
        # Calculate total just for the record (though we can sum items later)
        total_amount = sum(item['price'] for item in items)
        
        # Insert Receipt
        cursor.execute('''
            INSERT INTO receipts (merchant, address, date, total_amount, currency)
            VALUES (?, ?, ?, ?, ?)
        ''', (merchant, address, date, total_amount, currency))
        
        receipt_id = cursor.lastrowid
        
        # Insert Items
        for item in items:
            cursor.execute('''
                INSERT INTO items (receipt_id, name, price)
                VALUES (?, ?, ?)
            ''', (receipt_id, item.get('name'), item.get('price')))
            
        conn.commit()
        print(f"Saved receipt ID {receipt_id} with {len(items)} items.")
        return receipt_id
        
    except Exception as e:
        print(f"Error saving to database: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()
