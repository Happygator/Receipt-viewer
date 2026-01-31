from matplotlib import font_manager

fonts = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
print(f"Found {len(fonts)} fonts.")

cjk_candidates = ['SimHei', 'Microsoft YaHei', 'MS Gothic', 'Meiryo', 'Arial Unicode MS']
available_cjk = []

for font in fonts:
    try:
        prop = font_manager.FontProperties(fname=font)
        name = prop.get_name()
        if name in cjk_candidates:
            available_cjk.append(name)
        # Also check for names containing 'CJK' or 'Gothic' or 'Hei'
        elif 'CJK' in name or 'Gothic' in name or 'Hei' in name or 'YaHei' in name:
             available_cjk.append(name)
    except:
        pass

print("Potential CJK Fonts found:")
for f in sorted(list(set(available_cjk))):
    print(f)
