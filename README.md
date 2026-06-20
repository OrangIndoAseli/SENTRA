# SENTRA

**Safety Enforcement, Notification, Tracking & Risk Analytics** adalah sistem monitoring K3 berbasis computer vision. Sistem ini memproses gambar atau frame webcam/CCTV untuk mendeteksi pekerja, kepatuhan APD (helmet dan safety vest), serta intrusi ke zona bahaya. Pelanggaran disimpan sebagai insiden, ditampilkan pada dashboard, dan dapat ditindaklanjuti melalui status alert.

> Status proyek: MVP untuk demo/hackathon. Model PPE perlu disediakan secara terpisah dan tidak disimpan di Git.

## Arsitektur

```text
Browser (Vue 3, port 5173)
        |
        | REST API: data dashboard dan deteksi gambar
        v
Laravel API (port 8000) ---- SQLite / MySQL
        |
        | HTTP: gambar satu kali, WebSocket: frame live
        v
SENTRA-ML (FastAPI + YOLO, port 8001)
        |
        +-- model PPE, log lokal, dan capture bukti
```

Untuk deteksi gambar, frontend mengirimkan gambar ke Laravel lalu Laravel meneruskannya ke layanan ML. Pada mode live, frontend mengirim frame webcam ke WebSocket SENTRA-ML; ML hanya membuat insiden baru pada Laravel ketika pelanggaran baru terkonfirmasi. Insiden yang tidak terlihat selama 15 detik akan ditandai selesai.

## Fitur

- Dashboard statistik pelanggaran, kamera, dan alert aktif.
- Live monitoring dari webcam/browser dengan overlay hasil deteksi dan latensi.
- Deteksi `NO_HELMET`, `NO_VEST`, dan `DANGER_ZONE_ENTRY`.
- Zona bahaya per kamera melalui koordinat `x1`, `y1`, `x2`, `y2`.
- Penyimpanan insiden, alert, screenshot bukti, dan riwayat pelanggaran.
- Pencegahan duplikasi alert saat pelanggaran yang sama masih aktif.
- Pemilihan ulang screenshot bukti ketika kualitas deteksi meningkat.

## Struktur repository

```text
SENTRA/
|- Sentra_FE/       # Vue 3 + Vite: dashboard dan live monitoring
|- Sentra_BE/       # Laravel 12: API, database, dan penyimpanan insiden
|- Sentra-ML/       # FastAPI + Ultralytics YOLO: inferensi dan risk engine
`- README.md        # Dokumentasi utama
```

Dokumen teknis ML tersedia pada [Sentra-ML/API_CONTRACT.md](Sentra-ML/API_CONTRACT.md) dan penempatan model dijelaskan pada [Sentra-ML/models/README.md](Sentra-ML/models/README.md).

## Prasyarat

- Node.js 22.18+ (atau 24.12+) dan npm.
- PHP 8.2+, Composer, serta ekstensi SQLite; Laragon sudah sesuai untuk setup Windows.
- Python 3.10+ dan pip.
- Model YOLO PPE: `helmet.pt` dan `vest.pt` pada `Sentra-ML/models/`.

Model `.pt` tidak boleh dipush ke GitHub. Bila model tidak tersedia, aplikasi memakai fallback `yolov8n.pt`; mode tersebut hanya dapat mendeteksi orang dan tidak dapat memvalidasi APD secara akurat.

## Menjalankan secara lokal (Windows)

### 1. Layanan ML

```powershell
cd Sentra-ML
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Verifikasi: buka `http://127.0.0.1:8001/docs` atau `http://127.0.0.1:8001/health`.

### 2. Backend

Pada terminal baru:

```powershell
cd Sentra_BE
composer install
Copy-Item .env.example .env
php artisan key:generate
php artisan migrate --seed
php artisan storage:link
php artisan serve --host=127.0.0.1 --port=8000
```

Konfigurasi default memakai SQLite di `Sentra_BE/database/database.sqlite`. Untuk MySQL, ubah variabel `DB_*` pada `Sentra_BE/.env`, lalu jalankan migrasi kembali.

Verifikasi: `http://127.0.0.1:8000/api/health`. Respons akan menunjukkan status backend dan layanan ML.

### 3. Frontend

Pada terminal baru:

```powershell
cd Sentra_FE
npm install
npm run dev
```

Buka `http://127.0.0.1:5173/monitoring`. URL API default adalah `http://127.0.0.1:8000/api`; untuk mengubahnya, buat `Sentra_FE/.env.local` dengan `VITE_API_URL=...`.

## Cara demo singkat

1. Jalankan ketiga layanan dan pastikan endpoint health backend bernilai `ml: healthy`.
2. Buka **Monitoring**, pilih `CAM-01`, beri izin akses webcam, lalu mulai monitoring.
3. Tunjukkan satu kondisi aman dan satu pelanggaran APD atau masuk zona bahaya.
4. Perlihatkan popup alert serta bounding box pada video.
5. Buka **Dashboard**, **Violations**, dan **Logs** untuk membuktikan bahwa insiden dan bukti tersimpan.

## Aturan risiko

| Pelanggaran | Skor |
| --- | ---: |
| `NO_HELMET` | 40 |
| `NO_VEST` | 30 |
| `DANGER_ZONE_ENTRY` | 50 |

| Total skor | Level |
| --- | --- |
| 0 | `SAFE` |
| 1-40 | `WARNING` |
| 41-80 | `HIGH` |
| >80 | `CRITICAL` |

## Endpoint utama

| Layanan | Endpoint | Kegunaan |
| --- | --- | --- |
| Laravel | `GET /api/health` | Status backend dan ML |
| Laravel | `POST /api/detect-image` | Mendeteksi file gambar dan menyimpan hasil |
| Laravel | `GET /api/dashboard` | Statistik, alert, kamera, dan pelanggaran terbaru |
| Laravel | `GET/POST /api/cameras` | Membaca atau menambah kamera |
| Laravel | `GET/POST /api/danger-zones` | Membaca atau menambah zona bahaya |
| Laravel | `GET /api/detections` | Riwayat pelanggaran |
| ML | `GET /health` | Status FastAPI |
| ML | `POST /detect-image` | Inferensi gambar langsung |
| ML | `WS /ws/detect` | Inferensi frame live |

Gunakan Swagger FastAPI di `/docs` untuk melihat schema API ML secara interaktif.

## Konfigurasi penting

| File | Variabel | Default | Fungsi |
| --- | --- | --- | --- |
| `Sentra_BE/.env` | `SENTRA_ML_URL` | `http://127.0.0.1:8001` | Alamat layanan ML dari Laravel |
| `Sentra_BE/.env` | `SENTRA_ML_TIMEOUT` | `120` | Timeout inferensi (detik) |
| `Sentra_BE/.env` | `FRONTEND_URLS` | localhost:5173 | Origin frontend yang diizinkan |
| `Sentra-ML/.env` | `SENTRA_CORS_ORIGINS` | `*` | Origin yang diizinkan FastAPI |
| `Sentra-ML/.env` | `SENTRA_PPE_WORN_CONFIDENCE` | `0.35` | Ambang confidence APD |
| `Sentra_FE/.env.local` | `VITE_API_URL` | backend localhost | Base URL API frontend |

## Kualitas repository dan GitHub

File `.gitignore` root mengecualikan dependency hasil instalasi, virtual environment, cache, database/log/capture lokal, build output, serta model ML besar. Source code, migration, lockfile (`package-lock.json`, `composer.lock`), `.env.example`, dan aset demo tetap disimpan.

Jika artefak tersebut sudah pernah masuk ke indeks Git, `.gitignore` tidak menghapusnya dari riwayat. Jalankan perintah berikut sekali sebelum commit berikutnya:

```powershell
git rm -r --cached Sentra_FE/node_modules Sentra_BE/node_modules Sentra_BE/vendor Sentra-ML/.venv
git rm -r --cached Sentra-ML/models Sentra-ML/captures Sentra-ML/logs
git add .gitignore
git commit -m "chore: exclude generated artifacts"
```

Jangan jalankan perintah `git rm --cached` untuk folder yang belum pernah dilacak; Git akan memberi error bila path tidak ada pada indeks. Model dapat dibagikan lewat Google Drive, Hugging Face, atau GitHub Release, bukan commit biasa.

## Pengujian dan build

```powershell
# Frontend
cd Sentra_FE
npm run build

# Backend
cd ..\Sentra_BE
php artisan test
```

## Saran konsep video demo

Format paling efektif: video 90-120 detik dengan alur masalah → deteksi live → dampak operasional.

1. **0-10 dtk — masalah:** tampilkan area kerja/CCTV dan narasi singkat bahwa pengecekan APD manual tidak real-time.
2. **10-25 dtk — solusi:** tampilkan arsitektur sederhana: kamera → AI → dashboard/alert.
3. **25-65 dtk — inti demo:** lakukan dua skenario yang terkontrol: pekerja tanpa helmet dan pekerja masuk zona bahaya. Fokus pada overlay, level risiko, dan popup alert.
4. **65-90 dtk — pembuktian:** pindah ke dashboard/riwayat pelanggaran, buka screenshot bukti dan tunjukkan status alert dapat diselesaikan.
5. **90-120 dtk — nilai bisnis:** simpulkan dengan tiga manfaat terukur: respons lebih cepat, bukti insiden terdokumentasi, dan data untuk evaluasi K3.

Gunakan satu kamera, satu lokasi, dan dua skenario yang dapat diulang. Hindari mencoba terlalu banyak fitur atau kondisi pencahayaan yang tidak stabil saat rekaman. Siapkan rekaman cadangan dari alur yang sama untuk menghindari kegagalan webcam/model ketika presentasi.

## Lisensi

Proyek ini dikembangkan untuk Hackathon KIDECO 2026. Tambahkan lisensi eksplisit sebelum dipublikasikan sebagai proyek open-source.
