# SENTRA-ML

SENTRA adalah singkatan dari **Safety Enforcement, Notification, Tracking & Risk Analytics**. Project ini adalah MVP sistem deteksi dini bahaya dan keselamatan kerja berbasis Computer Vision untuk Hackathon Kideco 2026.

Fitur utama:

- Input webcam, CCTV URL, atau file video.
- Capture frame real-time dengan OpenCV.
- Deteksi person menggunakan Ultralytics YOLO.
- Deteksi helmet dan safety vest jika memakai model custom PPE.
- Pelanggaran `NO_HELMET`, `NO_VEST`, dan `DANGER_ZONE_ENTRY`.
- Overlay visual pada frame.
- Screenshot pelanggaran ke folder `captures/`.
- Log kejadian ke SQLite `sentra_logs.db` dan JSONL `logs/detection_logs.jsonl`.
- API FastAPI untuk integrasi Laravel atau dashboard frontend.

## Struktur Folder

```text
SENTRA-ML/
├── app/
│   ├── main.py
│   ├── detector.py
│   ├── config.py
│   ├── database.py
│   ├── schemas.py
│   ├── risk_engine.py
│   ├── zone.py
│   └── utils.py
├── models/
│   └── README.md
├── captures/
├── logs/
├── sample_videos/
├── requirements.txt
├── README.md
└── run_detector.py
```

## Install

Disarankan memakai virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan API

```bash
uvicorn app.main:app --reload --port 8001
```

Endpoint:

- `GET /` status API.
- `GET /health` health check.
- `GET /logs` membaca log dari SQLite.
- `GET /stats` statistik pelanggaran.
- `POST /detect-image` upload image dan proses deteksi.
- `POST /send-to-laravel` helper untuk mengirim payload ke URL Laravel.

Dokumentasi interaktif tersedia di:

```text
http://127.0.0.1:8001/docs
```

Kontrak API untuk Backend dan Frontend ada di:

```text
API_CONTRACT.md
```

## Menjalankan Detector Webcam

```bash
python run_detector.py --source 0
```

Menjalankan dari file video:

```bash
python run_detector.py --source sample_videos/test.mp4
```

Menjalankan CCTV atau stream URL:

```bash
python run_detector.py --source rtsp://username:password@camera-ip/stream
```

## Test Upload Image

Dengan curl:

```bash
curl -X POST "http://127.0.0.1:8000/detect-image?camera_code=CAM-01" -F "file=@sample.jpg"
```

Atau buka `http://127.0.0.1:8000/docs`, pilih endpoint `POST /detect-image`, lalu upload file gambar.

## Model Custom PPE

Untuk hasil demo saat ini, SENTRA-ML memakai dua model YOLO terpisah:

```text
models/helmet.pt
models/vest.pt
```

`models/helmet.pt` dipakai untuk deteksi `head`, `helmet`, dan `person`.
`models/vest.pt` dipakai untuk deteksi `safety_vest`.

Jika model custom belum ada, sistem memakai fallback `models/best.pt`, lalu `yolov8n.pt` agar minimal dapat mendeteksi `person`.

Class name didukung secara fleksibel, termasuk:

- `person`
- `helmet`, `hardhat`, `safety helmet`
- `safety vest`, `vest`, `reflective vest`
- `no-helmet`, `no_helmet`
- `no-vest`, `no_vest`

## Danger Zone

Zona bahaya default ada di `app/config.py`:

```python
DANGER_ZONE = {
    "x1": 100,
    "y1": 300,
    "x2": 600,
    "y2": 700,
}
```

Sistem mengecek foot point pekerja, yaitu titik tengah bawah bounding box person. Jika titik ini masuk zona bahaya, sistem menambahkan pelanggaran `DANGER_ZONE_ENTRY`.

## Risk Scoring

Bobot pelanggaran:

- `NO_HELMET` = 40
- `NO_VEST` = 30
- `DANGER_ZONE_ENTRY` = 50

Level risiko:

- `0` = `SAFE`
- `1` sampai `40` = `WARNING`
- `41` sampai `80` = `HIGH`
- lebih dari `80` = `CRITICAL`

## Contoh Output JSON

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
      "box": [100, 120, 250, 500]
    },
    {
      "worker_id": "W-002",
      "helmet": false,
      "vest": true,
      "in_danger_zone": true,
      "violations": ["NO_HELMET", "DANGER_ZONE_ENTRY"],
      "risk_score": 90,
      "risk_level": "CRITICAL",
      "box": [300, 140, 460, 520]
    }
  ],
  "summary": {
    "total_violation": 2,
    "highest_risk": "CRITICAL",
    "screenshot_saved": true,
    "screenshot_path": "captures/violation_20260617_101500.jpg"
  }
}
```

## Integrasi Laravel

Backend Laravel dapat membaca data dengan dua cara:

1. Pull data dari API SENTRA-ML melalui `GET /logs` atau `GET /stats`.
2. Terima push payload dari endpoint helper `POST /send-to-laravel`.

Contoh payload untuk helper:

```json
{
  "url": "http://localhost:8000/api/sentra/detections",
  "payload": {
    "camera_code": "CAM-01",
    "worker_count": 1,
    "detections": [],
    "summary": {
      "total_violation": 0,
      "highest_risk": "SAFE",
      "screenshot_saved": false,
      "screenshot_path": null
    }
  }
}
```

Untuk production, endpoint Laravel sebaiknya memakai autentikasi token dan HTTPS.
