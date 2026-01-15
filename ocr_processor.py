import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

# Ensure env vars are loaded
load_dotenv()

def initialize():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # We print an error but don't crash yet; user might add it later
        print("WARNING: GEMINI_API_KEY not found in .env. OCR will fail.")
    else:
        genai.configure(api_key=api_key)
        print("Gemini API configured.")

def process_image(image_bytes):
    """
    Sends receipt image to Gemini 1.5 Flash and returns a list of items.
    Returns:
        list[dict]: [{'name': 'Item Name', 'price': 10.99}, ...]
    """
    try:
        # Check config again just in case
        if not os.getenv("GEMINI_API_KEY"):
            print("Error: Missing GEMINI_API_KEY")
            return []

        model = genai.GenerativeModel("gemini-flash-latest")
        
        prompt = """
        You are an expert receipt parser. Analyze this receipt image.
        1. Extract the Merchant Name.
        2. Extract the Date of purchase (format: YYYY-MM-DD). If not found, look for date-like strings.
        3. Extract the Store Address.
        4. Extract a list of all purchased items.
           - Name: Clean up the name (remove codes like 123456, remove tax flags like 'A' or 'Tax').
           - Price: Must be the NET price.
             * IMPORTANT: If there is a discount line below an item (e.g. "Instant Savings", "Coupon", "-4.00"), SUBTRACT it from the item's price.
             * Example: Item $19.99 followed by Discount -$4.00 -> Price should be $15.99.
        5. Return strictly a JSON object. No markdown formatting.
        
        Schema:
        {
          "merchant": "string",
          "address": "string",
          "date": "YYYY-MM-DD",
          "items": [
            {"name": "string", "price": number}
          ]
        }
        """
        
        response = model.generate_content([
            {'mime_type': 'image/jpeg', 'data': image_bytes},
            prompt
        ])
        
        # Clean response text (sometimes includes ```json ... ```)
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            # Remove first line (```json) and last line (```)
            if lines[0].startswith("```"): lines = lines[1:]
            if lines[-1].startswith("```"): lines = lines[:-1]
            raw_text = "\n".join(lines)
            
        data = json.loads(raw_text)
        return data  # Return full object including merchant and date
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        import traceback
        traceback.print_exc()
        return []
