
# 🤖 Jarvis Hand Sign Recognition

Sistem cerdas berbasis Python yang mampu menerjemahkan 31 kombinasi gestur jari menjadi suara (Text-to-Speech) secara *real-time* dan *offline*. Alat ini dirancang untuk membantu komunikasi isyarat dengan akurasi tinggi menggunakan pustaka MediaPipe dan OpenCV.

## ✨ Fitur Utama

* **🖐️ 31 Kombinasi Gestur**: Mendukung pemetaan lengkap 31 variasi jari (dari kelingking hingga jempol) sesuai dengan standar dataset visual.
* **🔊 Kustomisasi Teks ke Suara**: Pengguna dapat mengisi teks ucapan secara dinamis untuk setiap nomor gestur sebelum menjalankan program.
* **⚡ Zero-Latency Audio**: Menggunakan sistem *audio caching* (pre-rendering gTTS) sehingga suara muncul instan tanpa jeda internet.
* **📡 Mode Offline**: Tidak memerlukan koneksi internet atau API eksternal (seperti Gemini AI) saat menjalankan deteksi di kamera.
* **🖥️ Clean HUD UI**: Tampilan antarmuka yang bersih dengan subtitle transparan yang menampilkan hasil terjemahan secara langsung.

## 🛠️ Prasyarat

* **Python 3.10+**: Runtime utama program.
* **Kamera/Webcam**: Untuk menangkap input visual tangan.

## 🚀 Instalasi

1. **Clone repositori ini:**
```bash
git clone https://github.com/andreiswahyudi/hand-sign.git
cd hand-sign

```


2. **Install dependensi:**
```bash
pip install -r requirements.txt

```


3. **Jalankan aplikasi:**
```bash
python handsign.py

```



## 📖 Cara Penggunaan

Program ini dilengkapi dengan menu interaktif di terminal sebelum kamera diaktifkan.

1. **Konfigurasi Suara**:
* Masukkan nomor ID gestur (1-31) berdasarkan tabel referensi.
* Ketik teks yang ingin diucapkan untuk gestur tersebut.


2. **Mulai Deteksi**:
* Ketik `run` di terminal. Sistem akan membuat cache audio dan menyalakan kamera.


3. **Kendali Kamera**:
* Tunjukkan gestur tangan kanan ke arah kamera.
* Tekan tombol **'Q'** pada keyboard untuk keluar dari program.



## 📋 Daftar Referensi Gestur (1-31)

Sistem menggunakan logika biner jari: **1=Kelingking, 2=Manis, 3=Tengah, 4=Telunjuk, 5=Jempol**.

No,Kombinasi Jari,No,Kombinasi Jari
1,[1] Kelingking Saja,17,"[1, 2, 4] Kelingking, Manis, Telunjuk"
2,[2] Jari Manis Saja,18,"[1, 2, 5] Kelingking, Manis, Jempol"
3,[3] Jari Tengah Saja,19,"[1, 3, 4] Kelingking, Tengah, Telunjuk"
4,[4] Jari Telunjuk Saja,20,"[1, 3, 5] Kelingking, Tengah, Jempol"
5,[5] Jempol Saja,21,"[1, 4, 5] Kelingking + Telunjuk + Jempol"
6,"[1, 2] Kelingking + Manis",22,"[2, 3, 4] Manis, Tengah, Telunjuk"
7,"[1, 3] Kelingking + Tengah",23,"[2, 3, 5] Manis, Tengah, Jempol"
8,"[1, 4] Kelingking + Telunjuk",24,"[2, 4, 5] Manis, Telunjuk, Jempol"
9,"[1, 5] Kelingking + Jempol",25,"[3, 4, 5] Tengah + Telunjuk + Jempol"
10,"[2, 3] Manis + Tengah",26,"[1, 2, 3, 4] Kel, Manis, Tengah, Telunjuk"
11,"[2, 4] Manis + Telunjuk",27,"[1, 2, 3, 5] Kel, Manis, Tengah, Jempol"
12,"[2, 5] Manis + Jempol",28,"[1, 2, 4, 5] Kel, Manis, Telunjuk, Jempol"
13,"[3, 4] Tengah + Telunjuk",29,"[1, 3, 4, 5] Kel, Tengah, Telunjuk, Jempol"
14,"[3, 5] Tengah + Jempol",30,"[2, 3, 4, 5] Manis + Tengah + Telunjuk + Jempol"
15,"[4, 5] Telunjuk + Jempol",31,"[1, 2, 3, 4, 5] Semua Jari (Full Hand)"
16,"[1, 2, 3] Kelingking, Manis, Tengah",,
*(Lihat daftar lengkap di folder `docs` atau file script untuk semua 31 kombinasi).*

## ⚠️ Disclaimer

Proyek ini dibuat untuk tujuan **edukasi, aksesibilitas, dan archival**. Pengembang tidak bertanggung jawab atas penyalahgunaan alat ini di luar ketentuan hukum yang berlaku.
