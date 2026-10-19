import re

frudia_products = [
    {
        "id": "local_frudia_2604280001",
        "barcode": "frudia_2604280001",
        "name": "Hydra Recharge Blueberry Hyaluronic Toner",
        "brand": "FRUDIA",
        "category": "Skincare",
        "imageUrl": "https://www.frudia.com/admin/data/product2/2604280001_M1.jpg",
        "ingredientNames": ["Water(Aqua)", "Glycerin", "Butylene Glycol", "Tripropylene Glycol", "1,2-Hexanediol", "Centella Asiatica Leaf Vesicles", "Polyglyceryl-10 Laurate", "Betaine", "Panthenol", "Sodium Citrate", "Xanthan Gum", "Sodium Hyaluronate"],
        "quantity": "500ml",
        "veganStatus": "vegan"
    },
    {
        "id": "local_frudia_2604210001",
        "barcode": "frudia_2604210001",
        "name": "Blurry Butter Jam - Lip&Cheek",
        "brand": "FRUDIA",
        "category": "Makeup",
        "imageUrl": "https://www.frudia.com/admin/data/product2/2604210001_M1.jpg",
        "ingredientNames": ["Dimethicone", "Silica", "Glycerin", "Titanium Dioxide", "Shea Butter"],
        "quantity": "10g",
        "veganStatus": "unknown"
    },
    {
        "id": "local_frudia_2602060001",
        "barcode": "frudia_2602060001",
        "name": "Citrus Brightening Toning Pad",
        "brand": "FRUDIA",
        "category": "Skincare",
        "imageUrl": "https://www.frudia.com/admin/data/product2/2602060001_M1.jpg",
        "ingredientNames": ["Citrus Unshiu Peel Extract", "Water", "Glycerin", "Niacinamide", "1,2-Hexanediol", "Panthenol", "Citric Acid", "Ascorbic Acid"],
        "quantity": "70ea",
        "veganStatus": "vegan"
    },
    {
        "id": "local_frudia_2601150001",
        "barcode": "frudia_2601150001",
        "name": "Green Grape Sebum Control Cooling",
        "brand": "FRUDIA",
        "category": "Skincare",
        "imageUrl": "https://www.frudia.com/admin/data/product2/2601150001_M1.jpg",
        "ingredientNames": ["Vitis Vinifera (Grape) Fruit Extract", "Water", "Methylpropanediol", "Glycerin", "1,2-Hexanediol", "Silica", "Panthenol", "Salicylic Acid"],
        "quantity": "50ml",
        "veganStatus": "vegan"
    },
    {
        "id": "local_frudia_2510150001",
        "barcode": "frudia_2510150001",
        "name": "What′s Wrong? Help AC Clear Pad",
        "brand": "FRUDIA",
        "category": "Skincare",
        "imageUrl": "https://www.frudia.com/admin/data/product2/2510150001_M1.jpg",
        "ingredientNames": ["Water", "Glycerin", "Butylene Glycol", "Salix Alba (Willow) Bark Extract", "1,2-Hexanediol", "Panthenol", "Allantoin", "Salicylic Acid"],
        "quantity": "70ea",
        "veganStatus": "unknown"
    },
    {
        "id": "local_frudia_2507230001",
        "barcode": "frudia_2507230001",
        "name": "Glow Juicy Jam - Lip&Cheek",
        "brand": "FRUDIA",
        "category": "Makeup",
        "imageUrl": "https://www.frudia.com/admin/data/product2/2507230001_M1.jpg",
        "ingredientNames": ["Dimethicone", "Water", "Glycerin", "Titanium Dioxide", "Shea Butter", "Fruit Extract"],
        "quantity": "10g",
        "veganStatus": "unknown"
    },
    {
        "id": "local_frudia_2501080001",
        "barcode": "frudia_2501080001",
        "name": "Citrus Brightening Vitamin C Ampoule",
        "brand": "FRUDIA",
        "category": "Skincare",
        "imageUrl": "https://www.frudia.com/admin/data/product2/2501080001_M1.jpg",
        "ingredientNames": ["Citrus Unshiu Peel Extract", "Water", "Glycerin", "Niacinamide", "1,2-Hexanediol", "Panthenol", "Ascorbic Acid", "Sodium Hyaluronate"],
        "quantity": "30ml",
        "veganStatus": "vegan"
    },
    {
        "id": "local_frudia_2409100001",
        "barcode": "frudia_2409100001",
        "name": "Re:proust UV Defense Leports Sun",
        "brand": "FRUDIA",
        "category": "Skincare",
        "imageUrl": "https://www.frudia.com/admin/data/product2/2409100001_M1.jpg",
        "ingredientNames": ["Water", "Zinc Oxide", "Titanium Dioxide", "Glycerin", "Butylene Glycol", "1,2-Hexanediol", "Niacinamide", "Panthenol", "Centella Asiatica Extract"],
        "quantity": "50g",
        "veganStatus": "vegan"
    },
    {
        "id": "local_frudia_2407250001",
        "barcode": "frudia_2407250001",
        "name": "Bare Skin Foundation Free Sun",
        "brand": "FRUDIA",
        "category": "Skincare",
        "imageUrl": "https://www.frudia.com/admin/data/product2/2407250001_M1.jpg",
        "ingredientNames": ["Water", "Zinc Oxide", "Titanium Dioxide", "Glycerin", "Butylene Glycol", "1,2-Hexanediol", "Niacinamide", "Iron Oxides", "Panthenol"],
        "quantity": "50g",
        "veganStatus": "unknown"
    },
    {
        "id": "local_frudia_2407040001",
        "barcode": "frudia_2407040001",
        "name": "Blueberry Hydrating Air Fit Sun",
        "brand": "FRUDIA",
        "category": "Skincare",
        "imageUrl": "https://www.frudia.com/admin/data/product2/2407040001_M1.jpg",
        "ingredientNames": ["Water", "Glycerin", "Butylene Glycol", "1,2-Hexanediol", "Vaccinium Angustifolium (Blueberry) Fruit Extract", "Niacinamide", "Panthenol", "Sodium Hyaluronate"],
        "quantity": "50g",
        "veganStatus": "vegan"
    }
]

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
    for idx, p in enumerate(frudia_products):
        added_content += "  {\n"
        for key, value in p.items():
            if isinstance(value, str):
                added_content += f"    {key}: '{value.replace(chr(39), chr(39)+chr(39))}',\n"
            elif isinstance(value, list):
                items = ", ".join([f"'{i.replace(chr(39), chr(39)+chr(39))}'" for i in value])
                added_content += f"    {key}: [{items}],\n"
        added_content += "  }"
        if idx < len(frudia_products) - 1:
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

    print(f"Appended {len(frudia_products)} Frudia products.")
except Exception as e:
    print(f"Error modifying js file: {e}")
