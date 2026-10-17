# E-Commerce Data Analysis

## Deskripsi
Proyek analisis data akhir (Dicoding, kelas *Belajar Fundamental Analisis Data*) yang menganalisis transaksi marketplace e-commerce di Brasil: **kategori produk dengan revenue tertinggi**, **tren pesanan dan revenue bulanan**, serta **hubungan keterlambatan pengiriman dengan skor ulasan pelanggan**. Sebagai analisis lanjutan, pelanggan disegmentasi dengan **RFM Analysis** (tanpa machine learning). Hasilnya ditampilkan pada dashboard Streamlit interaktif.

Alur analisis: Business Questions → Data Wrangling (Gathering, Assessing, Cleaning) → EDA → Visualization & Explanatory Analysis → Analisis Lanjutan (RFM) → Conclusion & Recommendation.

## Dataset
**E-Commerce Public Dataset** (data pesanan marketplace Brasil, September 2016 – Oktober 2018). Tujuh dari sembilan file dipakai dan disimpan di folder `data/`:

| File | Fungsi |
|---|---|
| `orders_dataset.csv` | Status dan timestamp pesanan |
| `order_items_dataset.csv` | Item, produk, dan harga per pesanan (revenue) |
| `products_dataset.csv` | Kategori produk |
| `product_category_name_translation.csv` | Terjemahan nama kategori ke bahasa Inggris |
| `order_reviews_dataset.csv` | Skor ulasan pelanggan |
| `customers_dataset.csv` | `customer_unique_id` dan negara bagian pelanggan |
| `order_payments_dataset.csv` | Nilai pembayaran (komponen Monetary pada RFM) |

`geolocation_dataset.csv` dan `sellers_dataset.csv` tidak dipakai karena tidak dibutuhkan oleh pertanyaan bisnis.

**Cakupan analisis:** pesanan berstatus `delivered` yang dibeli **1 Januari 2017 – 31 Agustus 2018** (96.211 pesanan). Periode ini dipilih karena tahun 2016 serta September–Oktober 2018 hanya berisi sedikit pesanan (terbukti pada tahap Assessing).

## Business Questions
1. **Kategori Produk dengan Revenue Tertinggi:** Kategori produk apa saja yang menghasilkan total revenue produk tertinggi dari pesanan delivered selama 1 Januari 2017 – 31 Agustus 2018, dan berapa persen kontribusi 10 kategori teratas terhadap total revenue?
2. **Tren Bulanan Pesanan dan Revenue:** Bagaimana tren jumlah pesanan dan total revenue produk per bulan selama Januari 2017 – Agustus 2018, bulan mana yang menjadi puncak, dan berapa persen pertumbuhan Januari–Agustus 2018 dibanding Januari–Agustus 2017?
3. **Keterlambatan Pengiriman dan Skor Ulasan Pelanggan:** Berapa selisih rata-rata skor ulasan antara pesanan terlambat dan tepat waktu selama Januari 2017 – Agustus 2018, berapa persen pesanan terlambat, dan negara bagian mana yang tingkat keterlambatannya tertinggi?

## Insight Utama
- **BQ1:** kategori teratas adalah `health_beauty` (9,3%), `watches_gifts` (8,8%), dan `bed_bath_table` (7,8%). Sepuluh kategori teratas menyumbang **62,5%** dari total revenue produk (R$ 13.181.027).
- **BQ2:** puncak pesanan pada **Nov 2017** (7.289 pesanan), terpusat pada 2017-11-24 (1.147 pesanan dalam sehari). Jan–Agu 2018 tumbuh **+139,9%** (pesanan) dan **+141,1%** (revenue) dibanding Jan–Agu 2017.
- **BQ3:** 8,01% pesanan terlambat. Rata-rata skor ulasan 4,29 (tepat waktu) vs 2,57 (terlambat). Keterlambatan tertinggi di MA (19,3%), CE (15,3%), dan BA (13,7%).
- **RFM:** 97,0% pelanggan hanya membeli satu kali; pelanggan *High-Value* satu pesanan (30,2% pelanggan) menyumbang 55,7% total pembayaran.
- **Kualitas data:** kolom tanggal bertipe string; timestamp kosong atau tidak konsisten; risiko duplikasi saat join (ulasan dan pembayaran); kategori produk hilang; periode data tidak merata. Seluruhnya ditangani pada notebook.

## Struktur Project
```
submission/
├── dashboard/
│   ├── main_data.csv      # data bersih hasil notebook (1 baris per item pesanan)
│   └── dashboard.py       # aplikasi Streamlit
├── data/
│   ├── customers_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   └── products_dataset.csv
├── notebook.ipynb         # proses analisis data lengkap
├── README.md
├── requirements.txt
└── url.txt                # URL dashboard yang sudah di-deploy
```

## Persyaratan
- Python 3.9 atau lebih baru
- pip (package manager Python)
- Library (lihat `requirements.txt`): NumPy, Pandas, Matplotlib, Seaborn (notebook), Streamlit, Plotly (dashboard)

## Setup Environment
Disarankan memakai virtual environment agar library proyek ini tidak bercampur dengan proyek lain.

1. Buka terminal (Command Prompt/PowerShell di Windows, Terminal di macOS/Linux) lalu masuk ke folder proyek:
   ```
   cd submission
   ```
2. Buat virtual environment:
   ```
   python -m venv .venv
   ```
3. Aktifkan virtual environment:
   - Windows:
     ```
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source .venv/bin/activate
     ```
   Jika berhasil, tulisan `(.venv)` muncul di awal baris terminal.

## Instalasi Dependency
Dengan virtual environment aktif dan berada di folder `submission/`:
```
pip install -r requirements.txt
```

## Menjalankan Dashboard
Masuk ke folder dashboard lalu jalankan Streamlit:
```
cd dashboard
streamlit run dashboard.py
```
Browser akan terbuka otomatis. Jika tidak, buka alamat yang tampil di terminal (biasanya `http://localhost:8501`). Untuk menghentikan dashboard, tekan `Ctrl+C`.

Alternatif dari folder `submission/` (tanpa `cd dashboard`):
```
streamlit run dashboard/dashboard.py
```

## Menjalankan Notebook (opsional)
Jalankan dari folder `submission/` agar folder `data/` terbaca:
```
pip install jupyter
jupyter notebook notebook.ipynb
```
Lalu pilih *Restart & Run All*. Di Google Colab, unggah file CSV ke folder `data/` (atau ke direktori yang sama dengan notebook) sebelum menjalankan sel.

## Dashboard Online
URL deployment tercantum di `url.txt` (diisi setelah dashboard di-deploy ke Streamlit Cloud).

## Fitur Dashboard
**Visualisasi untuk tiga Business Questions**
- **BQ1 (tab "BQ1: Kategori Produk"):** grafik batang horizontal kategori dengan revenue tertinggi beserta persentase kontribusinya.
- **BQ2 (tab "BQ2: Tren Bulanan"):** dua grafik garis, jumlah pesanan per bulan dan revenue produk per bulan, beserta bulan puncak dan pertumbuhan Jan–Agu 2018 vs 2017.
- **BQ3 (tab "BQ3: Keterlambatan & Ulasan"):** rata-rata skor ulasan pesanan tepat waktu vs terlambat, skor menurut lama keterlambatan, dan persentase pesanan terlambat per negara bagian.

**Visualisasi pendukung:** tab "Segmentasi RFM" menampilkan jumlah pelanggan per segmen RFM (hasil analisis lanjutan di notebook).

**Fitur interaktif (sidebar)**
- **Periode pembelian** (pemilih rentang tanggal)
- **Kategori produk** (pilihan ganda)
- **Negara bagian pelanggan** (pilihan ganda)
- **Jumlah kategori teratas** (slider, BQ1) dan **minimal pesanan per negara bagian** (slider, BQ3)

Perubahan filter langsung memperbarui KPI (pesanan, revenue, pelanggan unik, persentase terlambat, rata-rata skor), seluruh grafik, dan teks insight. Jika kombinasi filter tidak menghasilkan data, dashboard menampilkan peringatan tanpa error.

**Catatan metodologi dashboard:** `main_data.csv` berisi satu baris per item pesanan. Jumlah pesanan dan pelanggan dihitung dari kode unik (`order_code`, `customer_code`) sehingga tidak terhitung ganda; revenue adalah jumlah `price` (tidak termasuk ongkos kirim). Pada tanpa-filter, seluruh angka identik dengan notebook.

## Author
M Fahril Luthfi — Sistem Informasi, Universitas Islam Negeri Sultan Syarif Kasim Riau
