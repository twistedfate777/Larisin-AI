# Larisin AI - Dynamic Pricing Assistant

Larisin AI adalah *engine* penentuan harga dinamis (Dynamic Pricing) dan pembuat *caption* otomatis untuk *fashion thrifting* berbasis AI. Proyek ini memadukan 3 lapis arsitektur cerdas:
1. **L1 (Computer Vision):** MobileNetV2 mendeteksi *archetype* tren (Y2K, Modest-Modern, Generic).
2. **L2 (Probabilistic Math):** Hidden Markov Model (HMM) & Monte Carlo Simulation untuk menentukan harga jual paling optimal berdasarkan probabilitas tren.
3. **L3 (LLM Advisor):** Integrasi Groq (120b/27b) untuk menyusun rasionalisasi harga dan *draft caption* sosial media.

---

## Panduan Pengujian untuk Panitia (Juri)

Repositori ini telah disiapkan agar dapat berjalan secara **100% instan** menggunakan Docker, lengkap dengan model yang sudah dilatih (Pre-trained), sehingga Anda tidak perlu repot men-download dataset atau melatih model dari awal.

### Prasyarat
- Docker Desktop / Docker Compose terinstal.

### 1. Konfigurasi Kunci API
Buat sebuah file bernama `.env` di dalam folder `server/` (yaitu di `server/.env`) dan isi dengan kredensial Groq dan Database (atau bisa menggunakan kredensial pengujian yang kami sertakan di dokumen submission jika ada):

```env
GROQ_API_KEY="gsk_..."
DATABASE_URL="postgresql+asyncpg://..."
CLOUDINARY_URL="cloudinary://..."
```

### 2. Jalankan Aplikasi
Buka terminal di *root directory* (tempat file ini berada) dan jalankan:
```bash
docker compose up --build
```
Tunggu hingga proses selesai dan log terminal menampilkan *Uvicorn running*. (Catatan: Proses pertama kali akan mengunduh *image* Python dan menginstal dependensi).

### 3. Cara Pengujian (Swagger UI)
Kami telah menyediakan antarmuka interaktif:

1. Buka browser dan akses: **http://localhost:8000/docs**
2. Buka tab rute `POST /api/v1/price-recommendation`.
3. Klik tombol **Try it out** di sebelah kanan atas rute tersebut.
4. Isi form pengujian:
   - **image**: Pilih file foto baju (JPG/PNG) dari komputer Anda.
   - **base_price**: Masukkan harga modal (contoh: `100000`).
   - **stock_entry_date**: Masukkan tanggal (contoh: `2026-07-20`).
5. Klik **Execute**.

Scroll ke bawah untuk melihat *Response JSON* yang berisi klasifikasi tren, perhitungan margin Monte Carlo, dan *draft caption* dari LLM!

---
*Dibuat untuk MVP Competition 2026.*
