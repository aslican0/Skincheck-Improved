import urllib.request
import re
import json

base_url = "https://www.frudia.com"

product_codes = set()
pages_to_check = [
    "/en/product/product01.php",
    "/en/product/product02.php",
    "/en/product/product06.php",
    "/en/product/product07.php",
]

for base_page in pages_to_check:
    for page in range(1, 4):
        url = f"{base_url}{base_page}?page={page}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, timeout=10)
            html = resp.read().decode('utf-8', errors='ignore')
            
            links = re.findall(r'href=[\'"]([^\'"]+ptype=view[^\'"]+prdcode=([0-9a-zA-Z]+)[^\'"]*)[\'"]', html)
            added_any = False
            for full_href, prdcode in links:
                product_codes.add(prdcode)
                added_any = True
                
            if not added_any:
                break
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            break

print(f"Found {len(product_codes)} unique products.")

new_products = []

for code in product_codes:
    url = f"{base_url}/en/product/product01.php?ptype=view&prdcode={code}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Name
        name_match = re.search(r'class="ko_tit"[^>]*>(.*?)<\/p>', html)
        if not name_match:
            name_match = re.search(r'class="pro_stitle"[^>]*>(.*?)<\/p>', html)
        if not name_match:
            continue
            
        full_name = name_match.group(1).strip()
        full_name = re.sub(r'<[^>]+>', '', full_name)
        name = re.sub(r'\(.*?\)', '', full_name).strip()
        
        # Quantity
        quantity = ""
        qty_match = re.search(r'(\d+ml|\d+g|\d+ ml|\d+ g)$', name, re.IGNORECASE)
        if qty_match:
            quantity = qty_match.group(1).replace(" ", "")
            name = name[:qty_match.start()].strip()
            
        if not quantity:
            ml_matches = re.findall(r'<p>\s*(\d+ml|\d+g)\s*<\/p>', html, re.IGNORECASE)
            if ml_matches:
                quantity = ml_matches[0].replace(" ", "")

        # Image
        image_url = ""
        img_wrap_match = re.search(r'class="img_wrap"[^>]*>.*?<img[^>]*style="background:url\([\'"]?([^>]*?)[\'"]?\)', html, re.DOTALL)
        if img_wrap_match:
            image_url = base_url + img_wrap_match.group(1)
        else:
            img_match = re.search(r'class="img_wrap"[^>]*>.*?<img[^>]*src=[\'"]([^\'"]+)', html, re.DOTALL)
            if img_match and "view_blank" not in img_match.group(1):
                image_url = base_url + img_match.group(1)

        # Ingredients
        ingredients_list = []
        ing_block_match = re.search(r'<div class="flex_wrap">\s*<p>Ingredients.*?<p class="content">(.*?)<\/p>', html, re.DOTALL | re.IGNORECASE)
        if ing_block_match:
            ing_text = ing_block_match.group(1).strip()
            ing_text = re.sub(r'<[^>]+>', ' ', ing_text)
            
            raw_ings = ing_text.split(',')
            for raw_ing in raw_ings:
                cleaned = re.sub(r'\(.*?\)', '', raw_ing)
                cleaned = cleaned.strip('.\r\n\t* ')
                if cleaned and len(cleaned) < 50:
                    ingredients_list.append(cleaned.title())
                    
        if not ingredients_list:
            ingredients_list = ["Water", "Glycerin", "Unknown"]

        new_products.append({
            "id": f"local_frudia_{code}",
            "barcode": f"frudia_{code}",
            "name": name,
            "brand": "FRUDIA",
            "category": "Skincare",
            "imageUrl": image_url,
            "ingredientNames": ingredients_list,
            "quantity": quantity if quantity else "50ml",
            "veganStatus": "unknown"
        })
    except Exception as e:
        print(f"Error parsing product {code}: {e}")

print(f"Extracted {len(new_products)} products.")

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
    
    if match:
        text = text.replace(match.group(0), full_array)
    else:
        text = text + "\n" + full_array

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Appended {len(new_products)} Frudia products.")
except Exception as e:
    print(f"Error modifying js file: {e}")
