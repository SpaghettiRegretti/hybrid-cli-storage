"#🔐 CLI File Storage dengan Hybrid Encryption

Aplikasi CLI untuk menyimpan file dengan enkripsi hybrid menggunakan kombinasi **Modified Caesar Cipher** dan **RSA**.

## 📋 Deskripsi

Aplikasi ini mengimplementasikan sistem enkripsi hybrid 2-layer:

### Layer 1: Modified Caesar Cipher (Klasik - Dimodifikasi)
- **Dynamic Shift**: Shift tidak konstan, berubah di setiap posisi byte
- **Salt-based Randomization**: Menggunakan salt untuk meningkatkan keacakan
- **Position-dependent**: Setiap byte dienkripsi dengan shift berbeda berdasarkan posisinya
- **Byte-level Encryption**: Bekerja pada level byte, mendukung semua tipe file

**Modifikasi Unik:**
```
shift(position) = (base_shift + salt_hash[position % 32] + position) % 256
encrypted_byte = (original_byte + shift(position)) % 256
```

### Layer 2: RSA-2048 (Modern)
- Mengenkripsi parameter Caesar (base_shift, salt) dan metadata
- Key size: 2048 bits
- Padding: OAEP dengan SHA-256
- Melindungi confidentiality dari Caesar key

## 🎯 Keunggulan Metode Hybrid

1. **Kecepatan**: Caesar cipher (layer 1) cepat untuk file besar
2. **Keamanan**: RSA (layer 2) melindungi Caesar key dari serangan
3. **Integritas**: SHA-256 hash untuk verifikasi file
4. **Universal**: Mendukung semua tipe file (binary-safe)

## 🚀 Instalasi

```bash
cd /app/backend
pip install -r requirements.txt
```

## 📖 Penggunaan

### 1. Initialize Storage
Pertama kali, initialize storage dan generate RSA keys:

```bash
python cli_storage.py init
```

Output:
- Membuat directory `secure_storage/`
- Generate RSA key pair (2048-bit)
- Siap untuk enkripsi file

### 2. Encrypt File
Enkripsi file dan simpan ke storage:

```bash
python cli_storage.py encrypt <path_to_file>
```

Contoh:
```bash
python cli_storage.py encrypt /tmp/document.pdf
python cli_storage.py encrypt /home/user/photo.jpg
python cli_storage.py encrypt /app/data.zip
```

Output akan memberikan **File ID** yang harus disimpan untuk dekripsi.

### 3. List Files
Melihat semua file terenkripsi:

```bash
python cli_storage.py list
```

Menampilkan tabel dengan:
- File ID
- Original filename
- Size
- Timestamp

### 4. Decrypt File
Dekripsi file menggunakan File ID:

```bash
python cli_storage.py decrypt <file_id> <output_path>
```

Contoh:
```bash
python cli_storage.py decrypt a1b2c3d4 /tmp/restored.pdf
```

### 5. Delete File
Hapus file terenkripsi dari storage:

```bash
python cli_storage.py delete <file_id>
```

### 6. System Info
Lihat informasi sistem dan enkripsi:

```bash
python cli_storage.py info
```

### 7. Generate New Keys
Generate RSA key pair baru (WARNING: file lama tidak bisa didekripsi):

```bash
python cli_storage.py keygen
```

### 8. Help
Lihat semua perintah yang tersedia:

```bash
python cli_storage.py --help
```

## 📁 Struktur File

```
/app/backend/
├── cli_storage.py          # Main CLI application
├── crypto_engine.py        # Hybrid encryption engine
├── key_manager.py          # RSA key management
├── file_manager.py         # File storage management
└── secure_storage/
    ├── keys/
    │   ├── private_key.pem
    │   └── public_key.pem
    └── encrypted_files/
        ├── index.json
        ├── <file_id>.enc       # Encrypted file content
        └── <file_id>.meta      # Encrypted metadata
```

## 🔧 Alur Enkripsi

```
Original File
     ↓
[1] Generate Caesar Parameters
     ├─ base_shift ← SHA256(file_content)
     └─ salt ← random 16 bytes
     ↓
[2] Modified Caesar Encryption
     └─ Dynamic shift per byte
     ↓
Caesar Encrypted Content
     ↓
[3] Create Metadata
     └─ {filename, base_shift, salt, hash}
     ↓
[4] RSA Encryption (Metadata)
     └─ OAEP padding + SHA-256
     ↓
[5] Save to Storage
     ├─ Encrypted content → .enc
     └─ Encrypted metadata → .meta
```

## 🔓 Alur Dekripsi

```
Load from Storage
     ├─ Encrypted content (.enc)
     └─ Encrypted metadata (.meta)
     ↓
[1] RSA Decryption (Metadata)
     └─ Get Caesar parameters
     ↓
[2] Modified Caesar Decryption
     └─ Dynamic shift per byte
     ↓
[3] Integrity Verification
     └─ SHA-256 hash check
     ↓
Original File Restored
```

## 🎓 Aspek Akademik

### Kombinasi Klasik + Modern
- **Klasik (Caesar)**: Dimodifikasi dengan dynamic shift dan salt
- **Modern (RSA)**: Asymmetric encryption untuk key protection
- **Hybrid**: Menggabungkan kecepatan klasik dengan keamanan modern

### Keunikan Modifikasi
1. **Dynamic Shift Caesar**: Tidak seperti Caesar klasik yang shift konstan
2. **Salt-based**: Menambah entropi dan mencegah pattern analysis
3. **Position-dependent**: Setiap posisi byte punya shift berbeda
4. **Two-layer Protection**: Caesar untuk data, RSA untuk key

### Kasus Penggunaan
- **File Storage**: Menyimpan file sensitif dengan enkripsi
- **Backup System**: Backup terenkripsi otomatis
- **Document Protection**: Proteksi dokumen penting
- **Universal Encryption**: Mendukung semua tipe file

## 🔒 Keamanan

- **RSA 2048-bit**: Standar industri untuk key protection
- **OAEP Padding**: Mencegah chosen ciphertext attacks
- **SHA-256**: Hash function untuk integrity check
- **Private Key Protection**: File permission 600 (read/write owner only)
- **No Key Storage in Memory**: Keys loaded on-demand

## ⚠️ Catatan Penting

1. **Simpan Private Key**: Jangan hilangkan file `private_key.pem`
2. **Backup Keys**: Backup directory `secure_storage/keys/`
3. **File ID**: Simpan File ID setelah enkripsi
4. **New Keys = Data Loss**: Generate key baru akan membuat file lama tidak bisa didekripsi

## 🧪 Testing

### Test Enkripsi/Dekripsi
```bash
# Create test file
echo \"Hello World! This is a test.\" > /tmp/test.txt

# Encrypt
python cli_storage.py encrypt /tmp/test.txt

# List (dapatkan File ID)
python cli_storage.py list

# Decrypt
python cli_storage.py decrypt <file_id> /tmp/test_restored.txt

# Verify
cat /tmp/test_restored.txt
```

### Test dengan File Besar
```bash
# Create 10MB random file
dd if=/dev/urandom of=/tmp/large_file.bin bs=1M count=10

# Encrypt & decrypt
python cli_storage.py encrypt /tmp/large_file.bin
python cli_storage.py decrypt <file_id> /tmp/large_file_restored.bin

# Compare
diff /tmp/large_file.bin /tmp/large_file_restored.bin
```

## 📝 Lisensi

Dibuat untuk keperluan akademik - Proyek Akhir Mata Kuliah Kriptografi

## 👨‍💻 Author

Angela Echa Naresti_A11.2024.15971 - Implementasi Kriptografi Hybrid (Modified Caesar + RSA)
"