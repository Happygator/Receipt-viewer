from chart_generator import get_cjk_font
import matplotlib.font_manager as fm

print("--- Font Debug Tool ---")
found_font = get_cjk_font()
print(f"Detected CJK Font: {found_font}")

print("\n--- Searching System Fonts for Candidates ---")
keywords = ['cjk', 'gothic', 'hei', 'mincho', 'song', 'kai', 'arial unicode']
detected = []
for f in fm.fontManager.ttflist:
    name_lower = f.name.lower()
    for kw in keywords:
        if kw in name_lower:
            detected.append(f.name)

detected = sorted(list(set(detected)))
if detected:
    print(f"Found {len(detected)} potential CJK fonts:")
    for d in detected:
        print(f" - {d}")
else:
    print("NO CJK FONTS FOUND via fuzzy search.")

print("\n--- Instructions ---")
print("If 'Detected CJK Font' is None, please install fonts on your Raspberry Pi:")
print("sudo apt-get install fonts-noto-cjk fonts-wqy-zenhei")
