import re

path = r'c:\Users\hasli\OneDrive\Masaüstü\FinalProject\js\products.js'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to find the mistakenly replaced string:
# It looks like:
# ingredientNames: found.ingredientNames || found.ingredients || [,
#   { ... }
# ],

# The block that was inserted starts with "  {\n    id: 'dermabien" or similar and ends with "]," right before "      quantity: found.quantity || '',"
# Let's locate the split point
split_start = content.find("ingredientNames: found.ingredientNames || found.ingredients || [,")
split_end = content.find("],\n      quantity: found.quantity || '',")

if split_start != -1 and split_end != -1:
    print("Found the corrupted block.")
    # The corrupted array insertion
    # The actual inserted block is from split_start + len("ingredientNames: found.ingredientNames || found.ingredients || [,")
    # to split_end
    
    prefix = content[:split_start]
    suffix = content[split_end + 2:] # skip "],"
    
    inserted_block = content[split_start + len("ingredientNames: found.ingredientNames || found.ingredients || [,"):split_end]
    
    # We need to find where SEED_PRODUCTS ends.
    # It ends with:
    #   }
    # ];
    # But wait, did the script overwrite the ]; of SEED_PRODUCTS?
    # No, the bug happened because the script did a string replace of "]," to insert products.
    # But wait, SEED_PRODUCTS doesn't end with ], it ends with } ];
    # Wait, if the script replaced "]," maybe it searched for "],"
    
    # Let's restore the broken function first
    fixed_function = "ingredientNames: found.ingredientNames || found.ingredients || []," + suffix
    
    # Now let's fix SEED_PRODUCTS
    # we need to insert `inserted_block` at the end of SEED_PRODUCTS.
    # Where is SEED_PRODUCTS?
    seed_end = prefix.find("  }\n];\n\n// ===== PRODUCT STORE")
    if seed_end != -1:
        new_prefix = prefix[:seed_end + 4] + ",\n" + inserted_block.strip() + "\n];\n\n// ===== PRODUCT STORE" + prefix[seed_end + 32:]
    else:
        # try another pattern
        seed_end = prefix.rfind("  }\n];")
        if seed_end != -1:
            new_prefix = prefix[:seed_end + 3] + "," + inserted_block + "\n];" + prefix[seed_end + 6:]
        else:
            print("Could not find SEED_PRODUCTS end.")
            exit(1)
            
    final_content = new_prefix + fixed_function
    with open(path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print("Fixed!")
else:
    print("Could not find the corrupted block markers.")
