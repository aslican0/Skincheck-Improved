import os
import sqlite3
import json
import re
import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from bs4 import BeautifulSoup
import uuid

BASE_URL = 'https://www.anyong.com.tr'
PRODUCTS_URL = 'https://www.anyong.com.tr/tum-urunler'
DB_PATH = os.path.join(os.getcwd(), 'database.db')

def fetch_html(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        return html
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_ingredients(soup, text_content):
    # 1. Try to find by header
    for header in soup.find_all(['h2', 'h3', 'h4', 'strong', 'p', 'div']):
        text = header.get_text(separator=' ', strip=True)
        if 'İçerik' in text or 'İçindekiler' in text or 'Ingredients' in text:
            sib = header.find_next_sibling(['p', 'div'])
            if sib:
                s_text = sib.get_text(separator=' ', strip=True)
                if ',' in s_text and len(s_text) > 20:
                    return parse_ingredients(s_text)
            
            if 'Aqua,' in text or 'Water,' in text:
                return parse_ingredients(text)

    # 2. Try to find anywhere by INC pattern (Aqua, Glycerin...)
    best_candidate = ""
    for el in soup.find_all(['p', 'div', 'span']):
        txt = el.get_text(separator=' ', strip=True)
        if ('Aqua,' in txt or 'Water,' in txt) and txt.count(',') > 4:
            if len(txt) > len(best_candidate):
                best_candidate = txt
    
    if best_candidate:
        return parse_ingredients(best_candidate)
        
    return []

def parse_ingredients(text):
    text = re.sub(r'(?i)^(i̇çerik|içerik|içindekiler|ingredients)[\s:]*', '', text)
    parts = [p.strip().strip('.') for p in text.split(',') if len(p.strip()) > 1]
    return parts

def scrape_anyong():
    print("Fetching homepage / tum-urunler to find product links...")
    html = fetch_html(PRODUCTS_URL)
    if not html:
        html = fetch_html(BASE_URL)
        
    if not html:
        print("Could not fetch the site.")
        return

    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/urun/' in href:
            if href.startswith('/'):
                href = BASE_URL + href
            elif not href.startswith('http'):
                href = BASE_URL + '/' + href
            links.add(href)
            
    print(f"Found {len(links)} product links. Scraping...")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        barcode TEXT,
        name TEXT,
        brand TEXT,
        category TEXT,
        imageUrl TEXT,
        ingredientNames TEXT,
        quantity TEXT,
        veganStatus TEXT
    )''')
    
    added_count = 0
    
    for url in links:
        print(f"Scraping: {url}")
        p_html = fetch_html(url)
        if not p_html:
            continue
            
        p_soup = BeautifulSoup(p_html, 'html.parser')
        
        title_el = p_soup.find('h1')
        if not title_el:
            continue
        name = title_el.get_text().strip()
        
        ingredients = extract_ingredients(p_soup, p_html)
        
        img_url = ""
        img_el = p_soup.find('meta', property='og:image')
        if img_el:
            img_url = img_el.get('content', '')
            
        if not ingredients:
            print(f"  -> WARNING: No ingredients found for {name}")
            
        p_id = 'anyong_' + str(uuid.uuid4())[:8]
        barcode = 'anyong_' + name.replace(' ', '_').lower()[:20]
        # Store as comma separated string or json string, server expects comma separated string in POST or JSON string if modified
        # server.py reads: p['ingredientNames'] = [i.strip() for i in p['ingredientNames'].split(',')] 
        # so it must be a comma separated string
        ing_str = ", ".join(ingredients)
        
        c.execute("SELECT id FROM products WHERE name = ?", (name,))
        if c.fetchone():
            print(f"  -> {name} already in DB. Skipping.")
            continue
            
        c.execute('''
            INSERT INTO products (id, barcode, name, brand, category, imageUrl, ingredientNames, quantity, veganStatus)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (p_id, barcode, name, 'ANYONG', 'skincare', img_url, ing_str, '50ml', 'unknown'))
        
        added_count += 1
        print(f"  -> Added {name} with {len(ingredients)} ingredients.")
        
    conn.commit()
    conn.close()
    
    print(f"Scraping finished. Added {added_count} products.")

if __name__ == '__main__':
    scrape_anyong()
