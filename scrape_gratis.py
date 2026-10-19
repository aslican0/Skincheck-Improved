import sqlite3
import uuid

products = [
    {"name": "Bee Beauty C Vitaminli Yüz Yıkama Jeli", "brand": "Bee Beauty", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Glycerin", "Ascorbic Acid", "Cocamidopropyl Betaine"]},
    {"name": "Bee Beauty Hyaluronik Asit Yüz Serumu", "brand": "Bee Beauty", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Hyaluronic Acid", "Panthenol", "Phenoxyethanol"]},
    {"name": "Benri Aloe Vera Jel 250 ml", "brand": "Benri", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aloe Barbadensis Leaf Juice", "Aqua", "Glycerin"]},
    {"name": "Benri Makyaj Temizleme Suyu Micellar 500 ml", "brand": "Benri", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Peg-6 Caprylic", "Glycerin", "Disodium EDTA"]},
    {"name": "Bee Beauty Kil Maskesi", "brand": "Bee Beauty", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Kaolin", "Aqua", "Glycerin", "Parfum"]},
    {"name": "Lykd Cilt Yenileyici Tonik", "brand": "Lykd", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Glycolic Acid", "Lactic Acid", "Salicylic Acid"]},
    {"name": "Bee Beauty Güneş Kremi SPF 50+", "brand": "Bee Beauty", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Octocrylene", "Ethylhexyl Methoxycinnamate", "Titanium Dioxide"]},
    {"name": "Neutrogena Hydro Boost Water Gel", "brand": "Neutrogena", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Dimethicone", "Glycerin", "Sodium Hyaluronate"]},
    {"name": "Diadermine Kırışıklık Karşıtı Gündüz Kremi", "brand": "Diadermine", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Hexanediol", "Caprylic/Capric Triglyceride", "Tocopherol"]},
    {"name": "Garnier Micellar Kusursuz Makyaj Temizleme Suyu", "brand": "Garnier", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Hexylene Glycol", "Glycerin", "Disodium Cocoamphodiacetate"]},
    {"name": "L'Oreal Paris Revitalift Lazer X3 Yaşlanma Karşıtı Gece Kremi", "brand": "L'Oreal Paris", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Dimethicone", "Simmondsia Chinensis Seed Oil", "Pro-Xylane"]},
    {"name": "Nivea Besleyici Yüz Bakım Kremi", "brand": "Nivea", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Glycerin", "Butyrospermum Parkii Butter", "Cetearyl Alcohol"]},
    {"name": "Himalaya Arındırıcı Neem Özlü Yüz Yıkama Köpüğü", "brand": "Himalaya", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Melia Azadirachta Leaf Extract", "Glycerin", "Citric Acid"]},
    {"name": "Simple Water Boost Nemlendirici Jel Krem", "brand": "Simple", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Glycerin", "Dimethicone", "Butylene Glycol"]},
    {"name": "Naturals By Watsons Argan Yüz Yağı", "brand": "Naturals", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Argania Spinosa Kernel Oil", "Tocopherol", "Parfum"]},
    {"name": "Sebamed Clear Face Kompakt", "brand": "Sebamed", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Triticum vulgare starch", "Disodium Lauryl Sulfosuccinate", "Stearic Acid"]},
    {"name": "CeraVe Nemlendiren Temizleyici", "brand": "CeraVe", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Glycerin", "Cetearyl Alcohol", "Ceramide NP"]},
    {"name": "CeraVe Nemlendirici Krem", "brand": "CeraVe", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Glycerin", "Cetearyl Alcohol", "Caprylic/Capric Triglyceride"]},
    {"name": "La Roche-Posay Effaclar Jel", "brand": "La Roche-Posay", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "Sodium Laureth Sulfate", "PEG-8", "Coco-Betaine"]},
    {"name": "Vichy Mineral 89 Nemlendirici Serum", "brand": "Vichy", "category": "skincare", "img": "images/products/default.jpg", "ingredients": ["Aqua", "PEG/PPG/Polybutylene Glycol-8/5/3 Glycerin", "Glycerin", "Sodium Hyaluronate"]}
]

def add_gratis_products():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    added_count = 0
    for p in products:
        barcode = 'gratis_' + str(uuid.uuid4())[:8]
        p_id = 'gr_prod_' + str(uuid.uuid4())[:8]
        ing_str = ", ".join(p["ingredients"])
        
        c.execute("SELECT id FROM products WHERE name = ?", (p["name"],))
        if c.fetchone():
            continue
            
        c.execute('''
            INSERT INTO products (id, barcode, name, brand, category, imageUrl, ingredientNames, quantity, veganStatus)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (p_id, barcode, p["name"], p["brand"], p["category"], p["img"], ing_str, '50ml', 'unknown'))
        
        added_count += 1
        
    conn.commit()
    conn.close()
    print(f"Added {added_count} Gratis top selling products to the database.")

if __name__ == '__main__':
    add_gratis_products()
