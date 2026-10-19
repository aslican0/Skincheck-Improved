import re

path = 'js/products.js'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

index = text.find('// ===== PRODUCT STORE')
if index != -1:
    text = text[:index]

new_block = """// ===== PRODUCT STORE (Dynamic LocalStorage) =====
const ProductStore = {
  products: [],
  VERSION: 'v103', // Increment this when we want to force a cache refresh
  async init() {
    const stored = localStorage.getItem('SKINCHECK_Products');
    const storedVersion = localStorage.getItem('SKINCHECK_Version');
    if (stored && storedVersion === this.VERSION) {
      try {
        this.products = JSON.parse(stored);
        // Always merge new SEED_PRODUCTS if they are missing
        SEED_PRODUCTS.forEach(seed => {
          const exists = this.products.some(p => p.barcode === seed.barcode || p.id === seed.id);
          if (!exists) {
            this.products.push(seed);
          }
        });
      } catch (e) {
        console.error('Failed to parse stored products', e);
        this.products = [...SEED_PRODUCTS];
      }
    } else {
      // Version mismatch or no data: Force reset
      console.log("Refreshing product database cache...");
      this.products = [...SEED_PRODUCTS];
      localStorage.setItem('SKINCHECK_Version', this.VERSION);
    }
    // Ensure all products have barcodes
    this.products.forEach(p => {
      if (!p.barcode) {
        p.barcode = 'local_' + p.name.replace(/\s+/g, '_').toLowerCase();
      }
    });
    try {
      const res = await fetch('/api/products');
      if (res.ok) {
        const dbProducts = await res.json();
        dbProducts.forEach(dbProduct => {
          const index = this.products.findIndex(p => p.id === dbProduct.id || p.barcode === dbProduct.barcode);
          if (index !== -1) {
            this.products[index] = dbProduct; // Override with db version
          } else {
            this.products.push(dbProduct);
          }
        });
      }
    } catch(err) {
      console.error("Could not fetch db products", err);
    }
    this.save();
  },

  save() {
    localStorage.setItem('SKINCHECK_Products', JSON.stringify(this.products));
  },

  getByBarcode(barcode) {
    if (!barcode) return null;
    return this.products.find(p => String(p.barcode) === String(barcode) || String(p.id) === String(barcode));
  },

  search(query) {
    if (!query) return [];
    const q = query.toLowerCase();
    return this.products.filter(p =>
      p.name.toLowerCase().includes(q) ||
      p.brand.toLowerCase().includes(q) ||
      (p.barcode && String(p.barcode).includes(q))
    );
  }
};"""

with open(path, 'w', encoding='utf-8') as f:
    f.write(text + new_block)
print("Fixed the end of file")
