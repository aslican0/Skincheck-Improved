import urllib.request
import json
import re
import time

search_url = "https://www.korendy.com.tr/search/suggest.json?q=Medicube&resources[type]=product&resources[limit]=100"
req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode('utf-8'))
    handles = [p['handle'] for p in data.get('resources', {}).get('results', {}).get('products', [])]
except Exception as e:
    print("Failed to fetch search results:", e)
    handles = []

new_products = []

for handle in handles:
    prod_url = f"https://www.korendy.com.tr/products/{handle}.json"
    try:
        preq = urllib.request.Request(prod_url, headers={'User-Agent': 'Mozilla/5.0'})
        presp = urllib.request.urlopen(preq)
        pdata = json.loads(presp.read().decode('utf-8'))
        p = pdata.get('product', {})
    except Exception as e:
        print(f"Failed to fetch product {handle}:", e)
        continue
        
    title = p.get("title", "")
    
    # Extract quantity if present
    quantity = ""
    qty_match = re.search(r'(\d+ml|\d+g|\d+ ml|\d+ g|\d+li|\d+ adet)$', title, re.IGNORECASE)
    if qty_match:
        quantity = qty_match.group(1).replace(" ", "")
        name = title[:qty_match.start()].strip()
    else:
        name = title

    brand = p.get("vendor", "MEDICUBE").upper()
    category = "Skincare"
    
    images = p.get("images", [])
    image_url = images[0]["src"] if images else ""
    
    body_html = p.get("body_html", "")
    
    ingredients_list = []
    clean_body = re.sub(r'<[^>]+>', ' ', body_html).replace('&nbsp;', ' ')
    
    match = re.search(r'İçerik(?:ler)?\s*:?(.*)', clean_body, re.IGNORECASE | re.DOTALL)
    if not match:
        match = re.search(r'Ingredients\s*:?(.*)', clean_body, re.IGNORECASE | re.DOTALL)
        
    if match:
        ing_text = match.group(1)
        ing_text = re.split(r'Nasıl Kullanılır|Uyarılar|Kullanım|Öne Çıkan Özellikler', ing_text, flags=re.IGNORECASE)[0]
        
        raw_ings = ing_text.split(',')
        if len(raw_ings) >= 2:
            for raw_ing in raw_ings:
                cleaned = re.sub(r'\(.*?\)', '', raw_ing)
                cleaned = cleaned.strip('.\r\n\t* ')
                if cleaned and len(cleaned) < 50:
                    ingredients_list.append(cleaned.title())

    if not ingredients_list:
        ingredients_list = ["Water", "Glycerin", "Unknown"]

    new_products.append({
        "id": f"local_medicube_{p['id']}",
        "barcode": str(p['variants'][0]['barcode'] if p['variants'] and p['variants'][0].get('barcode') else p['id']),
        "name": name,
        "brand": brand,
        "category": category,
        "imageUrl": image_url,
        "ingredientNames": ingredients_list,
        "quantity": quantity if quantity else "50ml",
        "veganStatus": "unknown"
    })
    time.sleep(0.5)

file_path = "c:/Users/hasli/OneDrive/Masaüstü/FinalProject/js/products.js"
try:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    match = re.search(r'const SEED_PRODUCTS = \[(.*?)\];', text, re.DOTALL)
    if match:
        existing_content = match.group(1).strip()
        if existing_content.endswith(','):
            existing_content = existing_content[:-1]
    else:
        existing_content = ""

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

    print(f"Appended {len(new_products)} MEDICUBE products.")
except Exception as e:
    print(f"Error modifying js file: {e}")
