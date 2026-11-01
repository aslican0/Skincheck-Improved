import os
import sqlite3
import json
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image
import io
import excel_manager

def load_env_file():
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"\''))
        except Exception as e:
            print("Warning: Could not read .env file:", e)

load_env_file()

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

DB_PATH = 'database.db'

# Configure Gemini (you can set GEMINI_API_KEY environment variable or .env file)
# If not set, AI features will gracefully return clear informative messages
API_KEY = os.environ.get("GEMINI_API_KEY", "")
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        print("Gemini API configure warning:", e)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            barcode TEXT,
            name TEXT,
            brand TEXT,
            category TEXT,
            imageUrl TEXT,
            ingredientNames TEXT,
            quantity TEXT,
            veganStatus TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            skinProfile TEXT,
            routine TEXT,
            routineSettings TEXT,
            streak INTEGER DEFAULT 0,
            starSeries TEXT,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    try:
        cols = [r[1] for r in c.execute('PRAGMA table_info(users)').fetchall()]
        if 'streak' not in cols:
            c.execute('ALTER TABLE users ADD COLUMN streak INTEGER DEFAULT 0')
        if 'starSeries' not in cols:
            c.execute('ALTER TABLE users ADD COLUMN starSeries TEXT')
    except Exception as e:
        print("Column check info:", e)

    c.execute('''
        CREATE TABLE IF NOT EXISTS user_inputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            name TEXT,
            skin_type TEXT,
            skin_problems TEXT,
            concerns TEXT,
            routine_frequency TEXT,
            products_list TEXT,
            quiz_answers TEXT,
            weekly_schedule TEXT,
            raw_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed products catalog if empty
    c.execute('SELECT COUNT(*) FROM products')
    if c.fetchone()[0] == 0:
        seed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'products_seed.json')
        if os.path.exists(seed_path):
            try:
                with open(seed_path, 'r', encoding='utf-8') as f:
                    seed_prods = json.load(f)
                for p in seed_prods:
                    ing = p.get('ingredientNames', '')
                    if isinstance(ing, list):
                        ing = ", ".join(ing)
                    c.execute('''
                        INSERT OR IGNORE INTO products (id, barcode, name, brand, category, imageUrl, ingredientNames, quantity, veganStatus)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        p.get('id'), p.get('barcode', ''), p.get('name', ''), p.get('brand', ''),
                        p.get('category', ''), p.get('imageUrl', ''), ing,
                        p.get('quantity', ''), p.get('veganStatus', 'unknown')
                    ))
                print(f"Database seeded with {len(seed_prods)} products from products_seed.json.")
            except Exception as e:
                print("Error seeding products from products_seed.json:", e)

    conn.commit()
    conn.close()

    try:
        excel_manager.sync_excel_and_db(DB_PATH)
    except Exception as e:
        print("Initial Excel-DB Sync Error:", e)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    rows = c.fetchall()
    conn.close()
    
    products = []
    for row in rows:
        p = dict(row)
        if p['ingredientNames']:
            p['ingredientNames'] = [i.strip() for i in p['ingredientNames'].split(',')]
        else:
            p['ingredientNames'] = []
        products.append(p)
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        ingredients_str = ""
        if isinstance(data.get('ingredientNames'), list):
            ingredients_str = ", ".join(data.get('ingredientNames'))
        else:
            ingredients_str = data.get('ingredientNames', '')

        product_id = data.get('id')
        if not product_id:
            import uuid
            product_id = str(uuid.uuid4())

        c.execute('''
            INSERT INTO products (id, barcode, name, brand, category, imageUrl, ingredientNames, quantity, veganStatus)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_id,
            data.get('barcode', ''),
            data.get('name', ''),
            data.get('brand', ''),
            data.get('category', ''),
            data.get('imageUrl', ''),
            ingredients_str,
            data.get('quantity', ''),
            data.get('veganStatus', 'unknown')
        ))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "id": product_id, "message": "Product added successfully."}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"}), 400
    
    if not API_KEY:
        return jsonify({
            "success": False, 
            "error": "Gemini API anahtarı (GEMINI_API_KEY) tanımlı değil. Bu özelliği kullanmak için ortam değişkenini veya .env dosyasını ayarlayın. Uygulamanın diğer tüm özellikleri çalışmaya devam etmektedir."
        }), 200

    file = request.files['image']
    try:
        image_data = file.read()
        img = Image.open(io.BytesIO(image_data))
        
        # Use Gemini 1.5 Pro or Flash for image analysis
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = """
        You are an expert cosmetic chemistry analyzer. 
        Analyze this image of a cosmetic/skincare product.
        Extract the following information and output ONLY a valid JSON object without any markdown tags or extra text:
        {
          "brand": "Extracted Brand Name (if visible, else empty)",
          "name": "Extracted Product Name (if visible, else empty)",
          "ingredients": "Comma separated INCI ingredients list (e.g., Aqua, Glycerin, Niacinamide...)"
        }
        Do not hallucinate. If you can't read an ingredient perfectly, do your best to write the standard INCI name.
        """
        response = model.generate_content([prompt, img])
        result_text = response.text.strip()
        
        # Strip markdown if model returned it despite instructions
        if result_text.startswith('```json'):
            result_text = result_text[7:]
        if result_text.endswith('```'):
            result_text = result_text[:-3]
            
        data = json.loads(result_text)
        
        return jsonify({"success": True, "data": data})
    except Exception as e:
        print("AI Error:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate_text():
    data = request.json
    text = data.get('text')
    target_lang = data.get('target_lang')
    
    if not text or not target_lang:
        return jsonify({"success": False, "error": "Missing text or target_lang"}), 400
        
    if not API_KEY:
        # Fallback if no API key
        return jsonify({"success": True, "translated": text})
        
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Translate the following cosmetic/skincare product information to {target_lang}. Only return the translated text without markdown.\n\nText: {text}"
        response = model.generate_content(prompt)
        return jsonify({"success": True, "translated": response.text.strip()})
    except Exception as e:
        print("Translation Error:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chat-analyze', methods=['POST'])
def chat_analyze():
    data = request.json
    message = data.get('message')
    
    if not message:
        return jsonify({"success": False, "error": "Lütfen analiz edilecek bir içerik mesajı gönderin."}), 400
        
    if not API_KEY:
        mock_response = """
*(Uyarı: Sistemde Gemini API anahtarı ayarlanmadığı için bu örnek bir test yanıtıdır. Gerçek yapay zeka analizi için lütfen server.py dosyasına API anahtarınızı ekleyin.)*

### 🔬 İçerik Analiz Raporu

- **✨ Cilde Faydaları ve Riskler:** Girdiğiniz formülasyondaki bileşenler genel olarak cilt bariyerini destekleyici ve nemlendirici özelliktedir. Zararlı/toksik madde tespit edilmemiştir, güvenle kullanılabilir.
- **⚠️ Komedon (Sivilce) Riski:** İçeriklerde gözenek tıkama (komedojenik) riski yüksek ağır yağlar bulunmuyor. Komedon riski **düşüktür**.
- **🎯 Uygun Cilt Tipi:** Formül su bazlı ve yatıştırıcı içeriklere sahip olduğu için özellikle **Karma ve Yağlı** ciltlerin seveceği, aynı zamanda **Hassas** ciltlerin tolere edebileceği bir yapıdadır.
- **💎 Fiyat / Performans Değerlendirmesi:** İçeriğindeki hyalüronik asit ve bitkisel ekstreler göz önüne alındığında, eğer ürün piyasa ortalamasında bir fiyata sahipse **kesinlikle fiyat/performans ürünüdür**. Formül oldukça başarılı ve temiz.
"""
        return jsonify({"success": True, "response": mock_response.strip()})
        
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Sen uzman bir dermatolog ve kozmetik formülatörüsün. Kullanıcı sana bir kozmetik ürünün içerik listesini (veya onunla ilgili bir mesaj) gönderdi:
        "{message}"
        
        Lütfen bu içerikleri detaylıca incele ve doğrudan bir sohbet (chat) samimiyetinde şu 4 ana başlığı kapsayacak şekilde yanıt ver:
        
        ### 🔬 İçerik Analiz Raporu
        - **✨ Cilde Faydaları ve Riskler:** (Değerlendirmen...)
        - **⚠️ Komedon (Sivilce) Riski:** (Değerlendirmen...)
        - **🎯 Uygun Cilt Tipi:** (Değerlendirmen...)
        - **💎 Fiyat / Performans Değerlendirmesi:** (Değerlendirmen...)

        Yanıtını yukarıdaki gibi madde işaretli (bullet point) Markdown listesi formatında, çok uzun tutmadan ama tatmin edici detayda, anlaşılır ve şık bir şekilde ver. Sadece bu listeyi ve gerekiyorsa ufak bir kapanış/açılış cümlesini döndür.
        """
        response = model.generate_content(prompt)
        return jsonify({"success": True, "response": response.text.strip()})
    except Exception as e:
        print("Chat Analysis Error:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()
    name = (data.get('name') or '').strip()

    if not email or not password or not name:
        return jsonify({"success": False, "error": "İsim, e-posta ve şifre gereklidir."}), 400

    # Ensure sync first
    try:
        excel_manager.sync_excel_and_db(DB_PATH)
    except:
        pass

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE LOWER(email) = ?', (email,))
    existing = c.fetchone()
    conn.close()

    excel_users = excel_manager.get_all_users_from_excel()
    if existing or email in excel_users:
        return jsonify({"success": False, "error": "Bu e-posta adresi zaten kayıtlı."}), 400

    skin_profile = data.get('skinProfile') or {}
    routine = data.get('routine') or {}
    settings = data.get('routineSettings') or {}
    streak = data.get('streak', 0)
    star_series = skin_profile.get('starSeries') or data.get('starSeries') or {}

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (id, name, email, password, skinProfile, routine, routineSettings, streak, starSeries, updatedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (
        email, name, email, password,
        json.dumps(skin_profile, ensure_ascii=False),
        json.dumps(routine, ensure_ascii=False),
        json.dumps(settings, ensure_ascii=False),
        streak,
        json.dumps(star_series, ensure_ascii=False)
    ))
    conn.commit()
    conn.close()

    # Save to Excel immediately so user info is stored on disk
    excel_payload = {
        'user': {'name': name, 'email': email, 'password': password, 'isLoggedIn': True, 'streak': streak},
        'skinProfile': skin_profile,
        'routine': routine,
        'routineSettings': settings,
        'streak': streak,
        'password': password
    }
    excel_manager.save_user_entry_to_excel(excel_payload)

    return jsonify({
        "success": True,
        "message": "Kayıt başarılı.",
        "user": {
            "name": name,
            "email": email,
            "password": password,
            "skinProfile": skin_profile,
            "routine": routine,
            "routineSettings": settings,
            "streak": streak,
            "starSeries": star_series
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()

    if not email or not password:
        return jsonify({"success": False, "error": "E-posta ve şifre gereklidir."}), 400

    # Ensure Excel and DB sync so users in Excel are recognized
    try:
        excel_manager.sync_excel_and_db(DB_PATH)
    except:
        pass

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE LOWER(email) = ?', (email,))
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"success": False, "error": "Kullanıcı bulunamadı. Lütfen kayıt olun veya bilgilerinizi kontrol edin."}), 404

    user_dict = dict(row)
    db_password = (user_dict.get('password') or '').strip()

    # If user in Excel or DB previously had no password, allow setting it now
    if not db_password:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE users SET password = ? WHERE LOWER(email) = ?', (password, email))
        conn.commit()
        conn.close()
        db_password = password

    if db_password != password:
        return jsonify({"success": False, "error": "Hatalı şifre girdiniz."}), 401

    try:
        profile = json.loads(user_dict['skinProfile'] or '{}')
    except:
        profile = {}
    try:
        routine = json.loads(user_dict['routine'] or '{}')
    except:
        routine = {}
    try:
        settings = json.loads(user_dict['routineSettings'] or '{}')
    except:
        settings = {}
    try:
        star_series = json.loads(user_dict['starSeries'] or '{}')
    except:
        star_series = {}

    streak = user_dict.get('streak', 0) or 0

    # Update last login in Excel
    excel_payload = {
        'user': {'name': user_dict['name'], 'email': email, 'password': password, 'isLoggedIn': True, 'streak': streak},
        'skinProfile': profile,
        'routine': routine,
        'routineSettings': settings,
        'streak': streak,
        'password': password
    }
    excel_manager.save_user_entry_to_excel(excel_payload)

    return jsonify({
        "success": True,
        "message": "Giriş başarılı.",
        "user": {
            "name": user_dict['name'],
            "email": user_dict['email'],
            "password": password,
            "skinProfile": profile,
            "routine": routine,
            "routineSettings": settings,
            "streak": streak,
            "starSeries": star_series
        }
    })

@app.route('/api/users', methods=['GET'])
def get_all_users():
    try:
        excel_manager.sync_excel_and_db(DB_PATH)
    except:
        pass

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    rows = c.fetchall()
    conn.close()

    result = {}
    for r in rows:
        email = (r['email'] or '').strip().lower()
        if not email or '@' not in email or email == 'misafir@skincheck.local':
            continue
        try:
            profile = json.loads(r['skinProfile'] or '{}')
        except:
            profile = {}
        try:
            routine = json.loads(r['routine'] or '{}')
        except:
            routine = {}
        try:
            settings = json.loads(r['routineSettings'] or '{}')
        except:
            settings = {}
        try:
            star_series = json.loads(r['starSeries'] or '{}')
        except:
            star_series = {}

        result[email] = {
            "name": r['name'] or 'Kullanıcı',
            "email": email,
            "password": r['password'] or '123456',
            "skinProfile": profile,
            "routine": routine,
            "routineSettings": settings,
            "streak": r['streak'] or 0,
            "starSeries": star_series,
            "updatedAt": r['updatedAt']
        }
    return jsonify({"success": True, "users": result})

@app.route('/api/save-user-inputs', methods=['POST'])
def save_user_inputs():
    try:
        data = request.json or {}
        user = data.get('user', {})
        profile = data.get('skinProfile', {})
        routine = data.get('routine', {})
        settings = data.get('routineSettings', {})

        email = user.get('email') or profile.get('email') or 'misafir@skincheck.local'
        name = user.get('name') or profile.get('name') or 'Misafir'
        skin_type = profile.get('primaryType', '')
        password = user.get('password') or data.get('password') or ''
        streak = data.get('streak') or user.get('streak') or 0
        star_series = profile.get('starSeries') or data.get('starSeries') or {}

        # Skin problems & concerns
        skin_problems = profile.get('skinProblems', []) or []
        concerns = profile.get('concerns', []) or []
        problems_str = ", ".join(skin_problems) if skin_problems else ", ".join(concerns)
        concerns_str = ", ".join(concerns)

        freq = settings.get('frequency') or profile.get('frequency') or ''
        prods = settings.get('products') or profile.get('products') or []
        prods_str = ", ".join(prods) if isinstance(prods, list) else str(prods)
        quiz_answers_str = json.dumps(profile.get('detailedAnswers', []), ensure_ascii=False)
        weekly_schedule_str = json.dumps(routine.get('schedule', []), ensure_ascii=False)

        # 1. Save to SQLite database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO user_inputs (
                email, name, skin_type, skin_problems, concerns,
                routine_frequency, products_list, quiz_answers, weekly_schedule, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            email, name, skin_type, problems_str, concerns_str,
            freq, prods_str, quiz_answers_str, weekly_schedule_str, json.dumps(data, ensure_ascii=False)
        ))

        # Also update user profile in users table if user is registered
        if email and email != 'misafir@skincheck.local':
            c.execute('''
                INSERT INTO users (id, name, email, password, skinProfile, routine, routineSettings, streak, starSeries, updatedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(email) DO UPDATE SET
                    name=excluded.name,
                    password=COALESCE(NULLIF(excluded.password, ''), users.password),
                    skinProfile=excluded.skinProfile,
                    routine=excluded.routine,
                    routineSettings=excluded.routineSettings,
                    streak=excluded.streak,
                    starSeries=excluded.starSeries,
                    updatedAt=CURRENT_TIMESTAMP
            ''', (
                email, name, email, password,
                json.dumps(profile, ensure_ascii=False),
                json.dumps(routine, ensure_ascii=False),
                json.dumps(settings, ensure_ascii=False),
                streak,
                json.dumps(star_series, ensure_ascii=False)
            ))

        conn.commit()
        conn.close()

        # 2. Save / update in Excel spreadsheet (kullanici_girisleri.xlsx)
        excel_path = excel_manager.save_user_entry_to_excel(data)

        return jsonify({
            "success": True,
            "message": "Kullanıcı bilgileri ve haftalık rutin başarıyla Excel tablosuna kaydedildi.",
            "excel_path": excel_path,
            "filename": "kullanici_girisleri.xlsx"
        })
    except Exception as e:
        print("Save User Inputs Error:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/export-excel', methods=['GET'])
def export_excel():
    try:
        excel_path = excel_manager.EXCEL_FILE_PATH
        if not os.path.exists(excel_path):
            excel_manager.sync_excel_and_db(DB_PATH)
        return send_file(
            excel_path,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="kullanici_girisleri.xlsx"
        )
    except Exception as e:
        print("Export Excel Error:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/user-data', methods=['GET'])
def get_user_data():
    email = request.args.get('email', '').strip().lower()
    if not email:
        return jsonify({"success": False, "error": "Email parameter required"}), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE LOWER(email) = ?', (email,))
        row = c.fetchone()
        conn.close()
        if not row:
            # Fallback check Excel
            x_users = excel_manager.get_all_users_from_excel()
            if email in x_users:
                excel_manager.sync_excel_and_db(DB_PATH)
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute('SELECT * FROM users WHERE LOWER(email) = ?', (email,))
                row = c.fetchone()
                conn.close()

        if not row:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        user_dict = dict(row)
        return jsonify({
            "success": True,
            "user": {
                "name": user_dict['name'],
                "email": user_dict['email'],
                "skinProfile": json.loads(user_dict['skinProfile'] or '{}'),
                "routine": json.loads(user_dict['routine'] or '{}'),
                "routineSettings": json.loads(user_dict['routineSettings'] or '{}'),
                "streak": user_dict.get('streak', 0) or 0,
                "starSeries": json.loads(user_dict.get('starSeries') or '{}')
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return "Not found", 404

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 8090))
    print(f"Server running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
