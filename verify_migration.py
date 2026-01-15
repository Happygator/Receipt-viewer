import database
import sqlite3

def verify_migration():
    print("Initializing DB (triggering migration check)...")
    database.init_db()
    
    conn = sqlite3.connect("receipts.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(receipts)")
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Columns in receipts: {columns}")
    
    if 'address' in columns:
        print("SUCCESS: 'address' column found.")
    else:
        print("FAILURE: 'address' column NOT found.")
    
    conn.close()

def verify_insertion():
    print("\nTesting insertion with address...")
    data = {
        'merchant': 'Test Store',
        'address': '123 Test Lane',
        'date': '2025-01-01',
        'items': [{'name': 'Test Item', 'price': 10.0}]
    }
    
    try:
        receipt_id = database.save_receipt(data)
        
        conn = sqlite3.connect("receipts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT address FROM receipts WHERE id=?", (receipt_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == '123 Test Lane':
            print(f"SUCCESS: Address '123 Test Lane' retrieved from DB for ID {receipt_id}.")
        else:
            print(f"FAILURE: Retrieved address: {result}")
            
    except Exception as e:
        print(f"FAILURE: Insertion failed: {e}")

if __name__ == "__main__":
    verify_migration()
    verify_insertion()
