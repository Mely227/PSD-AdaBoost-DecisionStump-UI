# Dashboard Prediksi Niat Beli Pengunjung (versi Python / Streamlit)

Terjemahan dari versi PHP. Angka dan gambar sudah dihitung ulang pada dataset 12.330 sesi (17 fitur + 1 target Revenue, 26 fitur setelah encoding). Butuh Python 3.9 atau lebih baru.

## Cara menjalankan
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run frontend/app.py
```
Browser akan terbuka di `http://localhost:8501`.

## Struktur
**backend/** (data dan logika)
- `data.py`     : semua angka dari notebook dan identitas (nama, NIM). Edit di sini
- `helpers.py`  : format angka gaya Indonesia, statistik, pembuat SVG pohon stump
- `skema.py`    : arti tiap kolom dataset dan perlakuannya
- `dataset/`    : letakkan file CSV dataset di sini (opsional, atau unggah lewat sidebar)

**frontend/** (tampilan Streamlit)
- `app.py`       : menyusun halaman (sidebar, hero, daftar tab, footer)
- `tab_data.py`  : tab Dataset, Fitur & Target, Preprocessing, Tahapan (rumus + perhitungan)
- `tab_model.py` : tab Metrik, Eksplorasi, Cross-validation, Pohon, Tuning, Evaluasi, Simulator, Galeri
- `animasi.py`   : animasi hero, alur kerja, dan jaringan fitur-target (HTML/SVG/CSS)
- `ui.py`        : palet warna, gaya grafik, kartu, tabel
- `gaya.css`     : seluruh CSS halaman
- `assets/`      : gambar dari notebook

## Padanan dengan versi PHP
| PHP / JavaScript            | Python / Streamlit                 |
|-----------------------------|------------------------------------|
| `data/data.php`             | `data.py`                          |
| `includes/helpers.php`      | `helpers.py`                       |
| `includes/section_*.php`    | fungsi `render_*` di `tab_data.py` / `tab_model.py`, disusun lewat `st.tabs` di `app.py`              |
| Chart.js                    | Plotly                             |
| Modal / pop-up Bootstrap    | `st.popover`, `st.dialog`, `st.toast` |
| Kamus istilah (offcanvas)   | Sidebar                            |
