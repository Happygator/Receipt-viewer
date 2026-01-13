import matplotlib.pyplot as plt
import io

def generate_pie_chart(items, top_n=10):
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
    # Example: "3 AVOCADO OIL ($77.97)" or "AVOCADO OIL ($25.99)"
    sizes = [item['price'] for item in top_items]
    labels = []
    for item in top_items:
        qty_prefix = f"{item['count']} " if item.get('count', 1) > 1 else ""
        labels.append(f"{qty_prefix}{item['name'][:20]} (${item['price']:.2f})")

    # Create plot
    plt.figure(figsize=(10, 6))
    patches, texts, autotexts = plt.pie(
        sizes, 
        labels=labels, 
        autopct='%1.1f%%', 
        startangle=140,
        textprops={'fontsize': 10}
    )
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Top Expense Items')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches="tight")
    buf.seek(0)
    plt.close()
    
    return buf
