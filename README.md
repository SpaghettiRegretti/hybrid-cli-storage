# 🔐 Hybrid CLI Storage
Secure File Storage with Hybrid Encryption (Modified Caesar + RSA)

---

## 📖 Overview

**Hybrid CLI Storage** adalah aplikasi **Command Line Interface (CLI)** berbasis Python untuk **menyimpan dan mengelola file secara aman** menggunakan metode **enkripsi hybrid**.

Aplikasi ini mengombinasikan:
- **Modified Caesar Cipher** (kriptografi klasik yang dimodifikasi) untuk enkripsi data
- **RSA 2048-bit** (kriptografi modern) untuk perlindungan metadata dan kunci

Program ini dirancang sebagai **proyek UAS kriptografi** dan mendukung **semua jenis file (binary-safe)**.

---

## ✨ Features

- 🔐 Enkripsi file dengan metode hybrid (2 layer)
- 🔓 Dekripsi file dengan verifikasi integritas
- 📂 Penyimpanan file terenkripsi secara lokal
- 🗂️ Manajemen file (list, delete)
- 🔑 Manajemen kunci RSA
- 🖥️ Tampilan CLI interaktif (Rich + Typer)

---

## 🛠️ Tech Stack

- **Python 3.9+**
- **Typer** – CLI framework
- **Rich** – CLI UI
- **Cryptography** – RSA & hashing
- **FastAPI** (opsional, backend server)

---

## 📦 Requirements

Pastikan sistem telah memiliki:

- Python **>= 3.9**
- pip
- OS: Linux / macOS / Windows

Install dependency dari file berikut: app/backend/requirements.txt

---

## 🚀 Installation

```bash
# Clone repository
git clone <repository_url>
cd spaghettiregretti-hybrid-cli-storage/app/backend

# (Optional) Virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Usage

### 1️⃣ Initialize Storage (Required)
Generate RSA Keys dan setup storage
```bash
python cli_storage.py init
```
### 2️⃣ Encrypt File
```bash
python cli_storage.py encrypt <file_path>\
```
contoh : 
```bash
python cli_storage.py encrypt /home/user/document.pdf
```
### 3️⃣ List Encrypted Files
```bash
python cli_storage.py list
```
### 4️⃣ Decrypt File
```bash
python cli_storage.py decrypt <file_id> <output_path>
```
contoh : 
```bash
python cli_storage.py decrypt a1b2c3d4 /tmp/restored.pdf
```
### 5️⃣ Delete File
```bash
python cli_storage.py delete <file_id>
```
### 6️⃣ System Information
```bash
python cli_storage.py info
```
### 7️⃣ Generate New RSA Keys (⚠️ Warning)
```bash
python cli_storage.py keygen
```
**Warning:** Key baru akan membuat file lama tidak bisa didekripsi

---

## 🔐 Encryption Flow

File Asli
   ↓
Modified Caesar Cipher (Dynamic Shift)
   ↓
Data Terenkripsi
   ↓
Metadata → RSA 2048-bit Encryption
   ↓
Stored Securely

---

## 📁 Project Structure

app/backend/
├── cli_storage.py
├── crypto_engine.py
├── key_manager.py
├── file_manager.py
├── requirements.txt
└── secure_storage/
    ├── keys/
    └── encrypted_files/

---

## 🔒 Security Notes

- RSA 2048-bit + OAEP (SHA-256)
- SHA-256 integrity check
- Private key permission protected
- Binary-safe encryption

---

## ⚠️ Important Notes

- Jangan hapus private_key.pem
- Backup folder secure_storage/keys
- Simpan File ID setelah enkripsi
- Regenerating keys = data loss

---

## 🎓 Academic Purpose

Project ini dibuat sebagai implementasi kriptografi hybrid untuk kebutuhan pembelajaran dan tugas akhir mata kuliah kriptografi.

--- 

## 👤 Author

**Angela Echa Naresti**
A11.2024.15971
A11.43UG1

