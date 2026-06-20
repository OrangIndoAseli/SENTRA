# SENTRA-ML Start Guide

Panduan ini dipakai untuk menjalankan ulang project SENTRA-ML setelah laptop di-reset atau project dicopy dari flashdisk.

## 1. Restore Project

Copy folder `HACKATON` dari flashdisk ke laptop. Lokasi yang paling aman adalah lokasi lama:

```text
C:\Users\LOQ\OneDrive\Lampiran\Dokumen\KULIAH\HACKATON
```

Lalu buka folder ini di VS Code:

```text
C:\Users\LOQ\OneDrive\Lampiran\Dokumen\KULIAH\HACKATON\SENTRA-ML
```

File penting yang harus ada:

```text
SENTRA-ML\models\best.pt
SENTRA-ML\yolov8n.pt
SENTRA-ML\.python312\python.exe
SENTRA-ML\datasets\helmet_yolo\data.yaml
SENTRA-ML\runs\detect\runs\detect\helmet_cpu\weights\last.pt
```

Kalau `.python312` ikut tercopy, project bisa jalan tanpa install Python ulang.

## 2. Cek Python dan Dependency

Dari PowerShell di folder `SENTRA-ML`:

```powershell
.\.python312\python.exe --version
```

Harus keluar:

```text
Python 3.12.10
```

Cek dependency utama:

```powershell
.\.python312\python.exe -c "import fastapi, uvicorn, cv2, ultralytics, torch; print('deps ok')"
```

Kalau output `deps ok`, environment aman.

## 3. Jalankan API ML

```powershell
.\.python312\python.exe -m uvicorn app.main:app --reload
```

Kalau berhasil, terminal akan menampilkan server di:

```text
http://127.0.0.1:8000
```

Buka dokumentasi API:

```text
http://127.0.0.1:8000/docs
```

Endpoint penting:

```text
GET  /
GET  /health
GET  /logs
GET  /stats
POST /detect-image
POST /send-to-laravel
```

## 4. Test Deteksi Foto

Lewat Swagger:

1. Buka `http://127.0.0.1:8000/docs`
2. Pilih `POST /detect-image`
3. Klik `Try it out`
4. Upload foto, contoh `assets/sample1.jpeg`
5. Klik `Execute`

Lewat PowerShell:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/detect-image?camera_code=CAM-01" `
  -Method Post `
  -Form @{ file = Get-Item ".\assets\sample1.jpeg" }
```

## 5. Test Video atau Kamera

Untuk webcam laptop:

```powershell
.\.python312\python.exe run_detector.py --source 0
```

Kalau laptop masih Safe Mode, webcam biasanya tidak bisa dipakai. Pakai video dari HP:

```text
sample_videos\test.mp4
```

Lalu jalankan:

```powershell
.\.python312\python.exe run_detector.py --source sample_videos/test.mp4
```

Kalau preview window error:

```powershell
.\.python312\python.exe run_detector.py --source sample_videos/test.mp4 --no-window
```

Untuk IP camera HP, laptop dan HP harus satu jaringan. Contoh:

```powershell
.\.python312\python.exe run_detector.py --source "http://192.168.0.133:8888/video"
```

Kalau browser laptop tidak bisa membuka URL IP camera, Python juga tidak bisa membaca stream itu.

## 6. Response API untuk BE/FE

Contoh response `POST /detect-image`:

```json
{
  "camera_code": "CAM-01",
  "worker_count": 2,
  "detections": [
    {
      "worker_id": "W-001",
      "helmet": true,
      "vest": true,
      "in_danger_zone": false,
      "violations": [],
      "risk_score": 0,
      "risk_level": "SAFE",
      "box": [123, 261, 804, 1594]
    }
  ],
  "summary": {
    "total_violation": 0,
    "highest_risk": "SAFE",
    "screenshot_saved": false,
    "screenshot_path": null
  }
}
```

Field yang paling penting untuk backend/frontend:

```text
worker_count
detections[].helmet
detections[].vest
detections[].violations
detections[].risk_score
detections[].risk_level
summary.total_violation
summary.highest_risk
```

Nilai `risk_level`:

```text
SAFE
WARNING
HIGH
CRITICAL
```

Nilai `violations`:

```text
NO_HELMET
NO_VEST
DANGER_ZONE_ENTRY
```

Catatan: model saat ini dilatih untuk `head`, `helmet`, dan `person`. Dataset belum punya class `vest`, jadi sistem tidak memaksa violation `NO_VEST` selama model tidak mendukung vest.

## 7. Integrasi dengan Backend Laravel

Backend bisa pull data:

```text
GET http://127.0.0.1:8000/logs
GET http://127.0.0.1:8000/stats
```

Backend juga bisa menerima hasil dari endpoint image:

```text
POST http://127.0.0.1:8000/detect-image?camera_code=CAM-01
```

Jika frontend langsung memanggil API ML dari browser, CORS sudah aktif. Untuk production, batasi origin dengan environment variable:

```powershell
$env:SENTRA_CORS_ORIGINS="http://localhost:3000,http://localhost:5173"
.\.python312\python.exe -m uvicorn app.main:app --reload
```

## 8. Cek Progress Training

Progress training ada di:

```text
runs\detect\runs\detect\helmet_cpu
```

Cek epoch terakhir:

```powershell
Get-Content .\runs\detect\runs\detect\helmet_cpu\results.csv -Tail 1
```

Cek target total epoch:

```powershell
Get-Content .\runs\detect\runs\detect\helmet_cpu\args.yaml
```

File checkpoint:

```text
runs\detect\runs\detect\helmet_cpu\weights\best.pt
runs\detect\runs\detect\helmet_cpu\weights\last.pt
```

`best.pt` adalah model terbaik sementara. `last.pt` adalah checkpoint terakhir untuk lanjut training.

## 9. Lanjut Training

Training sebelumnya berjalan di CPU, jadi lambat. Untuk lanjut dari checkpoint terakhir:

```powershell
.\.python312\python.exe -c "from ultralytics import YOLO; model=YOLO('runs/detect/runs/detect/helmet_cpu/weights/last.pt'); model.train(resume=True)"
```

Setelah training selesai, copy model terbaik ke folder model aktif:

```powershell
Copy-Item .\runs\detect\runs\detect\helmet_cpu\weights\best.pt .\models\best.pt -Force
```

## 10. Backup Sebelum Reset

Backup seluruh folder:

```text
C:\Users\LOQ\OneDrive\Lampiran\Dokumen\KULIAH\HACKATON
```

Minimal file penting:

```text
SENTRA-ML\models\best.pt
SENTRA-ML\runs\detect\runs\detect\helmet_cpu\weights\best.pt
SENTRA-ML\runs\detect\runs\detect\helmet_cpu\weights\last.pt
SENTRA-ML\datasets\helmet_yolo
SENTRA-ML\.python312
SENTRA-ML\app
SENTRA-ML\tools
```

Kalau semua itu ada di flashdisk, progress training dan project aman.

## 11. Troubleshooting

Kalau API tidak bisa jalan, cek dependency:

```powershell
.\.python312\python.exe -c "from app.main import app; print(app.title)"
```

Kalau model custom tidak terbaca, pastikan file ini ada:

```text
models\best.pt
```

Kalau dataset training error setelah pindah lokasi folder, edit:

```text
datasets\helmet_yolo\data.yaml
```

Ubah `path:` supaya menunjuk ke lokasi baru folder dataset.

Kalau IP camera timeout, cek IP laptop:

```powershell
ipconfig
```

IP laptop dan IP HP harus satu jaringan. Contoh yang benar:

```text
HP:     192.168.0.133
Laptop: 192.168.0.50
```

Contoh yang tidak bisa langsung terhubung:

```text
HP:     192.168.0.133
Laptop: 10.134.52.44
```
