import sys
print("Importing paddle...")
try:
    from paddleocr import PaddleOCR
    print("Paddle imported.")
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    print("Paddle initialized. Running OCR...")
    res = ocr.ocr("receipt.jpg", cls=True)
    print("OCR finished.")
    print(res)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
