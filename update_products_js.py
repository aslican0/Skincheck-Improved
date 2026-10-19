import sqlite3
import json
import re

def update_js():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT barcode, name, brand, category, imageUrl, ingredientNames FROM products')
    rows = c.fetchall()
    
    seeds = []
    for r in rows:
        barcode, name, brand, cat, img, ings = r
        ingredients = ings.split(', ') if ings else []
        seeds.append({
            "id": barcode,
            "barcode": barcode,
            "name": name,
            "brand": brand,
            "category": "skincare",
            "imageUrl": img or "images/products/default.jpg",
            "ingredientNames": ingredients,
            "veganStatus": "unknown",
            "vegetarianStatus": "unknown",
            "quantity": "50ml",
            "source": "api"
        })
    
    conn.close()
    
    with open('js/products.js', 'r', encoding='utf-8') as f:
        content = f.read()
        
    seed_json = json.dumps(seeds, indent=2, ensure_ascii=False)
    
    # replace const SEED_PRODUCTS = [...]; or const SEED_PRODUCTS = [];
    content = re.sub(r'const SEED_PRODUCTS\s*=\s*\[.*?\];', f'const SEED_PRODUCTS = {seed_json};', content, flags=re.DOTALL)
    
    # Bump VERSION
    content = re.sub(r"VERSION\s*=\s*'v\d+'", "VERSION = 'v102'", content)
    
    with open('js/products.js', 'w', encoding='utf-8') as f:
        f.write(content)
        
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    html = re.sub(r'\?v=21', '?v=22', html)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"Updated js/products.js with {len(seeds)} products and bumped version to v102. Updated index.html.")

if __name__ == '__main__':
    update_js()
