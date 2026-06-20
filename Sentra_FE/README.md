# SENTRA

### Safety Enforcement, Notification, Tracking & Risk Analytics

SENTRA adalah sistem monitoring keselamatan kerja berbasis Computer Vision yang dirancang untuk membantu pengawasan K3 (Keselamatan dan Kesehatan Kerja) di lingkungan pertambangan secara real-time.

Sistem ini menggunakan teknologi Artificial Intelligence untuk mendeteksi pekerja, penggunaan APD (Alat Pelindung Diri), serta pelanggaran zona berbahaya melalui CCTV atau webcam.

---

## Latar Belakang

Industri pertambangan memiliki risiko kecelakaan kerja yang tinggi akibat:

* Pengawasan APD yang masih dilakukan secara manual.
* Area operasional yang luas dan dinamis.
* Sulitnya memantau seluruh pekerja secara bersamaan.
* Potensi masuknya pekerja ke zona berbahaya tanpa terdeteksi.
* Kebutuhan sistem peringatan dini yang cepat dan otomatis.

SENTRA hadir untuk mengubah sistem pengawasan keselamatan dari reaktif menjadi preventif melalui deteksi visual berbasis AI.

---

## Fitur Utama

### Dashboard Monitoring

* Statistik pekerja terdeteksi
* Statistik pelanggaran APD
* Statistik pelanggaran zona bahaya
* Ringkasan kondisi operasional

### Live Monitoring

* Monitoring CCTV secara real-time
* Informasi status kamera
* Deteksi objek berbasis AI

### PPE Detection

* Deteksi penggunaan Helmet
* Deteksi penggunaan Safety Vest
* Deteksi pelanggaran APD

### Danger Zone Detection

* Monitoring area berbahaya
* Deteksi intrusi zona terlarang
* Notifikasi pelanggaran otomatis

### Alert System

* Alert real-time
* Klasifikasi tingkat risiko
* Peringatan visual

### Activity Log

* Riwayat aktivitas sistem
* Audit keselamatan
* Penyimpanan kejadian pelanggaran

---

## Teknologi

| Komponen         | Teknologi     |
| ---------------- | ------------- |
| Frontend         | Vue 3         |
| Styling          | Tailwind CSS  |
| Routing          | Vue Router    |
| State Management | Pinia         |
| Computer Vision  | YOLOv11       |
| Image Processing | OpenCV        |
| Backend API      | FastAPI       |
| Database         | MySQL         |
| Input Device     | CCTV / Webcam |

---

## Struktur Project

```bash
src
│
├── assets
│
├── components
│   ├── Sidebar.vue
│   ├── Navbar.vue
│   ├── StatCard.vue
│   ├── CameraCard.vue
│   └── AlertPopup.vue
│
├── layouts
│   └── DashboardLayout.vue
│
├── pages
│   ├── Dashboard.vue
│   ├── Monitoring.vue
│   ├── Violations.vue
│   ├── DangerZone.vue
│   └── Logs.vue
│
├── router
│   └── index.js
│
├── stores
│   └── sentraStore.js
│
├── App.vue
└── main.js
```

---

## Routing

| Route        | Halaman         |
| ------------ | --------------- |
| /            | Dashboard       |
| /monitoring  | Live Monitoring |
| /violations  | Pelanggaran APD |
| /danger-zone | Zona Bahaya     |
| /logs        | Log Sistem      |

---

## MVP Features

* CCTV/Webcam Integration
* Person Detection
* Helmet Detection
* Safety Vest Detection
* Danger Zone Detection
* Real-time Alert
* Violation Screenshot Storage
* Monitoring Dashboard

---

## Future Development

* WebSocket Real-time Notification
* Telegram Alert Integration
* WhatsApp Alert Integration
* Employee Tracking
* Face Recognition
* Vehicle Detection
* Heavy Equipment Monitoring
* Predictive Risk Analytics
* AI Safety Report

---

## Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/sentra.git
cd sentra
```

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

### Build Production

```bash
npm run build
```

---

## Team

Hackathon KIDECO 2026

**Project:** SENTRA
**Full Name:** Safety Enforcement, Notification, Tracking & Risk Analytics

---

## License

This project is developed for Hackathon KIDECO 2026.
