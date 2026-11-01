import os
import re

print("=== Checking CSS for URLs ===")
css_path = 'styles.css'
if os.path.exists(css_path):
    with open(css_path, 'r', encoding='utf-8', errors='ignore') as f:
        css = f.read()
    urls = re.findall(r'url\s*\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)', css)
    for u in set(urls):
        clean = u.split('?')[0].split('#')[0]
        if not clean.startswith('data:'):
            exists = os.path.exists(clean)
            print(f"CSS URL: {u} (local exists: {exists})")
else:
    print("styles.css not found")

print("\n=== Checking HTML for assets ===")
for h in ['index.html', 'admin.html', 'debug_search.html']:
    if os.path.exists(h):
        with open(h, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()
        srcs = re.findall(r'src\s*=\s*[\'"]([^\'"]+)[\'"]', html)
        hrefs = re.findall(r'href\s*=\s*[\'"]([^\'"]+)[\'"]', html)
        print(f"File {h}:")
        for s in srcs:
            clean = s.split('?')[0].split('#')[0]
            if not clean.startswith(('http://', 'https://', 'data:', '//')):
                exists = os.path.exists(clean)
                print(f"  src : {s} -> exists: {exists}")
        for hr in hrefs:
            clean = hr.split('?')[0].split('#')[0]
            if not clean.startswith(('http://', 'https://', 'data:', '//', '#', 'mailto:')):
                exists = os.path.exists(clean)
                print(f"  href: {hr} -> exists: {exists}")
