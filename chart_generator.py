import matplotlib.pyplot as plt
import io

def generate_pie_chart(items, title="Top Expense Items", top_n=10, currency="USD"):
    """
    Generates a pie chart for the top N most expensive items.
    Returns a bytes buffer containing the image.
    """
    if not items:
        return None

    # Aggregate duplicated items (same name)
    aggregated = {}
    for item in items:
        name = item['name']
        price = item['price']
        if name in aggregated:
            aggregated[name]['price'] += price
            aggregated[name]['count'] += 1
        else:
            aggregated[name] = {'name': name, 'price': price, 'count': 1}
    
    unique_items = list(aggregated.values())

    # Sort and take top N
    # Items should already be net price (discounts applied)
    sorted_items = sorted(unique_items, key=lambda x: x['price'], reverse=True)
    top_items = sorted_items[:top_n]
    
    # Bundle the rest into "Others" if there are more
    if len(unique_items) > top_n:
        other_price = sum(item['price'] for item in sorted_items[top_n:])
        top_items.append({'name': 'Others', 'price': other_price, 'count': 1}) # Count 1 for bundle

    # Create labels with Count and Price
    # Example: "3 AVOCADO OIL ($77.97)" or "AVOCADO OIL (¥2500)"
    sizes = [item['price'] for item in top_items]
    labels = []
    
    # Simple symbol mapping
    currency_symbols = {
        'USD': '$',
        'CAD': '$',
        'AUD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CNY': '¥',
        'KRW': '₩',
    }
    symbol = currency_symbols.get(currency.upper(), currency + " ")

    for item in top_items:
        qty_prefix = f"{item['count']} " if item.get('count', 1) > 1 else ""
        price_str = f"{item['price']:.2f}"
        if currency.upper() in ['JPY', 'KRW']: # Currencies typically without decimals
             price_str = f"{int(item['price'])}"
             
        labels.append(f"{qty_prefix}{item['name'][:20]} ({symbol}{price_str})")

    # Create plot
    plt.figure(figsize=(10, 6))
    
    # Set CJK-compatible font
    font_name = get_cjk_font()
    if font_name:
        plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
        plt.rcParams['axes.unicode_minus'] = False # Fix minus sign
        
    patches, texts, autotexts = plt.pie(
        sizes, 
        labels=labels, 
        autopct='%1.1f%%', 
        startangle=140,
        textprops={'fontsize': 10}
    )
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(title, pad=20)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches="tight")
    buf.seek(0)
    plt.close()
    
    return buf

def get_cjk_font():
    """
    Checks for available CJK fonts on the system (Windows/Linux) 
    and returns the first one found.
    """
    from matplotlib import font_manager
    
    # Candidate fonts for Windows and Linux (including Raspberry Pi)
    cjk_candidates = [
        "Microsoft YaHei", "SimHei", "Malgun Gothic", "Meiryo",  # Windows
        "WenQuanYi Zen Hei", "WenQuanYi Micro Hei", "Noto Sans CJK SC", "Noto Sans CJK JP", "Droid Sans Fallback", # Linux
        "Arial Unicode MS", "MS Gothic" # Fallbacks
    ]
    
    for font in cjk_candidates:
        try:
            # findfont returns the path if found, or a default fallback if not found EXACTLY.
            # We need to be careful. font_manager.findfont(name, fallback_to_default=False) raises exception if not found.
            # However, fallback_to_default=False is not always reliable in older versions or might behave differently.
            # A better check is to see if the found font name matches.
            
            # Let's try a simpler approach compatible with common setups:
            # simple lookup by name.
            if font in [f.name for f in font_manager.fontManager.ttflist]:
                return font
                
            # Alternatively, check by file path (costlier). 
            # Let's rely on the name check in the system font list which is already loaded.
        except Exception:
            continue
            
    # If explicit names fail, try finding any font file that might work (less reliable without heavy logic)
    # We'll return None and let matplotlib use default (squares) if nothing found, 
    # but let's try to be robust.
    return None
