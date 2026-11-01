import time
import sys
import requests
from playwright.sync_api import sync_playwright

SERVER_URL = "http://localhost:8090"

def wait_for_server(url, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                print(f"Server is up and responding at {url}")
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def run_tests():
    console_errors = []
    page_errors = []
    failed_requests = []
    http_errors = []

    print("\n--- Starting Playwright Comprehensive Browser Automation Test ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console messages
        def on_console(msg):
            if msg.type in ['error']:
                console_errors.append(f"Console {msg.type}: {msg.text}")
                print(f"  [Browser Console Error] {msg.text}")
        page.on('console', on_console)

        # Capture uncaught exceptions
        def on_page_error(err):
            page_errors.append(str(err))
            print(f"  [Uncaught Page Error] {err}")
        page.on('pageerror', on_page_error)

        # Capture failed requests
        def on_request_failed(req):
            if "google-analytics" not in req.url:
                failed_requests.append(f"Failed request: {req.method} {req.url}")
                print(f"  [Request Failed] {req.method} {req.url}")
        page.on('requestfailed', on_request_failed)

        # Capture HTTP 4xx/5xx responses
        def on_response(res):
            if res.status >= 400 and "google-analytics" not in res.url:
                http_errors.append(f"HTTP {res.status}: {res.url}")
                print(f"  [HTTP Error {res.status}] {res.url}")
        page.on('response', on_response)

        # 1. Test Navigation to index.html
        print("\n[Step 1] Navigating to Home Page...")
        resp = page.goto(SERVER_URL, wait_until="networkidle")
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        print("  -> Page loaded successfully with status 200")

        # 2. Test Language Selection
        print("\n[Step 2] Testing Language Dropdown & Switching across multiple languages...")
        page.click("#langToggle")
        time.sleep(0.3)
        assert page.is_visible("#langDropdown"), "Language dropdown should be visible"
        print("  -> Dropdown opened")

        # Click English
        page.click('.lang-option[data-lang="en"]')
        time.sleep(0.5)
        current_lang = page.text_content("#currentLang").strip()
        print(f"  -> Switched language to English: '{current_lang}'")
        assert "English" in current_lang or "EN" in current_lang.upper()

        # Click German
        page.click("#langToggle")
        time.sleep(0.3)
        page.click('.lang-option[data-lang="de"]')
        time.sleep(0.5)
        current_lang = page.text_content("#currentLang").strip()
        print(f"  -> Switched language to Deutsch: '{current_lang}'")
        assert "Deutsch" in current_lang or "DE" in current_lang.upper()

        # Switch back to Turkish
        page.click("#langToggle")
        time.sleep(0.3)
        page.click('.lang-option[data-lang="tr"]')
        time.sleep(0.5)
        current_lang = page.text_content("#currentLang").strip()
        print(f"  -> Switched back to Türkçe: '{current_lang}'")

        # 3. Test Gönder / Arama (Ingredient Analysis with warnings)
        print("\n[Step 3] Testing Ingredient Search & Analysis with warnings formula...")
        test_ingredients_with_warnings = "Aqua, Alcohol Denat, Fragrance, Methylparaben, Isopropyl Myristate, Glycerin, Dimethicone"
        page.fill("#aiChatInput", test_ingredients_with_warnings)
        page.click("#aiChatSendBtn")
        time.sleep(1.0)
        
        # Verify results section is displayed
        assert page.is_visible("#resultsSection"), "Results section should be visible after analysis"
        score_text = page.text_content("#overallScore").strip()
        print(f"  -> Analysis rendered! Overall score: '{score_text}'")
        assert score_text != "", "Overall score should not be empty"

        # Verify ingredients list rendered
        ing_items = page.query_selector_all("#ingredientsList > *")
        print(f"  -> Rendered {len(ing_items)} ingredient elements in list")
        assert len(ing_items) > 0, "Ingredient list should contain elements"

        # 4. Test Result Tabs (Warnings Tab)
        print("\n[Step 4] Testing Result Tabs (Warnings Tab)...")
        warn_tab = page.query_selector('.result-tab[data-result="warningsPanel"]')
        assert warn_tab is not None, "Warnings tab button must exist"
        page.click('.result-tab[data-result="warningsPanel"]')
        time.sleep(0.4)
        assert page.is_visible("#warningsPanel"), "Warnings panel should be visible"
        warn_items = page.query_selector_all("#warningsList > *")
        print(f"  -> Warnings tab active! Found {len(warn_items)} warnings in list")
        assert len(warn_items) > 0, "Expected warnings to be listed"

        # Switch back to Ingredients tab
        page.click('.result-tab[data-result="ingredientsPanel"]')
        time.sleep(0.4)
        assert page.is_visible("#ingredientsPanel"), "Ingredients panel should be visible"
        print("  -> Switched back to Ingredients tab")

        # 5. Test Mini Search within Results Page
        print("\n[Step 5] Testing Mini Search Box...")
        page.fill("#miniSearchInput", "Aqua, Niacinamide, Zinc PCA")
        page.click("#miniSearchSendBtn")
        time.sleep(1.0)
        score_text2 = page.text_content("#overallScore").strip()
        print(f"  -> Mini search analysis rendered! New score: '{score_text2}'")
        assert score_text2 != ""

        # 6. Test User Auth Trigger & Modal
        print("\n[Step 6] Testing User Auth (Login/Register Modal)...")
        page.click("#authTrigger")
        time.sleep(0.5)
        assert page.is_visible("#authModal"), "Auth modal should open"
        print("  -> Auth modal opened")
        
        # Switch to Register tab
        page.click('.auth-tab[data-auth="register"]')
        time.sleep(0.3)
        assert page.is_visible("#registerForm"), "Register form should be visible"
        print("  -> Register form active")

        # Switch back to Login tab
        page.click('.auth-tab[data-auth="login"]')
        time.sleep(0.3)
        assert page.is_visible("#loginForm"), "Login form should be visible"
        print("  -> Login form active")

        # Test Forgot Password link
        page.click("#forgotPasswordLink")
        time.sleep(0.3)
        assert page.is_visible("#resetPasswordForm"), "Reset password form should be visible"
        print("  -> Reset password form opened")

        # Back to Login
        page.click(".back-to-login")
        time.sleep(0.3)
        assert page.is_visible("#loginForm"), "Should be back to login form"
        print("  -> Returned to login form")

        # Close auth modal
        page.click("#authModalClose")
        time.sleep(0.3)
        assert not page.is_visible("#loginForm"), "Login form should be hidden after close"
        print("  -> Auth modal closed")

        # 7. Test Encyclopedia Sidebar
        print("\n[Step 7] Testing Encyclopedia Sidebar...")
        page.click("#sidebarToggleBtn")
        time.sleep(0.5)
        sidebar_cls = page.get_attribute("#encyclopediaSidebar", "class") or ""
        assert "open" in sidebar_cls or page.is_visible("#encyclopediaSidebar"), "Sidebar should be open"
        print(f"  -> Encyclopedia sidebar opened")

        # Check concern items in sidebar
        concerns = page.query_selector_all("#sidebarConcerns .concern-item")
        print(f"  -> Found {len(concerns)} concern items in sidebar")
        assert len(concerns) > 0, "Sidebar concerns should not be empty"

        # Search in encyclopedia
        page.fill("#encyclopediaSearch", "Niacinamide")
        time.sleep(0.5)
        enc_results = page.query_selector_all("#sidebarContent .encyclopedia-item, #sidebarContent > *")
        print(f"  -> Filtered encyclopedia items: {len(enc_results)}")

        page.click("#sidebarCloseBtn")
        time.sleep(0.3)
        sidebar_cls_after = page.get_attribute("#encyclopediaSidebar", "class") or ""
        print(f"  -> Sidebar closed")

        # 8. Test Admin Panel
        print("\n[Step 8] Testing Admin Panel (/admin.html)...")
        resp_admin = page.goto(f"{SERVER_URL}/admin.html", wait_until="networkidle")
        assert resp_admin.status == 200, f"Expected 200 for admin.html, got {resp_admin.status}"
        time.sleep(1.0)
        items = page.query_selector_all(".product-item")
        print(f"  -> Admin panel loaded {len(items)} products in the database list")
        assert len(items) > 0, "Admin product list should load items from /api/products"

        # 9. Test Debug Search Page
        print("\n[Step 9] Testing debug_search.html...")
        resp_debug = page.goto(f"{SERVER_URL}/debug_search.html", wait_until="networkidle")
        assert resp_debug.status == 200, f"Expected 200 for debug_search.html, got {resp_debug.status}"
        print("  -> debug_search.html loaded successfully")

        browser.close()

    print("\n=================== TEST REPORT ===================")
    print(f"Total Page errors     : {len(page_errors)}")
    for e in page_errors:
        print(f"  ❌ {e}")
    print(f"Total Console errors  : {len(console_errors)}")
    for e in console_errors:
        print(f"  ❌ {e}")
    print(f"Total Failed requests : {len(failed_requests)}")
    for f in failed_requests:
        print(f"  ❌ {f}")
    print(f"Total HTTP 4xx/5xx    : {len(http_errors)}")
    for h in http_errors:
        print(f"  ❌ {h}")

    if page_errors or console_errors or failed_requests or http_errors:
        print("\n[FAIL] SOME CHECKS FAILED!")
        sys.exit(1)
    else:
        print("\n[SUCCESS] ALL TESTS PASSED WITH 0 CONSOLE ERRORS AND 0 NETWORK FAILURES!")
        sys.exit(0)

if __name__ == '__main__':
    run_tests()
