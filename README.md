# SKINCHECK — Skincare & Cosmetic Ingredient Analyzer

SKINCHECK, kozmetik ve cilt bakım ürünlerinin içerik listelerini (INCI) analiz eden, komedojenik risk, alerjen ve tahriş edici maddeleri tespit eden, 10 dilde çok dilli destek sunan ve kişiselleştirilmiş 7 günlük cilt bakım rutini oluşturan kapsamlı bir web platformudur.

---

## 🚀 Temiz Bir Bilgisayarda Kurulum ve Başlatma

Uygulamanın herhangi bir ek kuruluma ihtiyaç duymadan temiz bir bilgisayarda çalıştırılması için aşağıdaki adımları izleyin:

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/hasli/SkinCheck.git
cd SkinCheck
```

### 2. Sanal Ortam (Virtualenv) Oluşturun (Önerilir)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Ortam Değişkenlerini Ayarlayın (İsteğe Bağlı)
Yapay zeka (AI) destekli ürün fotoğrafı tarama ve sohbet analizi için Google Gemini API anahtarı gereklidir.
Örnek yapılandırma dosyasını kopyalayın:
```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```
`.env` dosyasını açıp anahtarınızı girin:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8090
```

> **Not:** Gemini API anahtarı girilmediğinde sistem hata vermez; yapay zeka analiz ekranlarında anlaşılır bir bilgilendirme mesajı gösterilir ve uygulamanın tüm yerel analiz, ansiklopedi, rutin oluşturma, filtreleme ve kullanıcı giriş özellikleri eksiksiz çalışmaya devam eder.

### 5. Sunucuyu Başlatın
```bash
python server.py
```

İlk çalıştırmada `database.db` SQLite veritabanı otomatik olarak oluşturulur ve `products_seed.json` içerisindeki başlangıç ürün kataloğu veritabanına otomatik yüklenir.

---

## 🌐 Yerel Erişim Adresleri

Sunucu başlatıldıktan sonra tarayıcınızdan aşağıdaki adreslere erişebilirsiniz:

- **Ana Uygulama (SKINCHECK):** [http://localhost:8090](http://localhost:8090)
- **Yönetici Paneli (Admin Panel):** [http://localhost:8090/admin.html](http://localhost:8090/admin.html)
- **Arama Hata Ayıklama Testi:** [http://localhost:8090/debug_search.html](http://localhost:8090/debug_search.html)

---

## 📱 Özellikler

1. **🔬 Anlık İçerik Analizi:**
   - INCI içerik listelerini yapıştırarak veya ürün adı arayarak komedon (gözenek tıkama), mantar akneleri (malassezia), irritasyon, EWG güvenlik skoru ve cilt tipi uyumluluğunu anında analiz edin.
2. **🌐 10 Dilde Tam Destek:**
   - Türkçe, İngilizce, Almanca, Fransızca, İspanyolca, Arapça, Japonca, Korece, Çince ve Rusça.
3. **🧬 10 Soruluk Kapsamlı Cilt Tipi Testi:**
   - Cilt tipinizi (kuru, yağlı, karma, hassas, normal, akneye meyilli) tespit eder ve cilt sorunlarınıza uygun öneriler sunar.
4. **📅 7 Günlük Kişiselleştirilmiş Rutin:**
   - Sabah ve akşam rutin adımlarını oluşturur, tamamlanan adımları ve seri (streak) takibini kaydeder.
5. **👤 Kullanıcı Giriş & Profil Yönetimi:**
   - Kayıt olma, giriş yapma, şifre sıfırlama, kullanıcı verilerini yerel SQLite ve Excel tablosunda senkronize tutma.
6. **📊 Excel Dışa Aktarma:**
   - Kullanıcı rutinlerini ve verilerini `kullanici_girisleri.xlsx` formatında indirme ve inceleme.
7. **📚 İçerik Ansiklopedisi:**
   - Yüzlerce aktif kozmetik bileşenin açıklaması, fonksiyonları ve faydaları.

---

## 🛠️ Klasör Yapısı

```
FinalProject/
├── js/                        # İstemci tarafı JavaScript modülleri
│   ├── admin.js               # Admin paneli işlevleri
│   ├── analyzer.js            # İçerik analiz motoru
│   ├── app.js                 # Ana uygulama denetleyicisi
│   ├── auth.js                # Kullanıcı giriş, kayıt ve profil yönetimi
│   ├── database.js            # Ürün ve bileşen veritabanı API istemcisi
│   ├── encyclopedia.js        # İçerik ansiklopedisi mantığı
│   ├── excel-export.js        # Excel dışa aktarım tetikleyicisi
│   ├── i18n.js                # Çok dilli yerelleştirme (10 dil)
│   ├── products.js            # İstemci önbellekli ürün kataloğu
│   ├── recommender.js         # Ürün ve rutin öneri motoru
│   ├── routine.js             # Haftalık rutin ve seri (streak) takibi
│   └── skinquiz.js            # 10 soruluk cilt testi mantığı
├── styles.css                 # Modern arayüz stilleri
├── index.html                 # Ana kullanıcı arayüzü
├── admin.html                 # Admin yönetim paneli
├── debug_search.html          # Arama ve API test aracı
├── server.py                  # Flask Python arka uç sunucusu
├── excel_manager.py           # Excel ve SQLite senkronizasyon yöneticisi
├── products_seed.json         # Başlangıç ürün kataloğu seed verisi
├── requirements.txt           # Python bağımlılık listesi
├── .env.example               # Örnek ortam değişkenleri dosyası
├── .gitignore                 # Git dışlama kuralları
└── README.md                  # Proje dokümantasyonu
```

---

## 📄 Lisans
Bu proje eğitim ve araştırma amaçlı geliştirilmiştir. Ürün verileri Open Beauty Facts (ODbL) altyapısından yararlanmaktadır.
