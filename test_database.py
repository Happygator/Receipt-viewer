import database
import os

DB_FILE = "receipts.db"

def test_database():
    # Clean up previous test
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        
    print("Initializing DB...")
    database.init_db()
    
    # Test Data
    mock_data = {
        "merchant": "Test Store",
        "date": "2023-01-01",
        "items": [
            {"name": "Apple", "price": 1.50},
            {"name": "Banana", "price": 0.75}
        ]
    }
    
    print("Saving receipt...")
    receipt_id = database.save_receipt(mock_data)
    print(f"Receipt saved with ID: {receipt_id}")
    
    # Verify
    conn = database.get_connection()
    c = conn.cursor()
    
    # Check Receipt
    receipt = c.execute("SELECT * FROM receipts WHERE id=?", (receipt_id,)).fetchone()
    print("Receipt Row:", receipt)
    assert receipt[1] == "Test Store"
    assert receipt[2] == "2023-01-01"
    assert receipt[3] == 2.25  # Total amount
    
    # Check Items
    items = c.execute("SELECT * FROM items WHERE receipt_id=?", (receipt_id,)).fetchall()
    print(f"Items found: {len(items)}")
    for item in items:
        print("Item Row:", item)
        
    assert len(items) == 2
    assert items[0][2] == "Apple"
    assert items[0][3] == 1.50
    
    print("SUCCESS: Database verification passed!")
    conn.close()

if __name__ == "__main__":
    test_database()
