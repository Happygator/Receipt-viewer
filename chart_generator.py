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
    
    # Priority 1: High-quality CJK fonts (Windows/Mac/Linux)
    # We remove "Droid Sans Fallback" because it often lacks ASCII glyphs on some Linux systems.
    primary_candidates = [
        "Microsoft YaHei", "SimHei", "Malgun Gothic", "Meiryo", # Windows
        "Noto Sans CJK JP", "Noto Sans CJK SC", "Noto Sans CJK TC", # Linux (Best)
        "WenQuanYi Zen Hei", "WenQuanYi Micro Hei", # Linux (Good)
    ]

    # Check loaded fonts first (fast)
    system_font_names = [f.name for f in font_manager.fontManager.ttflist]
    for font in primary_candidates:
        if font in system_font_names:
            return font
            
    # Priority 2: Scan system fonts explicitly for Noto CJK (Reliable on Pi)
    # This addresses the issue where ttflist cache might be stale or incomplete.
    try:
        fonts = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
        for font_path in fonts:
            try:
                prop = font_manager.FontProperties(fname=font_path)
                name = prop.get_name()
                
                # Check for Noto CJK families
                if "Noto" in name and "CJK" in name:
                     # Add to manager to ensure it's usable
                    font_manager.fontManager.addfont(font_path)
                    return name
            except:
                continue
    except Exception as e:
        print(f"Font scan error: {e}")

    # Priority 3: Fallbacks and fuzzy matching
    # Add 'URW Gothic' since user has it
    fallback_candidates = ["Arial Unicode MS", "MS Gothic", "URW Gothic"]
    for font in fallback_candidates:
        if font in system_font_names:
            return font

    # Fuzzy search through all available loaded fonts
    cw_keywords = ['cjk', 'gothic', 'hei', 'mincho', 'song', 'kai', 'arial unicode']
    for font in font_manager.fontManager.ttflist:
        name_lower = font.name.lower()
        if "droid" in name_lower and "fallback" in name_lower:
             continue # Skip Droid Sans Fallback
        for kw in cw_keywords:
            if kw in name_lower:
                return font.name
                
    return None
