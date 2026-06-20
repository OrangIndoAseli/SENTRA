# SENTRA-ML Handoff

## Model aktif

Pipeline deteksi saat ini memakai:

- `models/helmet.pt` sebagai model utama untuk person/helmet/head.
- `models/vest.pt` sebagai model utama untuk safety vest.
- `models/candidate_sh17.pt` sebagai second opinion untuk mengurangi false alarm.
- `yolov8n.pt` sebagai fallback person detector.

Helmet hanya dianggap valid kalau terdeteksi di area kepala dengan confidence cukup tinggi. Helm yang dipegang tangan tidak dihitung sebagai helm yang dipakai.

## Menjalankan API

Di Windows, dari folder project:

```powershell
.\.python312\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Jika `.python312` tidak cocok di laptop lain, buat environment baru:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install ultralytics
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Endpoint penting

- `GET /health`
- `POST /detect-image`

Kontrak payload untuk BE/FE ada di `API_CONTRACT.md`.

## Folder penting untuk dibawa

- `app/`
- `models/`
- `assets/`
- `tools/`
- `docs/`
- `requirements.txt`
- `README.md`
- `API_CONTRACT.md`
- `HANDOFF.md`

Untuk backup penuh, copy seluruh folder `SENTRA-ML`.
