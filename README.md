# Multi-Portal Job Auto-Apply Bot (LinkedIn & Glints)

Bot otomasi berbasis **Python + Selenium** untuk mencari lowongan kerja dan mengirim lamaran secara otomatis di **LinkedIn Easy Apply** dan **Glints Indonesia** (100% gratis, tanpa biaya langganan atau API berbayar).

---

## ✨ Fitur Utama
- **Multi-Portal:** Mendukung **LinkedIn Easy Apply** dan **Glints Indonesia**.
- **Auto-Login Google (Glints):** Mendukung login otomatis melalui Google Sign-In serta penyimpanan sesi permanen di folder lokal `chrome_profile/`.
- **Smart Multi-Step Form Filler:** Otomatis mengunggah Resume PDF, mengisi gaji saat ini, ekspektasi gaji, lama pengalaman, dan pertanyaan standar.
- **Interactive CMD Fallback:** Jika ada pertanyaan khusus/unik pada form lamaran (teks, pilihan ganda, atau dropdown), bot akan menampilkannya di terminal/CMD agar Anda bisa menjawab langsung dari terminal tanpa perlu menyentuh browser.
- **Setup Wizard Tanpa Edit Kode (`setup_config.py`):** Pengguna baru cukup menjalankan menu `[0]` untuk mengisi/mengubah data pribadi, gaji, kata kunci, dan path CV PDF.
- **Anti Duplikat & Log CSV:** Semua riwayat lamaran tercatat otomatis di file `.csv` sehingga bot tidak akan melamar ke lowongan yang sama dua kali.

---

## 📁 Struktur Folder

Folder utama dibuat sangat rapi agar pengguna baru cukup berfokus pada launcher dan panduan:

| File / Folder | Fungsi |
| :--- | :--- |
| `run_bot.bat` | **Launcher utama (Windows)** — klik 2x untuk membuka menu interaktif. |
| `AutoApply_Bot_v1_Guide.pptx` | **Presentasi / Panduan Visual** proyek AutoApply Bot v1. |
| `README.md` | Dokumentasi lengkap instalasi dan penggunaan. |
| `chrome_profile/` | Folder sesi login Chrome *(otomatis muncul di folder utama setelah user login Chrome pertama kali)*. |
| `bot/` | Folder berisi seluruh script inti (`auto_apply_bot.py`, `glints_auto_apply.py`, `glints_bot.py`, `setup_config.py`), template `config.example.json`, `requirements.txt`, serta hasil log `.csv`. |

---

## 🚀 Panduan Instalasi & Penggunaan (Untuk Pengguna Baru)

### 1. Prasyarat
- **Google Chrome** sudah terpasang.
- **Python 3.10+** sudah terpasang (centang *"Add Python to PATH"* saat instalasi).

### 2. Download & Install Library
1. Download repository ini (atau klik **Code -> Download ZIP**, lalu ekstrak foldernya).
2. Klik 2x file **`run_bot.bat`**.
3. Jika baru pertama kali menjalankan, pilih menu **`[5]`** (*Install Library Python*) untuk menginstall `selenium` dan `psutil` (atau jalankan `pip install -r requirements.txt` di terminal).

### 3. Mengisi Data Pribadi (Pilih Salah Satu Cara)

#### Cara A: Menggunakan Setup Wizard (Paling Mudah - Direkomendasikan)
1. Di menu `run_bot.bat`, pilih **`[0]`** (*Setup / Ubah Data Pribadi*).
2. Jawab pertanyaan satu per satu di terminal (kata kunci, lokasi, domisili, email, no. HP, gaji, dan file CV `.pdf`).
   > **Tips:** Untuk path Resume PDF, Anda bisa langsung **drag & drop** file PDF dari File Explorer ke jendela terminal, lalu tekan `ENTER`.
3. Jika nanti ingin mengubah gaji atau mengganti file CV, cukup jalankan ulang menu **`[0]`** dan tekan `ENTER` pada data yang tidak ingin diubah.

#### Cara B: Edit Manual `config.json`
Salin file `config.example.json` menjadi `config.json`, lalu buka dengan Notepad/VS Code dan sesuaikan isinya:

```json
{
  "keywords": "Java Spring Boot",
  "location": "Indonesia",
  "domicile": "Jakarta Timur, DKI Jakarta",
  "remote_only": false,
  "experience_level": ["entry_level", "associate", "mid_senior"],
  "email": "email.anda@gmail.com",
  "phone_number": "81234567890",
  "country_code": "+62",
  "resume_pdf_path": "C:\\Users\\NamaAnda\\Downloads\\CV_Anda.pdf",
  "years_of_experience_default": "1",
  "current_salary": "5000000",
  "expected_salary": "10000000",
  "max_jobs_to_apply": 30,
  "delay_between_applications_min_sec": 4,
  "delay_between_applications_max_sec": 8
}
```

**Penjelasan Field Penting:**
- `keywords`: Posisi/keahlian yang dicari (misal: `"Backend Developer"`, `"Data Analyst"`).
- `domicile`: Kota tempat tinggal Anda untuk pengisian form lokasi.
- `phone_number`: Nomor HP aktif tanpa angka `0` atau `+62` di depan (misal: `81234567890`).
- `resume_pdf_path`: Lokasi file CV PDF Anda (di Windows gunakan double backslash `\\`).
- `current_salary` & `expected_salary`: Nominal gaji tanpa titik/koma (misal: `"10000000"` untuk 10 juta).
- `max_jobs_to_apply`: Batas maksimal lamaran per satu kali jalan agar akun tetap aman.

---

## ▶️ Menjalankan Bot
1. Klik 2x **`run_bot.bat`**.
2. Pilih **`[1]`** untuk LinkedIn, **`[2]`** untuk Glints, atau **`[3]`** untuk keduanya.
3. **Login Pertama Kali:**
   - Pada LinkedIn: jika belum login, login secara manual di jendela Chrome yang terbuka lalu tekan `ENTER` di terminal.
   - Pada Glints: bot akan mencoba auto-login menggunakan akun Google Anda jika sesi belum aktif.
   - Sesi login tersimpan di `chrome_profile/`, sehingga pada pemakaian berikutnya tidak perlu login ulang.
4. **Jika Muncul Pertanyaan Khusus:**
   - Perhatikan jendela terminal. Jika bot menampilkan `[WARNING - INPUT FORM DIBUTUHKAN]`, ketik jawaban Anda langsung di terminal dan tekan `ENTER`.

---

## 🔒 Privasi & Keamanan
- Jangan pernah membagikan folder `chrome_profile/` atau file `config.json` Anda ke publik (sudah otomatis diabaikan oleh `.gitignore`).
- Gunakan jeda (`delay_between_applications`) dan batas `max_jobs_to_apply` yang wajar agar aktivitas akun tetap terlihat natural.
