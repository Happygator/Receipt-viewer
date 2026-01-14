from ocr_processor import process_image, initialize
from chart_generator import generate_pie_chart
import os
import sys

def main():
    # Load env (ocr_processor does it, but we can do it too)
    from dotenv import load_dotenv
    load_dotenv()
    
    image_path = "receipt.jpg"
    log_file = os.path.join("testing_logs", "test_gemini.txt")
    
    # Redirect stdout to log file and console
    class Logger(object):
        def __init__(self, filename):
            self.terminal = sys.stdout
            self.log = open(filename, "w", encoding='utf-8')
        
        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)
            
        def flush(self):
            self.terminal.flush()
            self.log.flush()

    sys.stdout = Logger(log_file)
    
    print(f"Processing {image_path} with Gemini 1.5 Flash...")
    initialize()
    
    try:
        if not os.path.exists(image_path):
             print(f"Error: {image_path} not found.")
             return

        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # 1. Process
        print("Sending to Gemini...")
        data = process_image(image_bytes)
        items = data.get('items', [])
        
        # 2. Results
        print(f"Found {len(items)} items:")
        total = 0
        for item in items:
            name = item.get('name', 'Unknown')
            price = item.get('price', 0.0)
            total += price
            print(f"- {name}: ${price:.2f}")
            
        print(f"Calculated Total: ${total:.2f}")
            
        # 3. Chart
        if items:
            generate_pie_chart(items)
            print("Chart generated (in memory).")
        else:
            print("No items found.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
