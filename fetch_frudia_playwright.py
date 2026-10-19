from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import json
import traceback

base_url = "https://www.frudia.com"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(20000)
        
        product_codes = set()
        pages_to_check = [
            "/en/product/product01.php",
            "/en/product/product02.php",
            "/en/product/product06.php",
            "/en/product/product07.php",
        ]

        for base_page in pages_to_check:
            for page_num in range(1, 4):
                url = f"{base_url}{base_page}?page={page_num}"
                print(f"Checking {url}")
                try:
                    page.goto(url)
                    page.wait_for_load_state("domcontentloaded", timeout=15000)
                    html = page.content()
                    
                    links = re.findall(r'href=[\'"]([^\'"]+ptype=view[^\'"]+prdcode=([0-9a-zA-Z]+)[^\'"]*)[\'"]', html)
                    added_any = False
                    for full_href, prdcode in links:
                        if prdcode not in product_codes:
                            product_codes.add(prdcode)
                            added_any = True
                            
                    if not added_any:
                        break
                except Exception as e:
                    print(f"Error fetching page {url}: {e}")
                    break

        print(f"Found {len(product_codes)} unique products.")

        new_products = []
        count = 0
        for code in product_codes:
            count += 1
            url = f"{base_url}/en/product/product01.php?ptype=view&prdcode={code}"
            print(f"Fetching {count}/{len(product_codes)}: {url}")
            try:
                page.goto(url)
                page.wait_for_load_state("domcontentloaded", timeout=15000)
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                
                title_tag = soup.find("p", class_="ko_tit")
                if not title_tag:
                    title_tag = soup.find("p", class_="pro_stitle")
                if not title_tag:
                    continue
                    
                full_name = title_tag.get_text(strip=True)
                name = re.sub(r'\(.*?\)', '', full_name).strip()
                
                quantity = ""
                qty_match = re.search(r'(\d+ml|\d+g|\d+ ml|\d+ g)$', name, re.IGNORECASE)
                if qty_match:
                    quantity = qty_match.group(1).replace(" ", "")
                    name = name[:qty_match.start()].strip()
                    
                if not quantity:
                    ml_div = soup.find("div", class_="ml")
                    if ml_div:
                        for p_tag in ml_div.find_all("p"):
                            if "ml" in p_tag.text.lower() or "g" in p_tag.text.lower():
                                quantity = p_tag.text.strip()
                                break
                
                image_url = ""
                img_wrap = soup.find("div", class_="img_wrap")
                if img_wrap:
                    img_tag = img_wrap.find("img")
                    if img_tag and "style" in img_tag.attrs:
                        style = img_tag["style"]
                        match = re.search(r"url\(['\"]?(/admin/data/product2/.*?)['\"]?\)", style)
                        if match:
                            image_url = base_url + match.group(1)
                    elif img_tag and img_tag.get("src") and not "view_blank" in img_tag.get("src"):
                        image_url = base_url + img_tag.get("src")

                ingredients_list = []
                content_ps = soup.find_all("p", class_="content")
                ing_text = ""
                for p_tag in content_ps:
                    prev = p_tag.find_previous_sibling("div", class_="flex_wrap")
                    if prev and "ingredients" in prev.get_text(strip=True).lower():
                        ing_text = p_tag.get_text(" ", strip=True)
                        break
                        
                if ing_text:
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
                
        browser.close()

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

            existing_items = re.findall(r'id:\s*[\'"]local_frudia_([a-zA-Z0-9]+)[\'"]', existing_content)
            added_codes = set(existing_items)

            added_content = ""
            appended_count = 0
            for p in new_products:
                p_code = p["id"].replace("local_frudia_", "")
                if p_code in added_codes:
                    continue
                    
                added_content += "  {\n"
                for key, value in p.items():
                    if isinstance(value, str):
                        added_content += f"    {key}: '{value.replace(chr(39), chr(39)+chr(39))}',\n"
                    elif isinstance(value, list):
                        items = ", ".join([f"'{i.replace(chr(39), chr(39)+chr(39))}'" for i in value])
                        added_content += f"    {key}: [{items}],\n"
                added_content += "  },\n"
                appended_count += 1
                
            if appended_count > 0:
                added_content = added_content.rstrip(',\n') + "\n"
                full_array = f"const SEED_PRODUCTS = [\n{existing_content},\n{added_content}];"
                
                if match:
                    text = text.replace(match.group(0), full_array)
                else:
                    text = text + "\n" + full_array

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)

            print(f"Appended {appended_count} Frudia products.")
        except Exception as e:
            print(f"Error modifying js file: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    run()
