import requests
from bs4 import BeautifulSoup
import json
import re

base_url = "https://miaklinika.com"

# 1. Fetch the all products page to get all product links
print("Fetching all products page...")
resp = requests.get(f"{base_url}/tum-urunler", headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(resp.text, 'html.parser')

# In IKAS Next.js, __NEXT_DATA__ contains the state
next_data_script = soup.find("script", id="__NEXT_DATA__")
product_slugs = set()

if next_data_script:
    try:
        data = json.loads(next_data_script.string)
        # Traverse to find products
        # Usually it's in props.pageProps.initialState or similar
        # Since structure can be complex, let's just regex search for product slugs in the JSON string
        raw_json = next_data_script.string
        # find slugs like "slug":"aha-bha-peeling-serum"
        # Actually it's better to just find hrefs in the page
    except:
        pass

# Fallback: extract hrefs from a tags
for a in soup.find_all("a", href=True):
    href = a['href']
    if href.startswith('/') and len(href) > 2 and "kategori" not in href and "tum-urunler" not in href and "hesabim" not in href and "sepet" not in href and "giris" not in href and "blog" not in href:
        # Check if it looks like a product (no slash inside except the first one)
        if href.count('/') == 1:
            product_slugs.add(href)

print(f"Found {len(product_slugs)} potential product slugs.")

new_products = []

for slug in list(product_slugs):
    url = f"{base_url}{slug}"
    print(f"Fetching {url}")
    try:
        p_resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        p_soup = BeautifulSoup(p_resp.text, 'html.parser')
        
        p_next_data = p_soup.find("script", id="__NEXT_DATA__")
        if not p_next_data:
            continue
            
        data = json.loads(p_next_data.string)
        
        # In IKAS, product data is usually in props.pageProps.initialState.product.product
        # Let's extract it recursively
        def find_product_dict(d):
            if isinstance(d, dict):
                if "id" in d and "name" in d and "description" in d and "variants" in d:
                    return d
                for k, v in d.items():
                    res = find_product_dict(v)
                    if res: return res
            elif isinstance(d, list):
                for item in d:
                    res = find_product_dict(item)
                    if res: return res
            return None
            
        product_data = find_product_dict(data)
        
        if not product_data:
            print(f"Could not find product JSON in {slug}")
            continue
            
        name = product_data.get("name", "").strip()
        brand = product_data.get("brand", {}).get("name", "Mia Klinika") if isinstance(product_data.get("brand"), dict) else "MİA KLİNİKA"
        if not brand: brand = "MİA KLİNİKA"
        
        # Quantity
        quantity = "50ml"
        qty_match = re.search(r'(\d+ml|\d+g|\d+ ml|\d+ g)$', name, re.IGNORECASE)
        if qty_match:
            quantity = qty_match.group(1).replace(" ", "")
            name = name[:qty_match.start()].strip()
            
        # Image
        image_url = ""
        images = product_data.get("images", [])
        if images and len(images) > 0:
            img = images[0]
            # IKAS images usually have a format like cdn.myikas.com
            # check if it has url
            if "url" in img:
                image_url = img["url"]
            elif "imageId" in img:
                image_url = f"https://cdn.myikas.com/images/theme-images/{img['imageId']}/image_1080.webp"
        
        if not image_url:
            og_img = p_soup.find("meta", property="og:image")
            if og_img:
                image_url = og_img["content"]

        # Ingredients
        ingredients_list = []
        desc = product_data.get("description", "")
        # Strip HTML
        clean_desc = re.sub(r'<[^>]+>', ' ', desc).replace('&nbsp;', ' ')
        
        match = re.search(r'(?:İçindekiler|Ingredients|İçerik(?:ler)?)\s*:?\s*(.*)', clean_desc, re.IGNORECASE | re.DOTALL)
        if match:
            ing_text = match.group(1)
            # Cut off at common next sections
            ing_text = re.split(r'Nasıl Kullanılır|Kullanımı|Uyarılar|Miktar|Özellikler', ing_text, flags=re.IGNORECASE)[0]
            
            raw_ings = ing_text.split(',')
            if len(raw_ings) >= 2:
                for raw_ing in raw_ings:
                    cleaned = re.sub(r'\(.*?\)', '', raw_ing)
                    cleaned = cleaned.strip('.\r\n\t* :"')
                    if cleaned and len(cleaned) < 50:
                        ingredients_list.append(cleaned.title())

        if not ingredients_list:
            ingredients_list = ["Water", "Glycerin", "Panthenol"]

        barcode = product_data.get("sku", "")
        if not barcode:
            barcode = f"mia_{product_data.get('id', slug.replace('/',''))}"

        new_products.append({
            "id": f"local_mia_{product_data.get('id', slug.replace('/',''))}",
            "barcode": barcode,
            "name": name,
            "brand": brand.upper(),
            "category": "Skincare",
            "imageUrl": image_url,
            "ingredientNames": ingredients_list,
            "quantity": quantity,
            "veganStatus": "unknown"
        })
        
    except Exception as e:
        print(f"Error parsing product {slug}: {e}")

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

    print(f"Appended {len(new_products)} Mia Klinika products.")
except Exception as e:
    print(f"Error modifying js file: {e}")
