import os
import re

print("=== Checking JS files for fetch / XHR / URLs ===")
js_dir = 'js'
for fname in sorted(os.listdir(js_dir)):
    if not fname.endswith('.js'):
        continue
    fpath = os.path.join(js_dir, fname)
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    fetches = re.findall(r'fetch\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', content)
    if fetches:
        print(f"\nIn {fname}:")
        for ft in fetches:
            print(f"  fetch -> {ft}")
