import urllib.request
import re
import json

req = urllib.request.Request('https://incidecoder.com', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
html = urllib.request.urlopen(req).read().decode('utf-8')

# The popular products are usually under the "Most popular products" section
# Let's find links to /products/
matches = re.findall(r'href="(/products/[^"]+)">([^<]+)</a>', html)
# Let's print out the first 10 unique products
products = []
seen = set()
for href, name in matches:
    name = name.strip()
    if href not in seen and name:
        seen.add(href)
        products.append({"name": name, "url": "https://incidecoder.com" + href})
        if len(products) >= 10:
            break

print(json.dumps(products, indent=2))
