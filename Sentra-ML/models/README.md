# Model SENTRA-ML

SENTRA-ML saat ini memakai dua model YOLO terpisah agar hasil demo lebih stabil:

```text
models/helmet.pt  -> deteksi head, helmet, person
models/vest.pt    -> deteksi safety_vest
```

`models/best.pt` tetap boleh ada untuk kompatibilitas, tetapi aplikasi utama membaca `helmet.pt` dan `vest.pt`.

Jika salah satu file belum tersedia, aplikasi akan fallback ke `models/best.pt`, lalu ke `yolov8n.pt` jika perlu. Fallback `yolov8n.pt` terutama hanya berguna untuk deteksi `person`.

Jangan commit file `.pt` ke Git kalau repo akan dipush ke GitHub. Simpan model di Google Drive, Hugging Face, GitHub Release, atau storage bersama, lalu tulis link download di sini.

Class name yang didukung:

```text
person
head
helmet, hardhat, safety helmet
safety_vest, safety vest, vest, reflective vest
no_helmet, no-helmet, without helmet
no_vest, no-vest, without vest
```
