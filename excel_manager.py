import os
import datetime
import json
import sqlite3
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

EXCEL_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kullanici_girisleri.xlsx')

HEADER_FILL_ACCOUNTS = PatternFill(start_color="4834D4", end_color="4834D4", fill_type="solid") # Elegant royal purple
HEADER_FILL_PRIMARY = PatternFill(start_color="D946A8", end_color="D946A8", fill_type="solid")
HEADER_FILL_SECONDARY = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
HEADER_FILL_TERTIARY = PatternFill(start_color="16A085", end_color="16A085", fill_type="solid")

HEADER_FONT = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
REGULAR_FONT = Font(name="Segoe UI", size=10, color="2C3E50")
BOLD_FONT = Font(name="Segoe UI", size=10, bold=True, color="2C3E50")

THIN_BORDER = Border(
    left=Side(style='thin', color='E0E0E0'),
    right=Side(style='thin', color='E0E0E0'),
    top=Side(style='thin', color='E0E0E0'),
    bottom=Side(style='thin', color='E0E0E0')
)

ZEBRA_FILL = PatternFill(start_color="FDF6FB", end_color="FDF6FB", fill_type="solid")
WHITE_FILL = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

def format_sheet_headers(ws, headers, fill):
    ws.append(headers)
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = fill
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER
    ws.row_dimensions[1].height = 28
    ws.freeze_panes = "A2"

def auto_fit_columns(ws, max_widths=None):
    if max_widths is None:
        max_widths = {}
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            val = str(cell.value or '')
            if '\n' in val:
                lines = val.split('\n')
                line_max = max(len(l) for l in lines)
                max_len = max(max_len, line_max)
            else:
                max_len = max(max_len, len(val))
        cap = max_widths.get(col_letter, 50)
        ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), cap)

def save_user_entry_to_excel(data, filepath=EXCEL_FILE_PATH):
    """
    Saves and updates user information across sheets in kullanici_girisleri.xlsx:
    - Sheet 0: 'Kullanıcı Bilgileri & Hesaplar' (User accounts, credentials, streak, star series)
    - Sheet 1: 'Kullanıcı Girişleri & Sorunlar' (Skin concerns, type, scores, routine products)
    - Sheet 2: 'Haftalık Bakım Rutini (7 Gün)' (7-day morning/evening routine steps)
    - Sheet 3: 'Test Cevapları Detayı' (Answers to skin quiz)
    """
    if os.path.exists(filepath):
        try:
            wb = openpyxl.load_workbook(filepath)
        except Exception:
            wb = openpyxl.Workbook()
    else:
        wb = openpyxl.Workbook()

    # Extract user profile information
    user = data.get('user', {})
    profile = data.get('skinProfile', {})
    routine = data.get('routine', {})
    settings = data.get('routineSettings', {})
    
    timestamp_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    name = user.get('name') or profile.get('name') or 'Misafir Kullanıcı'
    email = user.get('email') or profile.get('email') or 'misafir@skincheck.local'
    password = user.get('password') or data.get('password') or ''
    is_logged_in = user.get('isLoggedIn', False) or (email and email != 'misafir@skincheck.local')
    account_type = "Kayıtlı Kullanıcı" if is_logged_in else "Misafir Kullanıcı"

    skin_type = profile.get('primaryType') or 'Belirtilmedi'
    type_labels = {
        'dry': 'Kuru Cilt',
        'oily': 'Yağlı Cilt',
        'combination': 'Karma Cilt',
        'sensitive': 'Hassas Cilt',
        'acne': 'Akneye Yatkın Cilt',
        'normal': 'Normal Cilt'
    }
    skin_type_label = type_labels.get(skin_type, skin_type.capitalize())

    # Skin Problems / Concerns
    concerns = profile.get('concerns', []) or []
    skin_problems = profile.get('skinProblems', []) or []
    if not skin_problems:
        problem_map = {
            'acne': 'Akne ve Sivilce',
            'sensitive': 'Kızarıklık ve Hassasiyet',
            'dehydrated': 'Nemsizlik ve Pullanma',
            'pores': 'Geniş Gözenekler',
            'dark_spots': 'Koyu Lekeler / Hiperpigmentasyon',
            'dull': 'Mat ve Cansız Görünüm',
            'fine_lines': 'İnce Çizgiler / Kırışıklık'
        }
        skin_problems = [problem_map.get(c, c) for c in concerns]
        if skin_type in ['acne', 'oily'] and 'Akne ve Sivilce' not in skin_problems:
            skin_problems.insert(0, 'Aşırı Sebum ve Akneye Eğilim')
        elif skin_type == 'dry' and 'Nemsizlik ve Pullanma' not in skin_problems:
            skin_problems.insert(0, 'Cilt Bariyeri Zayıflığı ve Kuruluk')
        elif skin_type == 'sensitive' and 'Kızarıklık ve Hassasiyet' not in skin_problems:
            skin_problems.insert(0, 'Hassas Reaktif Cilt Bariyeri')

    problems_str = ", ".join(skin_problems) if skin_problems else "Önemli bir problem belirtilmedi"

    # Scores
    scores = profile.get('scores', {})
    if isinstance(scores, dict) and scores:
        scores_str = ", ".join([f"{k}: {v}" for k, v in scores.items() if v > 0])
    else:
        scores_str = "-"

    # Habits & Products
    freq = settings.get('frequency') or profile.get('frequency') or 'regularly'
    habit_str = "Düzenli Cilt Bakımı Yapıyor" if freq == 'regularly' else "Temel Bakım (Yeni Başlayan)"

    products = settings.get('products') or profile.get('products') or []
    prod_count = len(products)
    products_str = ", ".join(products) if products else "Temel Adımlar (Ürün eklenmedi)"

    has_weekly = "7 Günlük Haftalık Çizelge Aktif" if (routine.get('isCustomWeekly') or routine.get('schedule')) else "Standart Günlük Liste"

    # Routine Streak (Rutin Serisi)
    streak_val = data.get('streak') or user.get('streak') or 0
    try:
        streak_val = int(streak_val)
    except:
        streak_val = 0
    streak_display = f"{streak_val} Günlük Seri 🔥" if streak_val > 0 else "0 Gün"

    # Star Series (Yıldız Serisi)
    star_series = profile.get('starSeries') or user.get('starSeries') or {}
    star_active = star_series.get('activeProduct')
    star_queue = star_series.get('waitingQueue') or []
    if star_active:
        start_date_str = star_series.get('startDate')
        days_passed = 0
        if start_date_str:
            try:
                dt = datetime.datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                days_passed = max(0, (datetime.datetime.now(datetime.timezone.utc) - dt).days)
            except:
                pass
        left_days = max(0, 14 - days_passed)
        queue_info = f" | Sırada: {len(star_queue)} ürün" if star_queue else ""
        star_display = f"Aktif: {star_active} ({days_passed}. gün, kalan: {left_days} gün){queue_info}"
    elif star_queue:
        star_display = f"Sırada: {', '.join(star_queue)}"
    else:
        star_display = "Yok"

    # ==========================================================
    # Sheet 0: Kullanıcı Bilgileri & Hesaplar (Öncelikli Sayfa)
    # ==========================================================
    sheet0_name = "Kullanıcı Bilgileri & Hesaplar"
    if sheet0_name in wb.sheetnames:
        ws0 = wb[sheet0_name]
    else:
        # Insert as first sheet
        ws0 = wb.create_sheet(title=sheet0_name, index=0)
        headers0 = [
            "Kayıt / Güncelleme Tarihi",
            "Kullanıcı Adı",
            "E-Posta",
            "Şifre / Parola",
            "Cilt Tipi",
            "Tespit Edilen Cilt Problemleri",
            "Rutin Serisi (Streak)",
            "Yıldız Serisi Durumu",
            "Rutindeki Ürün Sayısı",
            "Kullanılan Ürünler Listesi",
            "Son Giriş / İşlem",
            "Hesap Durumu"
        ]
        format_sheet_headers(ws0, headers0, HEADER_FILL_ACCOUNTS)

    # Find existing row in Sheet 0
    row0_idx = None
    existing_password = ""
    for r in range(2, ws0.max_row + 1):
        c_email = str(ws0.cell(row=r, column=3).value or '').strip().lower()
        if c_email == email.strip().lower():
            row0_idx = r
            existing_password = str(ws0.cell(row=r, column=4).value or '').strip()
            break

    if not row0_idx:
        row0_idx = ws0.max_row + 1

    final_password = password if password else (existing_password or "123456")

    row_data0 = [
        timestamp_str,
        name,
        email,
        final_password,
        skin_type_label,
        problems_str,
        streak_display,
        star_display,
        prod_count,
        products_str,
        timestamp_str,
        "Aktif"
    ]

    for c_idx, val in enumerate(row_data0, 1):
        cell = ws0.cell(row=row0_idx, column=c_idx, value=val)
        cell.font = REGULAR_FONT
        cell.border = THIN_BORDER
        cell.fill = ZEBRA_FILL if (row0_idx % 2 == 0) else WHITE_FILL
        if c_idx in [1, 4, 5, 7, 9, 11, 12]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    ws0.row_dimensions[row0_idx].height = 26

    # ==========================================================
    # Sheet 1: Kullanıcı Girişleri & Sorunlar
    # ==========================================================
    sheet1_name = "Kullanıcı Girişleri & Sorunlar"
    if sheet1_name in wb.sheetnames:
        ws1 = wb[sheet1_name]
    else:
        ws1 = wb.create_sheet(title=sheet1_name)
        headers1 = [
            "Kayıt Tarihi",
            "Kullanıcı Adı",
            "E-Posta",
            "Hesap Türü",
            "Cilt Tipi",
            "Tespit Edilen Cilt Problemleri",
            "Cilt Endişeleri (Skorlar)",
            "Bakım Alışkanlığı",
            "Rutindeki Ürün Sayısı",
            "Kullanılan Ürünler Listesi",
            "Haftalık Rutin Durumu"
        ]
        format_sheet_headers(ws1, headers1, HEADER_FILL_PRIMARY)

    user_row = None
    for r in range(2, ws1.max_row + 1):
        if str(ws1.cell(row=r, column=3).value or '').strip().lower() == email.strip().lower():
            user_row = r
            break

    if not user_row:
        user_row = ws1.max_row + 1

    row_data1 = [
        timestamp_str,
        name,
        email,
        account_type,
        skin_type_label,
        problems_str,
        scores_str,
        habit_str,
        prod_count,
        products_str,
        has_weekly
    ]

    for c_idx, val in enumerate(row_data1, 1):
        cell = ws1.cell(row=user_row, column=c_idx, value=val)
        cell.font = REGULAR_FONT
        cell.border = THIN_BORDER
        cell.fill = ZEBRA_FILL if (user_row % 2 == 0) else WHITE_FILL
        if c_idx in [1, 4, 5, 8, 9, 11]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    ws1.row_dimensions[user_row].height = 24

    # ==========================================================
    # Sheet 2: Haftalık Bakım Rutini (7 Günlük Çizelge)
    # ==========================================================
    sheet2_name = "Haftalık Bakım Rutini (7 Gün)"
    if sheet2_name in wb.sheetnames:
        ws2 = wb[sheet2_name]
    else:
        ws2 = wb.create_sheet(title=sheet2_name)
        headers2 = [
            "Kullanıcı E-Posta",
            "Gün",
            "Günün Vurgusu",
            "Sabah Rutini (☀️ AM Adımları)",
            "Akşam Rutini (🌙 PM Adımları)",
            "Haftalık Özel Uygulama / Uyarılar",
            "Uygulama İpuçları & Öneriler"
        ]
        format_sheet_headers(ws2, headers2, HEADER_FILL_SECONDARY)

    # Remove previous schedule rows for this user in Sheet 2
    rows_to_keep = []
    for r in range(2, ws2.max_row + 1):
        cell_email = str(ws2.cell(row=r, column=1).value or '').strip().lower()
        if cell_email != email.strip().lower():
            rows_to_keep.append([ws2.cell(row=r, column=c).value for c in range(1, 8)])

    while ws2.max_row > 1:
        ws2.delete_rows(2)

    for r_vals in rows_to_keep:
        ws2.append(r_vals)
        cur_r = ws2.max_row
        for c in range(1, 8):
            cell = ws2.cell(row=cur_r, column=c)
            cell.font = REGULAR_FONT
            cell.border = THIN_BORDER
            cell.alignment = Alignment(vertical="center", wrap_text=True)

    # Prepare schedule
    schedule = routine.get('schedule') or []
    day_tr_map = {
        'Monday': 'Pazartesi',
        'Tuesday': 'Salı',
        'Wednesday': 'Çarşamba',
        'Thursday': 'Perşembe',
        'Friday': 'Cuma',
        'Saturday': 'Cumartesi',
        'Sunday': 'Pazar'
    }

    if not schedule:
        morning_steps = routine.get('morning', [])
        evening_steps = routine.get('evening', [])
        am_text = " -> ".join([f"{s.get('icon', '🧴')} {s.get('title', 'Adım')}" for s in morning_steps]) or "1. Temizleyici -> 2. Nemlendirici -> 3. Güneş Kremi (SPF)"
        pm_text = " -> ".join([f"{s.get('icon', '🌙')} {s.get('title', 'Adım')}" for s in evening_steps]) or "1. Temizleyici -> 2. Onarıcı Nemlendirici"

        standard_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        schedule = []
        for d in standard_days:
            notifs = []
            if d == 'Wednesday':
                notifs.append('exfoliant')
            elif d == 'Sunday':
                notifs.append('mask')
            schedule.append({
                'dayName': d,
                'am_text': am_text,
                'pm_text': pm_text,
                'notifications': notifs
            })

    for day_item in schedule:
        d_name_eng = day_item.get('dayName', '')
        d_name_tr = day_tr_map.get(d_name_eng, d_name_eng)

        if 'am_text' in day_item:
            am_steps_str = day_item['am_text']
        else:
            am_steps = day_item.get('am', [])
            am_lines = []
            for idx, s in enumerate(am_steps, 1):
                icon = s.get('icon', '🧴')
                title = s.get('title', 'Adım')
                prods = s.get('products', [])
                prod_label = f" ({', '.join(prods)})" if prods else ""
                am_lines.append(f"{idx}. {icon} {title}{prod_label}")
            am_steps_str = "\n".join(am_lines) if am_lines else "Temizleyici -> Nemlendirici -> SPF 50+"

        if 'pm_text' in day_item:
            pm_steps_str = day_item['pm_text']
        else:
            pm_steps = day_item.get('pm', [])
            pm_lines = []
            for idx, s in enumerate(pm_steps, 1):
                icon = s.get('icon', '🌙')
                title = s.get('title', 'Adım')
                prods = s.get('products', [])
                prod_label = f" ({', '.join(prods)})" if prods else ""
                pm_lines.append(f"{idx}. {icon} {title}{prod_label}")
            pm_steps_str = "\n".join(pm_lines) if pm_lines else "Temizleyici -> Gece Nemlendiricisi"

        notifs = day_item.get('notifications', [])
        notif_labels = []
        if 'retinol' in notifs:
            notif_labels.append("🔬 Retinol Uygulaması (Hücre Yenileme)")
        if 'exfoliant' in notifs:
            notif_labels.append("🧪 Peeling / Asit Bakımı (Ölü Deri & Gözenek)")
        if 'mask' in notifs:
            notif_labels.append("🧖‍♀️ Yoğun Nem & Onarım Maskesi")
        if 'vitc' in notifs:
            notif_labels.append("🍊 C Vitamini (Antioksidan Aydınlatma)")

        special_str = " | ".join(notif_labels) if notif_labels else "🌿 Temel Bariyer Koruma & Dinlenme"

        if 'retinol' in notifs:
            focus_str = "Gece yenilenmesi: Retinolü kuru cilde uygulayın, sonrasında nemlendiriciyle bariyeri destekleyin."
        elif 'exfoliant' in notifs:
            focus_str = "Eksfoliasyon: Asit sonrası retinol kullanmayın, ertesi sabah mutlaka SPF sürün."
        elif 'mask' in notifs:
            focus_str = "Haftalık dinlenme: Maskeyi 15-20 dk uygulayın, cildin nem deposunu doldurun."
        else:
            focus_str = "Günlük koruma: Sabah SPF'i tazeleyin, akşam nazikçe temizleyip nemlendirin."

        day_badge = f"{d_name_tr}"
        row_vals2 = [
            email,
            day_badge,
            "Günün Bakımı",
            am_steps_str,
            pm_steps_str,
            special_str,
            focus_str
        ]
        ws2.append(row_vals2)
        cur_row = ws2.max_row
        for c in range(1, 8):
            cell = ws2.cell(row=cur_row, column=c)
            cell.font = REGULAR_FONT
            cell.border = THIN_BORDER
            cell.fill = ZEBRA_FILL if (cur_row % 2 == 0) else WHITE_FILL
            if c in [1, 2, 3]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

        ws2.row_dimensions[cur_row].height = 42

    # ==========================================================
    # Sheet 3: Test Cevapları Detayı
    # ==========================================================
    sheet3_name = "Test Cevapları Detayı"
    if sheet3_name in wb.sheetnames:
        ws3 = wb[sheet3_name]
    else:
        ws3 = wb.create_sheet(title=sheet3_name)
        headers3 = [
            "Kullanıcı E-Posta",
            "Soru No",
            "Soru Metni",
            "Kullanıcının Seçtiği Cevap",
            "Cilt Etkisi / Puan Dağılımı"
        ]
        format_sheet_headers(ws3, headers3, HEADER_FILL_TERTIARY)

    detailed_answers = profile.get('detailedAnswers') or []
    if detailed_answers:
        keep_rows3 = []
        for r in range(2, ws3.max_row + 1):
            if str(ws3.cell(row=r, column=1).value or '').strip().lower() != email.strip().lower():
                keep_rows3.append([ws3.cell(row=r, column=c).value for c in range(1, 6)])

        while ws3.max_row > 1:
            ws3.delete_rows(2)

        for r_vals in keep_rows3:
            ws3.append(r_vals)

        for idx, ans in enumerate(detailed_answers, 1):
            q_num = f"Soru {idx}"
            q_text = ans.get('questionText') or ans.get('q_tr') or f"Soru {idx}"
            a_text = ans.get('answerText') or ans.get('opt_tr') or ans.get('id', '-')
            scores_item = ans.get('scores', {})
            scores_label = ", ".join([f"{k}: +{v}" for k, v in scores_item.items()]) if isinstance(scores_item, dict) else "-"

            row_vals3 = [email, q_num, q_text, a_text, scores_label]
            ws3.append(row_vals3)
            cur_r = ws3.max_row
            for c in range(1, 6):
                cell = ws3.cell(row=cur_r, column=c)
                cell.font = REGULAR_FONT
                cell.border = THIN_BORDER
                cell.fill = ZEBRA_FILL if (cur_r % 2 == 0) else WHITE_FILL
                if c in [1, 2]:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            ws3.row_dimensions[cur_r].height = 24

    # Auto-adjust column widths
    auto_fit_columns(ws0, {'D': 20, 'F': 35, 'H': 35, 'J': 45})
    auto_fit_columns(ws1, {'F': 35, 'J': 45})
    auto_fit_columns(ws2, {'D': 45, 'E': 45, 'F': 35, 'G': 45})
    auto_fit_columns(ws3, {'C': 45, 'D': 35, 'E': 25})

    wb.save(filepath)
    return filepath

def get_all_users_from_excel(filepath=EXCEL_FILE_PATH):
    """
    Reads all registered user accounts and their latest info from Excel file.
    Returns dict keyed by lowercased email:
    {
        email: {
            name, email, password, skinType, problems, streak, starSeries, products, lastLogin
        }
    }
    """
    if not os.path.exists(filepath):
        return {}

    try:
        wb = openpyxl.load_workbook(filepath, data_only=True)
    except Exception as e:
        print("Error opening Excel:", e)
        return {}

    users = {}

    # 1. Read from 'Kullanıcı Bilgileri & Hesaplar' if present
    if "Kullanıcı Bilgileri & Hesaplar" in wb.sheetnames:
        ws0 = wb["Kullanıcı Bilgileri & Hesaplar"]
        for r in range(2, ws0.max_row + 1):
            email = str(ws0.cell(row=r, column=3).value or '').strip().lower()
            if not email or '@' not in email or email == 'misafir@skincheck.local':
                continue

            name = str(ws0.cell(row=r, column=2).value or '').strip() or 'Kullanıcı'
            pwd = str(ws0.cell(row=r, column=4).value or '').strip() or '123456'
            skin_type = str(ws0.cell(row=r, column=5).value or '').strip()
            problems = str(ws0.cell(row=r, column=6).value or '').strip()
            streak_str = str(ws0.cell(row=r, column=7).value or '').strip()
            
            streak_num = 0
            if streak_str:
                import re
                m = re.search(r'\d+', streak_str)
                if m:
                    streak_num = int(m.group())

            star_str = str(ws0.cell(row=r, column=8).value or '').strip()
            prods_str = str(ws0.cell(row=r, column=10).value or '').strip()
            prods = [p.strip() for p in prods_str.split(',') if p.strip() and p.strip() != 'Temel Adımlar (Ürün eklenmedi)']
            last_login = str(ws0.cell(row=r, column=11).value or '').strip()

            users[email] = {
                'name': name,
                'email': email,
                'password': pwd,
                'skinType': skin_type,
                'skinProblems': problems,
                'streak': streak_num,
                'starSeries': star_str,
                'products': prods,
                'lastLogin': last_login
            }

    # 2. Also check 'Kullanıcı Girişleri & Sorunlar' for any users not yet in sheet 0
    if "Kullanıcı Girişleri & Sorunlar" in wb.sheetnames:
        ws1 = wb["Kullanıcı Girişleri & Sorunlar"]
        for r in range(2, ws1.max_row + 1):
            email = str(ws1.cell(row=r, column=3).value or '').strip().lower()
            if not email or '@' not in email or email == 'misafir@skincheck.local':
                continue
            if email not in users:
                name = str(ws1.cell(row=r, column=2).value or '').strip() or 'Kullanıcı'
                skin_type = str(ws1.cell(row=r, column=5).value or '').strip()
                problems = str(ws1.cell(row=r, column=6).value or '').strip()
                prods_str = str(ws1.cell(row=r, column=10).value or '').strip()
                prods = [p.strip() for p in prods_str.split(',') if p.strip() and p.strip() != 'Temel Adımlar (Ürün eklenmedi)']
                users[email] = {
                    'name': name,
                    'email': email,
                    'password': '123456',
                    'skinType': skin_type,
                    'skinProblems': problems,
                    'streak': 0,
                    'starSeries': 'Yok',
                    'products': prods,
                    'lastLogin': str(ws1.cell(row=r, column=1).value or '')
                }

    return users

def sync_excel_and_db(db_path, filepath=EXCEL_FILE_PATH):
    """
    Ensures complete bidirectional synchronization between database.db and kullanici_girisleri.xlsx:
    - Users in DB are updated/added to Excel
    - Users in Excel are updated/added to DB
    """
    excel_users = get_all_users_from_excel(filepath)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Get DB users
    c.execute('SELECT * FROM users')
    db_rows = c.fetchall()
    db_users = {row['email'].lower(): dict(row) for row in db_rows if row['email']}

    # 1. Sync Excel users to DB
    for email, x_user in excel_users.items():
        if email not in db_users:
            # Map skin type
            skin_map = {'Kuru Cilt': 'dry', 'Yağlı Cilt': 'oily', 'Karma Cilt': 'combination', 'Hassas Cilt': 'sensitive', 'Normal Cilt': 'normal'}
            mapped_type = skin_map.get(x_user['skinType'], 'combination')
            profile = {
                'name': x_user['name'],
                'email': email,
                'primaryType': mapped_type,
                'products': x_user['products']
            }
            c.execute('''
                INSERT INTO users (id, name, email, password, skinProfile, routine, routineSettings, streak, starSeries)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                email, x_user['name'], email, x_user['password'] or '123456',
                json.dumps(profile, ensure_ascii=False), '{}',
                json.dumps({'products': x_user['products'], 'frequency': 'regularly'}, ensure_ascii=False),
                x_user.get('streak', 0), json.dumps({'status': x_user.get('starSeries')}, ensure_ascii=False)
            ))
        else:
            # If DB user has no password, update it from Excel
            db_u = db_users[email]
            if not db_u.get('password') and x_user.get('password'):
                c.execute('UPDATE users SET password = ? WHERE email = ?', (x_user['password'], email))

    conn.commit()

    # 2. Sync DB users to Excel
    c.execute('SELECT * FROM users')
    all_db_rows = c.fetchall()
    conn.close()

    for row in all_db_rows:
        email = (row['email'] or '').strip().lower()
        if not email or '@' not in email or email == 'misafir@skincheck.local':
            continue
        try:
            profile = json.loads(row['skinProfile'] or '{}')
        except:
            profile = {}
        try:
            routine = json.loads(row['routine'] or '{}')
        except:
            routine = {}
        try:
            settings = json.loads(row['routineSettings'] or '{}')
        except:
            settings = {}

        data_payload = {
            'user': {
                'name': row['name'] or 'Kullanıcı',
                'email': email,
                'password': row['password'] or '123456',
                'isLoggedIn': True,
                'streak': row['streak'] or 0
            },
            'skinProfile': profile,
            'routine': routine,
            'routineSettings': settings,
            'streak': row['streak'] or 0,
            'password': row['password'] or '123456'
        }
        save_user_entry_to_excel(data_payload, filepath)
