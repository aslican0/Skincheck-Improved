import re
import json

new_products = [
  # THE PUREST SOLUTIONS
  {
    "id": "local_purest_aha_bha", "barcode": "local_purest_aha_bha",
    "name": "AHA 10% + BHA 2% Exfoliating Facial Peeling Serum", "brand": "THE PUREST SOLUTIONS", "category": "Skincare",
    "imageUrl": "https://thepurestsolutions.com/cdn/shop/files/kirmizi-peeling-serum-aha-10-bha-2-30-ml-720894.png",
    "ingredientNames": ["Aqua", "Glycolic Acid", "Ethoxydiglycol", "Salicylic Acid", "Sodium Hydroxide", "Anthocyanins", "Phenethyl Alcohol", "Glycerin", "Xanthan Gum", "1,2-Hexanediol", "Citric Acid", "Propylene Glycol", "Sodium PCA", "Pentylene Glycol", "Lactic Acid", "Malic Acid", "Gluconic Acid", "Ascorbic Acid", "Tasmannia Lanceolata Fruit Extract", "Erythritol", "Carrageenan", "Sodium Acetylated Hyaluronate", "Sodium Hyaluronate", "Sodium Hyaluronate Crosspolymer", "Tartaric Acid", "Hydrolyzed Sodium Hyaluronate", "Ethylhexylglycerin"],
    "quantity": "30ml", "veganStatus": "vegan"
  },
  {
    "id": "local_purest_niacinamide", "barcode": "8682110072021",
    "name": "Niacinamide 5% + Zinc PCA 1% Serum", "brand": "THE PUREST SOLUTIONS", "category": "Skincare",
    "imageUrl": "https://thepurestsolutions.com/cdn/shop/products/Niacinamide-5_-Zinc-PCA-1_-30-ml.jpg",
    "ingredientNames": ["Aqua", "Niacinamide", "Pentylene Glycol", "Zinc PCA", "Glycerin", "Phenoxyethanol", "Hydroxyethylcellulose", "Ethylhexylglycerin", "Sodium Hyaluronate", "Allantoin", "Panthenol"],
    "quantity": "30ml", "veganStatus": "vegan"
  },
  # MARUDERM
  {
    "id": "local_maruderm_cy_serum", "barcode": "local_maruderm_cy_serum",
    "name": "C Vitamini ve Peptid Aydınlatıcı Cilt Bakım Serumu", "brand": "MARUDERM", "category": "Skincare",
    "imageUrl": "https://maruderm.com/cdn/shop/files/maruderm-c-vitamini-peptit-aydinlatici-cilt-bakim-serum-30-ml-318.png",
    "ingredientNames": ["Aqua", "Sodium Ascorbyl Phosphate", "Niacinamide", "Propylene Glycol", "Pisum Sativum Peptide", "Panthenol", "Arginine", "Aspartic Acid", "Glycine", "Alanine", "Serine", "Valine", "Proline", "Threonine", "Isoleucine", "Histidine", "Phenylalanine", "Hydroxyethylcellulose", "Sodium Benzoate", "Potassium Sorbate"],
    "quantity": "30ml", "veganStatus": "unknown"
  },
  {
    "id": "local_maruderm_azelaic", "barcode": "8682750691515",
    "name": "Azelaic Acid 10% Cilt Bakım Serumu", "brand": "MARUDERM", "category": "Skincare",
    "imageUrl": "https://maruderm.com/cdn/shop/products/MarudermAzelaicAcid10CiltBakimSerumu30ml.png",
    "ingredientNames": ["Aqua", "Azelaic Acid", "Glycerin", "Propylene Glycol", "Panthenol", "Salicylic Acid", "Sodium Hyaluronate", "Phenoxyethanol", "Ethylhexylglycerin", "Xanthan Gum", "Allantoin"],
    "quantity": "30ml", "veganStatus": "unknown"
  },
  # COSMED
  {
    "id": "local_cosmed_enzyme_peeling", "barcode": "local_cosmed_enzyme_peeling",
    "name": "Alight Enzyme Peeling Powder", "brand": "COSMED", "category": "Skincare",
    "imageUrl": "https://cosmed.com/cdn/shop/files/Alight-Enzyme-Peeling-Powder.jpg",
    "ingredientNames": ["Zea Mays Starch", "Sodium Cocoyl Isethionate", "Sodium Lauroyl Glutamate", "Sodium Palmitate", "Diglycerin", "Allantoin", "Maltodextrin", "Protease", "Acacia Senegal Gum", "Aqua", "Crocus Chrysanthus Bulb Extract"],
    "quantity": "75g", "veganStatus": "unknown"
  },
  {
    "id": "local_cosmed_atopia_oil", "barcode": "8698973595679",
    "name": "Atopia Temizleme Yağı (Cleansing Oil)", "brand": "COSMED", "category": "Skincare",
    "imageUrl": "https://cosmed.com/cdn/shop/products/AtopiaTemizlemeYagi.jpg",
    "ingredientNames": ["Helianthus Annuus Seed Oil", "PEG-20 Glyceryl Triisostearate", "Tocopheryl Acetate", "Parfum", "Squalane", "Ceramide NP", "Ceramide AP", "Cholesterol"],
    "quantity": "200ml", "veganStatus": "unknown"
  },
  # SINOZ
  {
    "id": "local_sinoz_cy_serum", "barcode": "local_sinoz_cy_serum",
    "name": "%10 C Vitamini Serumu", "brand": "SINOZ", "category": "Skincare",
    "imageUrl": "https://sinoz.com.tr/cdn/shop/products/sinoz-c-vitamini-serumu-c-vitamini-serumu-452.jpg",
    "ingredientNames": ["Aqua", "3-O-Ethyl Ascorbic Acid", "Butylene Glycol", "Niacinamide", "Citrus Reticulata Peel Extract", "Glycerin", "Glyceryl Acrylate/Acrylic Acid Copolymer", "Pvm/Ma Copolymer", "Caprylyl Glycol", "Propylene Glycol", "Citrus Nobilis Peel Oil", "Sodium Hyaluronate", "Ppg-26-Buteth-26", "Panthenol", "Phenoxyethanol"],
    "quantity": "30ml", "veganStatus": "unknown"
  },
  {
    "id": "local_sinoz_dark_spot", "barcode": "8682006760113",
    "name": "Leke Kremi (Dark Spot Cream)", "brand": "SINOZ", "category": "Skincare",
    "imageUrl": "https://sinoz.com.tr/cdn/shop/products/sinoz-leke-kremi.jpg",
    "ingredientNames": ["Aqua", "Cetearyl Alcohol", "Glyceryl Stearate", "Cyclopentasiloxane", "Caprylic/Capric Triglyceride", "Glycerin", "Niacinamide", "Alpha-Arbutin", "Bellis Perennis Flower Extract", "Phenoxyethanol", "Panthenol", "Sodium Ascorbyl Phosphate", "Allantoin", "Tocopheryl Acetate", "Ethylhexylglycerin", "Parfum", "Potassium Cetyl Phosphate", "Ceteareth-20"],
    "quantity": "40ml", "veganStatus": "unknown"
  },
  # DERMOSKIN
  {
    "id": "local_dermoskin_be_bright", "barcode": "local_dermoskin_be_bright",
    "name": "Be Bright Liposomal Vitamin C Complex Serum", "brand": "DERMOSKIN", "category": "Skincare",
    "imageUrl": "https://www.dermoskin.com.tr/Uploads/UrunResimleri/buyuk/dermoskin-be-bright-lipozomal-c-vitami-5f-a36.png",
    "ingredientNames": ["Aqua", "L-Ascorbic Acid", "Lecithin", "Glycerin", "Propylene Glycol", "Panthenol", "Pentylene Glycol", "Ethoxydiglycol", "Polysorbate 20", "Ferulic Acid", "Sodium Hyaluronate", "Xanthan Gum", "Phenoxyethanol", "Parfum", "Tocopherol", "Ethylhexylglycerin"],
    "quantity": "30ml", "veganStatus": "unknown"
  },
  {
    "id": "local_dermoskin_aha_bha", "barcode": "8697723010452",
    "name": "AHA/BHA Bakım Kremi", "brand": "DERMOSKIN", "category": "Skincare",
    "imageUrl": "https://www.dermoskin.com.tr/Uploads/UrunResimleri/buyuk/dermoskin-aha-bha-kremi-30-ml-7306.jpg",
    "ingredientNames": ["Aqua", "Glycolic Acid", "Cetearyl Alcohol", "Glycerin", "Salicylic Acid", "Glyceryl Stearate", "Sodium Hydroxide", "Phenoxyethanol", "Ethylhexylglycerin", "Cyclopentasiloxane", "Panthenol", "Tocopheryl Acetate", "Allantoin"],
    "quantity": "30ml", "veganStatus": "unknown"
  },
  # LUV IT!
  {
    "id": "local_luvit_niacinamide", "barcode": "local_luvit_niacinamide",
    "name": "Gözenek Sıkılaştırıcı & Aydınlatıcı Serum", "brand": "LUV IT!", "category": "Skincare",
    "imageUrl": "https://luvit.com.tr/cdn/shop/files/luvit-kategori-gorsel_2.jpg",
    "ingredientNames": ["Aqua", "Niacinamide", "Glycerin", "Hamamelis Virginiana Leaf Extract", "Allantoin", "Panthenol", "Zinc Sulfate", "Hyaluronic Acid", "Hydroxyethylcellulose", "Arginine", "Polysorbate 20", "Phenoxyethanol", "Disodium EDTA", "Ethylhexylglycerin"],
    "quantity": "30ml", "veganStatus": "unknown"
  },
  {
    "id": "local_luvit_peeling", "barcode": "8683526140021",
    "name": "AHA %10 + BHA %2 Kırmızı Peeling Serum", "brand": "LUV IT!", "category": "Skincare",
    "imageUrl": "https://luvit.com.tr/cdn/shop/products/kirmizi-peeling.jpg",
    "ingredientNames": ["Aqua", "Glycolic Acid", "Lactic Acid", "Salicylic Acid", "Propylene Glycol", "Glycerin", "Sodium Hydroxide", "Sodium Hyaluronate", "Phenoxyethanol", "Ethylhexylglycerin", "Tasmannia Lanceolata Fruit Extract", "Panthenol", "Xanthan Gum", "Sodium PCA"],
    "quantity": "30ml", "veganStatus": "unknown"
  },
  # CREAM CO.
  {
    "id": "local_creamco_sos_serum", "barcode": "local_creamco_sos_serum",
    "name": "SOS Serum", "brand": "CREAM CO.", "category": "Skincare",
    "imageUrl": "https://skincarecream.co/cdn/shop/files/SOSSERUM-2.png",
    "ingredientNames": ["Aqua", "Niacinamide", "3-0-Ethyl Ascorbic Acid", "Caprylic/Capric Triglyceride", "Glycerin", "Butylene Glycol", "Alpha-Arbutin", "Sodium Acrylates Copolymer", "Behenyl Alcohol", "Glyceryl Stearate", "Ethylhexyl Palmitate", "Lecithin", "Glycine Soja Sterols", "Tranexamic Acid", "Phenoxyethanol", "Tocopheryl Acetate", "Sodium PCA", "Panthenol", "Carbomer", "Polysorbate 20", "Palmitoyl Tripeptide-1", "Palmitoyl Tetrapeptide-7", "Ascorbyl Tetraisopalmitate", "Propanediol", "Hydrolyzed Glycosaminoglycans", "Sodium Hyaluronate", "Hydrolyzed Hyaluronic Acid", "Hyaluronic Acid", "Sodium Hyaluronate Crosspolymer", "Ethylhexylglycerin", "Squalane", "Lactic Acid", "Rosmarinus Officinalis Leaf Extract", "Corallina Officinalis Extract", "Citrus Aurantium Dulcis Peel Extract", "Arnica Montana Flower Extract", "Camellia Sinensis Leaf Extract", "Salvia Officinalis Leaf Extract", "Olea Europaea Leaf Extract", "Sodium Hydroxide", "Xanthan Gum", "Disodium EDTA"],
    "quantity": "30ml", "veganStatus": "vegan"
  },
  {
    "id": "local_creamco_moisturizer", "barcode": "8682858564024",
    "name": "Peptide Ceramide Moisturizer", "brand": "CREAM CO.", "category": "Skincare",
    "imageUrl": "https://skincarecream.co/cdn/shop/products/PeptideCeramideMoisturizer.png",
    "ingredientNames": ["Aqua", "Glycerin", "Squalane", "Niacinamide", "Panthenol", "Ceramide NP", "Sodium Hyaluronate", "Centella Asiatica Extract", "Caprylic/Capric Triglyceride", "Cetearyl Alcohol", "Stearic Acid", "Palmitoyl Tripeptide-1", "Palmitoyl Tetrapeptide-7", "Phenoxyethanol", "Ethylhexylglycerin"],
    "quantity": "50ml", "veganStatus": "vegan"
  },
  # BIONNEX
  {
    "id": "local_bionnex_preventiva", "barcode": "local_bionnex_preventiva",
    "name": "Preventiva Dry Touch Sunscreen Fluid SPF 50+", "brand": "BIONNEX", "category": "Skincare",
    "imageUrl": "https://bionnex.com/wp-content/uploads/2021/04/bionnex-preventiva-gunes-kremi.png",
    "ingredientNames": ["Aqua", "Octocrylene", "Ethylhexyl Methoxycinnamate", "C12-15 Alkyl Benzoate", "Ethylhexyl Palmitate", "Butyl Methoxydibenzoylmethane", "Zinc Oxide", "Tapioca Starch Polymethylsilsesquioxane", "Ceteareth-25", "VP/Hexadecene Copolymer", "Glycerin", "Dimethicone", "Glyceryl Stearate SE", "Cetyl Alcohol", "Titanium Dioxide", "Butylene Glycol", "Silica", "Ammonium Polyacrylate", "Cyclopentasiloxane", "PTFE", "Phenoxyethanol", "Ethylhexylglycerin", "Tocopheryl Acetate", "Acrylates/C10-30 Alkyl Acrylate Crosspolymer", "Xanthan Gum", "Disodium EDTA"],
    "quantity": "50ml", "veganStatus": "unknown"
  },
  # CERAVE
  {
    "id": "local_cerave_hydrating", "barcode": "3337875597333",
    "name": "Nemlendiren Temizleyici (Hydrating Cleanser)", "brand": "CERAVE", "category": "Skincare",
    "imageUrl": "https://www.cerave.com.tr/-/media/project/loreal/brand-sites/cerave/master/turkey/product/cleansers/hydrating-cleanser/cerave_hydrating_cleanser_236ml_front.png",
    "ingredientNames": ["Aqua", "Glycerin", "Cetearyl Alcohol", "PEG-40 Stearate", "Stearyl Alcohol", "Potassium Phosphate", "Ceramide NP", "Ceramide AP", "Ceramide EOP", "Carbomer", "Glyceryl Stearate", "Behentrimonium Methosulfate", "Sodium Lauroyl Lactylate", "Sodium Hyaluronate", "Cholesterol", "Phenoxyethanol", "Disodium EDTA", "Dipotassium Phosphate", "Tocopherol", "Phytosphingosine", "Xanthan Gum", "Cetyl Alcohol", "Polysorbate 20", "Ethylhexylglycerin"],
    "quantity": "236ml", "veganStatus": "unknown"
  },
  {
    "id": "local_cerave_moisturizing", "barcode": "3337875597388",
    "name": "Nemlendirici Krem (Moisturising Cream)", "brand": "CERAVE", "category": "Skincare",
    "imageUrl": "https://www.cerave.com.tr/-/media/project/loreal/brand-sites/cerave/master/turkey/product/moisturizers/moisturizing-cream/cerave_moisturising_cream_340g_front.png",
    "ingredientNames": ["Aqua", "Glycerin", "Cetearyl Alcohol", "Caprylic/Capric Triglyceride", "Cetyl Alcohol", "Ceteareth-20", "Petrolatum", "Dimethicone", "Phenoxyethanol", "Behentrimonium Methosulfate", "Potassium Phosphate", "Ethylhexylglycerin", "Sodium Lauroyl Lactylate", "Disodium EDTA", "Dipotassium Phosphate", "Ceramide NP", "Ceramide AP", "Phytosphingosine", "Cholesterol", "Xanthan Gum", "Carbomer", "Sodium Hyaluronate", "Tocopherol", "Ceramide EOP"],
    "quantity": "340g", "veganStatus": "unknown"
  },
  # LA ROCHE-POSAY
  {
    "id": "local_lrp_effaclar", "barcode": "3337872411083",
    "name": "Effaclar Purifying Foaming Gel", "brand": "LA ROCHE-POSAY", "category": "Skincare",
    "imageUrl": "https://www.laroche-posay.com.tr/-/media/project/loreal/brand-sites/lrp/master/tr/products/effaclar/effaclar-purifying-foaming-gel-400ml.png",
    "ingredientNames": ["Aqua", "Sodium Laureth Sulfate", "PEG-8", "Coco-Betaine", "Hexylene Glycol", "Sodium Chloride", "PEG-120 Methyl Glucose Dioleate", "Zinc PCA", "Sodium Hydroxide", "Citric Acid", "Sodium Benzoate", "Phenoxyethanol", "Caprylyl Glycol", "Parfum"],
    "quantity": "400ml", "veganStatus": "unknown"
  },
  {
    "id": "local_lrp_cicaplast", "barcode": "3337875815314",
    "name": "Cicaplast Baume B5+", "brand": "LA ROCHE-POSAY", "category": "Skincare",
    "imageUrl": "https://www.laroche-posay.com.tr/-/media/project/loreal/brand-sites/lrp/master/tr/products/cicaplast/cicaplast-baume-b5-40ml.png",
    "ingredientNames": ["Aqua", "Hydrogenated Polyisobutene", "Dimethicone", "Glycerin", "Butyrospermum Parkii Butter", "Panthenol", "Propanediol", "Butylene Glycol", "Aluminum Starch Octenylsuccinate", "Cetyl PEG/PPG-10/1 Dimethicone", "Trihydroxystearin", "Zinc Gluconate", "Madecassoside", "Manganese Gluconate", "Silica", "Aluminum Hydroxide", "Magnesium Sulfate", "Disodium EDTA", "Copper Gluconate", "Capryloyl Glycine", "Citric Acid", "Acetylated Glycol Stearate", "Polyglyceryl-4 Isostearate", "Tocopherol", "Pentaerythrityl Tetra-Di-T-Butyl Hydroxyhydrocinnamate", "CI 77891"],
    "quantity": "40ml", "veganStatus": "unknown"
  },
  # BIODERMA
  {
    "id": "local_bioderma_sensibio", "barcode": "3401345935571",
    "name": "Sensibio H2O Micellar Water", "brand": "BIODERMA", "category": "Skincare",
    "imageUrl": "https://www.bioderma.com.tr/sites/tr/files/styles/product_image/public/2021-08/Sensibio_H2O.png",
    "ingredientNames": ["Aqua", "PEG-6 Caprylic/Capric Glycerides", "Fructooligosaccharides", "Mannitol", "Xylitol", "Rhamnose", "Cucumis Sativus Fruit Extract", "Propylene Glycol", "Cetrimonium Bromide", "Disodium EDTA"],
    "quantity": "500ml", "veganStatus": "unknown"
  }
]

js_content = "const SEED_PRODUCTS = [\n"
for idx, p in enumerate(new_products):
    js_content += "  {\n"
    for key, value in p.items():
        if isinstance(value, str):
            js_content += f"    {key}: '{value}',\n"
        elif isinstance(value, list):
            items = ", ".join([f"'{i}'" for i in value])
            js_content += f"    {key}: [{items}],\n"
    js_content += "  }"
    if idx < len(new_products) - 1:
        js_content += ",\n"
    else:
        js_content += "\n"
js_content += "];"

file_path = "c:/Users/hasli/OneDrive/Masaüstü/FinalProject/js/products.js"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace the block from `const SEED_PRODUCTS = [` to `];` before `// ===== PRODUCT STORE`
text = re.sub(r'const SEED_PRODUCTS = \[.*?\];', js_content, text, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Succesfully injected 20 top products!")
