# 📸 BendolSort

[![Python Version](https://img.shields.io/badge/python-3.10+-00A3FF?style=flat-proportional\&logo=python\&logoColor=white)](https://www.python.org)
[![Framework](https://img.shields.io/badge/UI%20Framework-PyQt5-00A3FF?style=flat-proportional\&logo=qt\&logoColor=white)](https://www.qt.io/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-proportional)](LICENSE)

**BendolSort** adalah aplikasi manajemen dan kurasi foto *all-in-one* berbasis desktop yang dirancang khusus untuk fotografer, kreator konten, dan editor visual. Aplikasi ini berfokus pada kecepatan dan efisiensi, memungkinkan kamu memilah ribuan foto mentah (*raw files*) dalam hitungan menit hanya menggunakan shortcut keyboard.

---

## ✨ Fitur Utama

* **Ultra-Fast Sorting:** Pilah foto ke folder target (`SELECT`, `MAYBE`, `REJECT`) instan dengan satu ketukan tombol.
* **Multi-Format Support:** Mendukung format gambar standar (`.jpg`, `.jpeg`, `.png`) hingga file RAW profesional (`.arw`, `.cr2`, `.cr3`, `.nef`, `.dng`, `.raf`).
* **EXIF Metadata Reader:** Menampilkan informasi kamera langsung di panel info saat foto dimuat.
* **Client Auto Sort (Bento Grid Integration Ready):** Punya daftar nama file dari klien? Cukup *paste* daftarnya, dan BendolSort akan menyortirnya secara otomatis.
* **Modern Dark UI:** Antarmuka minimalis dengan tema *deep charcoal* dan aksen *electric blue* yang nyaman di mata untuk sesi kerja yang lama.
* **Cross-Platform:** Tersedia untuk Windows, Linux, dan macOS.

---

## ⌨️ Shortcut Keyboard (Default)

| Aksi         | Shortcut                          | Keterangan                                      |
| ------------ | --------------------------------- | ----------------------------------------------- |
| **SELECT**   | `1`                               | Menyalin foto aktif ke folder tujuan **Accept** |
| **MAYBE**    | `2`                               | Menyalin foto aktif ke folder tujuan **Maybe**  |
| **REJECT**   | `3`                               | Menyalin foto aktif ke folder tujuan **Reject** |
| **NEXT**     | `→`                               | Berpindah ke foto selanjutnya                   |
| **PREV**     | `←`                               | Kembali ke foto sebelumnya                      |
| **ZOOM IN**  | `Ctrl + +` / `Ctrl + Scroll Up`   | Memperbesar tampilan                            |
| **ZOOM OUT** | `Ctrl + -` / `Ctrl + Scroll Down` | Memperkecil tampilan                            |

> ⚙️ **Tips:** Kamu bisa mengubah seluruh shortcut di atas melalui menu **Settings (Ikon Gear)** di dalam aplikasi.

---

## 🚀 Cara Menggunakan

### 🔹 Cara Instan (Rekomendasi)

1. Pergi ke tab **Releases** di repository GitHub.
2. Unduh file sesuai sistem operasi:

* **Windows:** `BendolSort-Windows.exe`
* **Linux:** `BendolSort-Linux`
  Jalankan dengan:

  ```bash
  chmod +x BendolSort-Linux
  ./BendolSort-Linux
  ```
* **macOS:** `BendolSort-MacOS.dmg`

---

### 🔹 Cara Manual (Developer)

1. **Clone repository:**

```bash
git clone https://github.com/CalvinBendol/BendolSort-Sorting-Photo.git
cd BendolSort-Sorting-Photo
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Jalankan aplikasi:**

```bash
python main.py
```

---

## 🛠️ Struktur Proyek

```plaintext
BendolSort/
├── .github/workflows/
│   └── build.yml       # CI/CD lintas OS via GitHub Actions
├── main.py             # Logika utama & UI PyQt5
├── requirements.txt    # Dependensi Python
└── README.md           # Dokumentasi proyek
```

---

## 👨‍💻 Pembuat

**Muhamad Calvin Alfiansyah**
(@calvinbendol)

* Freelance Graphic Designer
* Content Creator
* Developer

📍 Lumajang, Jawa Timur, Indonesia

---

## 📄 Lisensi

Proyek ini menggunakan lisensi **MIT License**.
Bebas digunakan, dimodifikasi, dan didistribusikan secara terbuka.

