from chart_generator import generate_pie_chart
import matplotlib.pyplot as plt

# Test with CJK characters
items = [
    {'name': '苹果 (Apple)', 'price': 5.0, 'count': 2},
    {'name': '香蕉 (Banana)', 'price': 3.0, 'count': 5},
    {'name': '寿司 (Sushi)', 'price': 15.0, 'count': 1},
    {'name': 'ラーメン (Ramen)', 'price': 12.0, 'count': 1}
]

print("Generating pie chart with CJK characters...")
try:
    buf = generate_pie_chart(items, title="CJK Font Test")
    
    if buf:
        with open("test_cjk_chart.png", "wb") as f:
            f.write(buf.getvalue())
        print("Success! Chart saved to test_cjk_chart.png")
        
        # Verify font usage
        from chart_generator import get_cjk_font
        used_font = get_cjk_font()
        print(f"Font selected: {used_font}")
        
    else:
        print("Failed to generate chart.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
