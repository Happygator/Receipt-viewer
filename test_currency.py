import database
from chart_generator import generate_pie_chart
import os

# 1. Test Database Migration and Insertion
print("--- Testing Database ---")
database.init_db() # Should trigger migration if needed

test_data = {
    'merchant': 'Tokyo Store',
    'address': 'Shibuya, Tokyo',
    'date': '2024-01-31',
    'currency': 'JPY',
    'items': [
        {'name': 'Sushi Set', 'price': 1500},
        {'name': 'Green Tea', 'price': 150},
        {'name': 'Mochi', 'price': 300}
    ]
}

try:
    receipt_id = database.save_receipt(test_data)
    print(f"Successfully saved JPY receipt with ID: {receipt_id}")
    
    # Verify retrieval (optional, but good sanity check)
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT currency, total_amount FROM receipts WHERE id=?", (receipt_id,))
    row = c.fetchone()
    print(f"Retrieved: Currency={row[0]}, Total={row[1]}")
    conn.close()
    
    assert row[0] == 'JPY'
    assert row[1] == 1950.0

except Exception as e:
    print(f"Database Error: {e}")

# 2. Test Chart Generation
print("\n--- Testing Chart Generation ---")
try:
    buf = generate_pie_chart(test_data['items'], title="JPY Expense Test", currency='JPY')
    if buf:
        with open("test_jpy_chart.png", "wb") as f:
            f.write(buf.getvalue())
        print("Success! Chart saved to test_jpy_chart.png. Check for '¥' symbol.")
    else:
        print("Failed to generate chart.")
except Exception as e:
    print(f"Chart Error: {e}")
    import traceback
    traceback.print_exc()
