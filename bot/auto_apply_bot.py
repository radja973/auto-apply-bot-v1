import os
import sys
import time
import json
import random
import csv
from datetime import datetime
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
CSV_LOG_FILE = os.path.join(os.path.dirname(__file__), "applied_jobs.csv")
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chrome_profile")
DEBUG_SCREENSHOT = os.path.join(os.path.dirname(__file__), "debug_search.png")


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"[INFO] File konfigurasi belum ditemukan di: {CONFIG_FILE}")
        print("[INFO] Menjalankan wizard setup awal...\n")
        from setup_config import run_setup_wizard
        return run_setup_wizard(CONFIG_FILE)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def random_sleep(min_sec=3, max_sec=6):
    sleep_time = random.uniform(min_sec, max_sec)
    time.sleep(sleep_time)


def clean_lingering_bot_chrome():
    try:
        import psutil
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if USER_DATA_DIR.lower() in cmdline.lower() and proc.info['pid'] != current_pid:
                        proc.kill()
            except Exception:
                pass
        time.sleep(1)
    except Exception:
        pass


def init_driver():
    clean_lingering_bot_chrome()
    options = Options()
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    print("[INFO] Membuka Google Chrome...")
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def is_logged_in(driver):
    if driver.get_cookie("li_at"):
        return True
    indicators = driver.find_elements(By.CSS_SELECTOR, ".global-nav__me, #global-nav, nav.global-nav, img[alt*='Photo of']")
    return len(indicators) > 0


def verify_login(driver):
    driver.get("https://www.linkedin.com/feed/")
    random_sleep(3, 4)

    if not is_logged_in(driver):
        print("\n" + "=" * 65)
        print(" [PERHATIAN] AKUN LINKEDIN BELUM LOGIN DI CHROME!")
        print("=" * 65)
        print(" 1. Jendela Google Chrome sekarang sedang terbuka.")
        print(" 2. Silakan login ke akun LinkedIn Anda di browser tsb.")
        print(" 3. Setelah berhasil masuk ke Beranda / Feed LinkedIn Anda,")
        print("    KEMBALI KE TERMINAL INI, lalu:")
        print("=" * 65)
        input(" >>> TEKAN [ENTER] DI SINI SETELAH ANDA SELESAI LOGIN DI CHROME <<< ")
        print("\n[INFO] Memverifikasi status login...")
        driver.get("https://www.linkedin.com/feed/")
        random_sleep(2, 3)

    if is_logged_in(driver):
        print("[SUCCESS] Login LinkedIn terverifikasi! Sesi telah disimpan.\n")
        return True
    return False


def build_search_url(config):
    keywords = quote(config.get("keywords", "Java Spring Boot"))
    location = quote(config.get("location", "Indonesia"))
    
    url = f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}&f_AL=true"
    if config.get("remote_only", False):
        url += "&f_WT=2"
    return url


def log_applied_job(title, company, link, status):
    file_exists = os.path.exists(CSV_LOG_FILE)
    with open(CSV_LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Job Title", "Company", "Job Link", "Status"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), title, company, link, status])


def smart_fill_form(driver, config):
    """Otomatis mendeteksi pertanyaan form Easy Apply dan menjawab secara presisi."""
    # 1. Phone number
    try:
        phone_inputs = driver.find_elements(By.CSS_SELECTOR, "input[id*='phoneNumber'], input[type='tel']")
        for inp in phone_inputs:
            val = inp.get_attribute("value")
            if not val or len(val.strip()) < 3:
                inp.clear()
                inp.send_keys(config.get("phone_number", ""))
                print(f"   [+] No Telp diisi: {config.get('phone_number')}")
    except Exception:
        pass

    # 2. Upload resume
    resume_path = config.get("resume_pdf_path", "").strip()
    if resume_path and os.path.exists(resume_path):
        try:
            file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            for file_inp in file_inputs:
                file_inp.send_keys(os.path.abspath(resume_path))
                print(f"   [+] Upload resume: {os.path.basename(resume_path)}")
                random_sleep(1, 2)
        except Exception:
            pass

    # 3. Input teks & angka (Pertanyaan tambahan)
    try:
        text_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input:not([type]), input[type='number']")
        for inp in text_inputs:
            val = inp.get_attribute("value") or ""
            if val.strip():
                continue  # Sudah terisi

            # Ambil label menggunakan JavaScript murni (100% tahan obfuscation)
            js_get_label = """
            let inp = arguments[0];
            let labelText = '';
            
            // Cek aria-label atau placeholder
            if (inp.getAttribute('aria-label')) labelText += ' ' + inp.getAttribute('aria-label');
            if (inp.getAttribute('placeholder')) labelText += ' ' + inp.getAttribute('placeholder');
            
            // Cek label terkait id
            if (inp.id) {
                try {
                    let lbl = document.querySelector(`label[for="${CSS.escape(inp.id)}"]`);
                    if (lbl) labelText += ' ' + lbl.innerText;
                } catch(e) {}
            }
            
            // Cek elemen kontainer induk
            let parent = inp.parentElement;
            for (let i = 0; i < 4; i++) {
                if (!parent) break;
                let lbl = parent.querySelector('label, span.t-14, .fb-dash-form-element__label');
                if (lbl && lbl.innerText) {
                    labelText += ' ' + lbl.innerText;
                }
                parent = parent.parentElement;
            }
            return labelText.toLowerCase();
            """
            label_text = driver.execute_script(js_get_label, inp) or ""

            # Logika pencocokan cerdas
            if "current" in label_text and "salary" in label_text or "gaji saat ini" in label_text or "gaji sekarang" in label_text:
                curr = str(config.get("current_salary", "2000000"))
                inp.clear()
                inp.send_keys(curr)
                print(f"   [+] Gaji saat ini diisi: Rp {int(curr):,}")
            elif any(w in label_text for w in ["expect", "expected", "gaji yang diharapkan", "ekspektasi gaji"]):
                exp = str(config.get("expected_salary", "10000000"))
                inp.clear()
                inp.send_keys(exp)
                print(f"   [+] Ekspektasi gaji diisi: Rp {int(exp):,}")
            elif any(w in label_text for w in ["year", "experience", "tahun", "pengalaman"]):
                years = str(config.get("years_of_experience_default", "1"))
                inp.clear()
                inp.send_keys(years)
                print(f"   [+] Pengalaman diisi: {years} tahun")
            elif any(w in label_text for w in ["city", "kota", "location"]):
                inp.clear()
                inp.send_keys("Jakarta")
            elif any(w in label_text for w in ["notice", "pemberitahuan"]):
                inp.clear()
                inp.send_keys("Immediately")
            elif "salary" in label_text or "gaji" in label_text:
                # Jika cuma tertulis Salary tanpa kata current/expect
                exp = str(config.get("expected_salary", "10000000"))
                inp.clear()
                inp.send_keys(exp)
                print(f"   [+] Kolom gaji diisi: Rp {int(exp):,}")
            else:
                # Default angka pengalaman jika berupa input angka pendek
                inp.clear()
                inp.send_keys("1")
    except Exception:
        pass

    # 4. Radio Buttons (Pilih Yes / Ya)
    try:
        radio_wrappers = driver.find_elements(By.CSS_SELECTOR, "fieldset, div[data-test-form-builder-radio-button-form-component]")
        for rw in radio_wrappers:
            try:
                # Cari label Yes / Ya
                yes_labels = rw.find_elements(By.XPATH, ".//label[contains(translate(text(), 'YES', 'yes'), 'yes') or contains(translate(text(), 'YA', 'ya'), 'ya')]")
                if yes_labels and yes_labels[0].is_displayed():
                    yes_labels[0].click()
                    print("   [+] Memilih opsi: Yes / Ya")
                else:
                    radios = rw.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                    if radios and not any(r.is_selected() for r in radios):
                        driver.execute_script("arguments[0].click();", radios[0])
            except Exception:
                pass
    except Exception:
        pass


def discard_modal(driver):
    try:
        dismiss_btns = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Dismiss'], button[data-test-modal-close-btn], button[aria-label='Tutup']")
        for btn in dismiss_btns:
            if btn.is_displayed():
                btn.click()
                random_sleep(1, 2)
                break

        discard_btns = driver.find_elements(By.CSS_SELECTOR, "button[data-control-name='discard_application_confirm_btn'], button[data-test-dialog-secondary-action]")
        for btn in discard_btns:
            if btn.is_displayed():
                btn.click()
                random_sleep(1, 2)
                break
    except Exception:
        pass


def apply_on_job_page(driver, config, title):
    random_sleep(3, 4)

    # Cari tombol Easy Apply / Lamar Mudah
    apply_btn = None
    selectors = [
        "button[aria-label*='Easy Apply']",
        "button[aria-label*='Lamar Mudah']",
        "button.jobs-apply-button",
        "div.jobs-apply-button--top-card button"
    ]
    for sel in selectors:
        btns = driver.find_elements(By.CSS_SELECTOR, sel)
        for b in btns:
            if b.is_displayed():
                txt = b.text.lower()
                if "easy apply" in txt or "lamar mudah" in txt or "apply" in txt:
                    apply_btn = b
                    break
        if apply_btn:
            break

    if not apply_btn:
        print("   [-] Tidak ada tombol Easy Apply (mungkin sudah dilamar / link eksternal).")
        return False, "NO_EASY_APPLY_BTN"

    try:
        apply_btn.click()
        random_sleep(2, 3)

        for step in range(8):
            smart_fill_form(driver, config)
            random_sleep(1, 2)

            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            clicked = False

            # 1. Cek tombol Submit
            for b in all_buttons:
                if b.is_displayed():
                    t = b.text.strip().lower()
                    if t in ["submit application", "submit", "kirim lamaran", "kirim permohonan"]:
                        b.click()
                        print(f"   🎉 [BERHASIL TERKIRIM] {title}!")
                        random_sleep(3, 4)
                        discard_modal(driver)
                        return True, "SUCCESS"

            # 2. Cek tombol Review
            for b in all_buttons:
                if b.is_displayed():
                    t = b.text.strip().lower()
                    if t in ["review", "tinjau"]:
                        b.click()
                        clicked = True
                        random_sleep(1, 3)
                        break
            if clicked:
                continue

            # 3. Cek tombol Next
            for b in all_buttons:
                if b.is_displayed():
                    t = b.text.strip().lower()
                    if t in ["next", "berikutnya", "lanjut"]:
                        b.click()
                        clicked = True
                        random_sleep(1, 3)
                        break
            if clicked:
                continue

            # 4. Jika ada error tak tertangani
            errors = driver.find_elements(By.CSS_SELECTOR, ".artdeco-inline-feedback--error")
            if errors and any(e.is_displayed() for e in errors):
                print("   [!] Ada pertanyaan kustom tak terjawab. Dilewati dengan aman.")
                discard_modal(driver)
                return False, "SKIPPED_CUSTOM_QUESTIONS"

        discard_modal(driver)
        return False, "MULTI_STEP_TIMEOUT"

    except Exception as e:
        discard_modal(driver)
        return False, f"ERROR: {str(e)[:30]}"


def extract_jobs_from_page(driver):
    for _ in range(6):
        driver.execute_script("window.scrollBy(0, 700);")
        time.sleep(0.4)

    js_code = """
    let links = document.querySelectorAll("a[href*='/jobs/view/']");
    let result = [];
    links.forEach(a => {
        let href = a.href.split('?')[0];
        let title = a.innerText.trim();
        if (title.length > 2 && !result.some(r => r.url === href)) {
            result.push({url: href, title: title});
        }
    });
    return result;
    """
    raw_jobs = driver.execute_script(js_code)
    return raw_jobs or []


def run_bot():
    config = load_config()
    print("=" * 65)
    print("      LINKEDIN EASY APPLY AUTO-BOT (100% GRATIS)")
    print("=" * 65)
    print(f" Kata Kunci : {config.get('keywords')}")
    print(f" Lokasi     : {config.get('location')}")
    print(f" Remote     : {config.get('remote_only')} (False = Termasuk On-site/Hybrid)")
    print(f" Resume PDF : {os.path.basename(config.get('resume_pdf_path', ''))}")
    print(f" Current Sal: Rp {int(config.get('current_salary', 2000000)):,}")
    print(f" Gaji Target: Rp {int(config.get('expected_salary', 10000000)):,}")
    print(f" Max Jobs   : {config.get('max_jobs_to_apply')}")
    print("=" * 65 + "\n")

    driver = init_driver()

    try:
        verify_login(driver)

        search_url = build_search_url(config)
        print(f"[INFO] Membuka URL Pencarian:\n{search_url}\n")
        driver.get(search_url)
        random_sleep(5, 7)

        applied_count = 0
        max_jobs = config.get("max_jobs_to_apply", 30)

        jobs = extract_jobs_from_page(driver)
        print(f"[INFO] Berhasil menemukan {len(jobs)} lowongan Easy Apply di hasil pencarian.")

        if not jobs:
            print("[WARN] Belum ada lowongan ditemukan. Menyimpan screenshot debug...")
            driver.save_screenshot(DEBUG_SCREENSHOT)
            print(f"[DEBUG] Screenshot tersimpan di: {DEBUG_SCREENSHOT}")

        for idx, job in enumerate(jobs, 1):
            if applied_count >= max_jobs:
                break

            title = job["title"]
            job_url = job["url"]

            print(f"\n[{idx}/{len(jobs)}] Membuka Lowongan: {title}")
            print(f"      URL: {job_url}")

            driver.get(job_url)

            success, status = apply_on_job_page(driver, config, title)
            log_applied_job(title, "LinkedIn", job_url, status)

            if success:
                applied_count += 1
                print(f"   📊 [TOTAL BERHASIL]: {applied_count}/{max_jobs}")
                delay_min = config.get("delay_between_applications_min_sec", 4)
                delay_max = config.get("delay_between_applications_max_sec", 8)
                random_sleep(delay_min, delay_max)
            else:
                random_sleep(1, 2)

        print("\n" + "=" * 65)
        print(f"[SELESAI] Total berhasil melamar ke {applied_count} lowongan!")
        if os.path.exists(CSV_LOG_FILE):
            print(f"[LAPORAN] Detail riwayat tersimpan di: {CSV_LOG_FILE}")
        print("=" * 65)

    except KeyboardInterrupt:
        print("\n[STOP] Bot dihentikan secara manual oleh Anda.")
    except Exception as e:
        print(f"\n[ERROR] Terjadi kendala: {e}")
    finally:
        print("[INFO] Menutup browser...")
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    run_bot()
