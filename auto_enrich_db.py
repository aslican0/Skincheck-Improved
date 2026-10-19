import re
import json

file_prod = "c:/Users/hasli/OneDrive/Masaüstü/FinalProject/js/products.js"
file_db = "c:/Users/hasli/OneDrive/Masaüstü/FinalProject/js/database.js"

with open(file_prod, 'r', encoding='utf-8') as f:
    prod_data = f.read()

# Extract all ingredients
ing_pattern = re.compile(r"ingredientNames:\s*\[(.*?)\]", re.DOTALL)
matches = ing_pattern.findall(prod_data)
all_ingredients = set()
for match in matches:
    # clean quotes
    items = re.findall(r"'([^']+)'|\"([^\"]+)\"", match)
    for i in items:
        val = i[0] if i[0] else i[1]
        all_ingredients.add(val.lower().strip())

with open(file_db, 'r', encoding='utf-8') as f:
    db_data = f.read()

# Find existing ingredients
existing_ing_pattern = re.compile(r"'([^']+)':\s*\{\s*safetyx?:")
# We can just look at the keys of ingredientDB
existing_keys = set(re.findall(r"\'?([a-zA-Z0-9\-\s/]+)\'?\s*:\s*\{\s*safety:", db_data))

missing = all_ingredients - set([x.lower() for x in existing_keys])

new_db_entries = []
new_meta_entries = []

for ing in missing:
    safe = 'safe'
    como = 0
    bnf = False
    func = 'Cosmetic Ingredient'
    prem = False
    
    if 'sulfate' in ing or 'parfum' in ing or 'fragrance' in ing or 'alcohol denat' in ing:
        safe = 'caution'
    if 'oil' in ing:
        como = 3
        func = 'Emollient / Oil'
    if 'butter' in ing:
        como = 0
        func = 'Emollient'
    if 'ceramide' in ing or 'peptide' in ing or 'hyaluro' in ing or 'panthenol' in ing or 'niacinamide' in ing or 'extract' in ing or 'ascorb' in ing or 'arbutin' in ing:
        bnf = True
    if 'ceramide' in ing or 'peptide' in ing or 'ascorb' in ing:
        prem = True
        
    if 'extract' in ing:
        func = 'Botanical Extract'
    elif 'peptide' in ing:
        func = 'Anti-aging Peptide'
    elif 'acid' in ing:
        if 'hyaluronic' in ing:
            func = 'Humectant'
        elif 'glycolic' in ing or 'lactic' in ing or 'salicylic' in ing or 'malic' in ing or 'tartaric' in ing:
            func = 'Exfoliant'
        elif 'ascorbic' in ing:
            func = 'Antioxidant'
        else:
            func = 'Acid / Formulator'
            
    desc_tr = f"{ing.title()} — Bu formülde kullanılan fonksiyonel bileşen ({func})."
    desc_en = f"{ing.title()} — Functional ingredient used in this formula ({func})."
    
    entry = f"    '{ing}': {{ safety: '{safe}', comedogenic: {como}, function: '{func}', beneficial: {'true' if bnf else 'false'}, desc_tr: '{desc_tr}', desc_en: '{desc_en}' }}"
    new_db_entries.append(entry)
    
    if bnf:
        meta = f"    '{ing}': {{ skinTypes: ['all'], avoidSkin: [], timeOfDay: 'AM/PM', frequency: 'Daily', premium: {'true' if prem else 'false'} }}"
        new_meta_entries.append(meta)

# Inject into database.js
# We need to find the end of ingredientDB and ingredientMeta
db_lines = db_data.split('\n')

db_new = []
in_db = False
in_meta = False

added_db = False
added_meta = False

for line in db_lines:
    if "ingredientDB: {" in line:
        in_db = True
    elif in_db and "}," in line and "ingredientMeta:" in db_data[db_data.find(line):]:
        # end of ingredientDB
        if not added_db:
            db_new.append(",\n".join(new_db_entries) + ",")
            added_db = True
        in_db = False
        
    if "ingredientMeta: {" in line:
        in_meta = True
    elif in_meta and "}," in line and "expensiveBrands:" in db_data[db_data.find(line):]:
        if not added_meta:
            db_new.append(",\n".join(new_meta_entries) + ",")
            added_meta = True
        in_meta = False
        
    db_new.append(line)

with open(file_db, 'w', encoding='utf-8') as f:
    f.write('\n'.join(db_new))

print(f"Added {len(new_db_entries)} missing ingredients to DB.")
