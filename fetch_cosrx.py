import urllib.request
import json
import re

url = "https://www.korendy.com.tr/collections/cosrx/products.json"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req)
data = json.loads(resp.read().decode('utf-8'))

products = data.get("products", [])

new_products = []

for p in products:
    title = p.get("title", "")
    # Remove the Turkish translation in parenthesis if exists
    name = re.sub(r'\(.*?\)', '', title).strip()
    # sometimes there are sizes like 150ml, extract it
    quantity = ""
    qty_match = re.search(r'(\d+ml|\d+g|\d+ ml|\d+ g)$', name, re.IGNORECASE)
    if qty_match:
        quantity = qty_match.group(1).replace(" ", "")
        name = name[:qty_match.start()].strip()
    
    brand = p.get("vendor", "COSRX").upper()
    category = "Skincare"
    
    images = p.get("images", [])
    image_url = images[0]["src"] if images else ""
    
    body_html = p.get("body_html", "")
    
    # Extract ingredients. Usually marked by "İçerik", "Ingredients", or "Tüm İçerik Listesi"
    # we can use a regex to find everything after "İçerik" or similar
    ingredients_list = []
    
    # Strip HTML tags
    clean_body = re.sub(r'<[^>]+>', ' ', body_html)
    clean_body = clean_body.replace('&nbsp;', ' ')
    
    # Try to find ingredients
    match = re.search(r'İçerik(?:ler)?\s*:?(.*)', clean_body, re.IGNORECASE | re.DOTALL)
    if not match:
        match = re.search(r'Ingredients\s*:?(.*)', clean_body, re.IGNORECASE | re.DOTALL)
        
    if match:
        ing_text = match.group(1)
        # cut off at the next heading or empty line (heuristics)
        ing_text = re.split(r'Nasıl Kullanılır|Uyarılar|Kullanım|Öne Çıkan Özellikler', ing_text, flags=re.IGNORECASE)[0]
        
        # Split by comma
        raw_ings = ing_text.split(',')
        if len(raw_ings) < 3:
            # maybe separated by period or dash
            pass
        else:
            for raw_ing in raw_ings:
                cleaned = re.sub(r'\(.*?\)', '', raw_ing) # remove things in parens
                cleaned = cleaned.strip('.\r\n\t* ')
                if cleaned and len(cleaned) < 50:
                    ingredients_list.append(cleaned.title())
                    
    # Fallback to a predefined list if we can't extract (for demonstration, we will just use empty or placeholder)
    if not ingredients_list:
        ingredients_list = ["Water", "Glycerin", "Unknown"]

    new_products.append({
        "id": f"local_cosrx_{p['id']}",
        "barcode": str(p['variants'][0]['barcode'] if p['variants'] and p['variants'][0].get('barcode') else p['id']),
        "name": name,
        "brand": brand,
        "category": category,
        "imageUrl": image_url,
        "ingredientNames": ingredients_list,
        "quantity": quantity if quantity else "50ml",
        "veganStatus": "unknown"
    })

js_content = "const SEED_PRODUCTS = [\n"

# First, read the existing SEED_PRODUCTS
file_path = "c:/Users/hasli/OneDrive/Masaüstü/FinalProject/js/products.js"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Extract the existing array contents
match = re.search(r'const SEED_PRODUCTS = \[(.*?)\];', text, re.DOTALL)
if match:
    existing_content = match.group(1).strip()
    if existing_content.endswith(','):
        existing_content = existing_content[:-1] # remove trailing comma
else:
    existing_content = ""

# Append new products
added_content = ""
for idx, p in enumerate(new_products):
    added_content += "  {\n"
    for key, value in p.items():
        if isinstance(value, str):
            added_content += f"    {key}: '{value.replace(chr(39), chr(39)+chr(39))}',\n"
        elif isinstance(value, list):
            items = ", ".join([f"'{i.replace(chr(39), chr(39)+chr(39))}'" for i in value])
            added_content += f"    {key}: [{items}],\n"
    added_content += "  }"
    if idx < len(new_products) - 1:
        added_content += ",\n"
    else:
        added_content += "\n"

full_array = f"const SEED_PRODUCTS = [\n{existing_content},\n{added_content}];"
text = re.sub(r'const SEED_PRODUCTS = \[.*?\];', full_array, text, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Appended {len(new_products)} COSRX products.")
