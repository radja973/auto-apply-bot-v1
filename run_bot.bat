@echo off
title AutoApply Bot v1 - Multi-Portal Job Auto-Bot (100%% Gratis)
cd /d "%~dp0"

:menu
cls
echo ========================================================
echo      AUTOAPPLY BOT V1 - MULTI-PORTAL JOB AUTO-BOT
echo ========================================================
python --version >nul 2>&1
if errorlevel 1 (
    echo  [!] Python belum terpasang / belum masuk PATH.
    echo      Pilih [P] untuk install Python terlebih dahulu.
    echo ========================================================
)
if not exist "bot\config.json" (
    echo  [!] File bot\config.json belum dibuat.
    echo      Pilih [0] terlebih dahulu untuk mengisi data pribadi.
    echo ========================================================
)
echo  Pilih opsi yang ingin Anda jalankan:
echo.
echo  [P] Install Python (Khusus yang belum punya Python)
echo  [0] Setup / Ubah Data Pribadi (Gaji, Resume, Keyword)
echo  [1] LinkedIn Easy Apply (Lamar Otomatis)
echo  [2] Glints Auto-Apply (Lamar Otomatis Glints)
echo  [3] Jalankan Keduanya Otomatis (LinkedIn + Glints)
echo  [4] Glints Scanner Saja (Hanya kumpulkan daftar lowongan)
echo  [5] Install Library Python (requirements.txt)
echo  [6] Keluar
echo.
set /p choice="Masukkan pilihan (P/0/1/2/3/4/5/6): "

if /i "%choice%"=="P" goto install_python
if "%choice%"=="0" goto setup
if "%choice%"=="1" goto linkedin
if "%choice%"=="2" goto glints_auto
if "%choice%"=="3" goto both
if "%choice%"=="4" goto glints_scan
if "%choice%"=="5" goto install_deps
if "%choice%"=="6" goto end
goto menu

:install_python
echo.
echo [INFO] Mengecek dan menginstall Python 3.12 via Windows Package Manager (winget)...
where winget >nul 2>&1
if errorlevel 1 goto open_python_web
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
if errorlevel 1 goto open_python_web
echo.
echo [SUCCESS] Python berhasil diinstall!
echo [PENTING] Tutup jendela ini lalu klik 2x run_bot.bat lagi agar PATH terbaca.
pause
goto end

:open_python_web
echo.
echo [INFO] Membuka halaman download resmi Python di browser...
echo [PENTING] Saat instalasi, WAJIB centang "Add python.exe to PATH".
start "" "https://www.python.org/downloads/"
pause
goto menu

:setup
echo.
python bot\setup_config.py
pause
goto menu

:linkedin
echo.
echo [Menjalankan LinkedIn Auto-Bot...]
python bot\auto_apply_bot.py
goto end

:glints_auto
echo.
echo [Menjalankan Glints Auto-Apply Bot...]
python bot\glints_auto_apply.py
goto end

:both
echo.
echo [1/2] Menjalankan LinkedIn Auto-Bot...
python bot\auto_apply_bot.py
echo.
echo [2/2] Menjalankan Glints Auto-Apply Bot...
python bot\glints_auto_apply.py
goto end

:glints_scan
echo.
echo [Menjalankan Glints Job Scanner...]
python bot\glints_bot.py
goto end

:install_deps
echo.
echo [Menginstall dependensi Python...]
pip install -r bot\requirements.txt
pause
goto menu

:end
echo.
echo ========================================================
echo       Selesai! Tekan tombol apa saja untuk keluar.
echo ========================================================
pause
