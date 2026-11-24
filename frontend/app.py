"""Dashboard Prediksi Niat Beli Pengunjung (versi Python / Streamlit).

Jalankan dari folder utama dengan:  streamlit run frontend/app.py

File ini hanya menyusun halaman. Isi tiap tab ada di file lain:
    tab_data.py   -> Dataset, Fitur & Target, Preprocessing, Tahapan
    tab_model.py  -> Metrik, Eksplorasi, Cross-validation, Pohon, Tuning, Evaluasi, Simulator, Galeri
    animasi.py    -> animasi hero
    ui.py         -> kartu, tabel, gaya grafik
    gaya.css      -> seluruh CSS (satu file, dibagi per bagian)
    gaya.py       -> pemuat gaya.css
Angka dan identitas dibaca dari backend/data.py.
"""
import sys
from pathlib import Path

# Agar modul di folder backend/ (data, helpers, skema) bisa diimpor
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import streamlit as st
import streamlit.components.v1 as components

from animasi import hero_html
from data import DATA, ISTILAH
from gaya import muat_css
from tab_data import ambil_df, render_data, render_fitur, render_prep, render_tahap
from tab_model import (render_cv, render_eksplorasi, render_evaluasi, render_galeri,
                       render_metrik, render_pohon, render_simulator, render_tuning)

ID = DATA["identitas"]


# ================================================================ PENGATURAN HALAMAN
def pasang_gaya():
    """Pasang CSS bagian \"halaman\" dari gaya.css (termasuk latar belakang animasi)."""
    st.markdown(f"<style>\n{muat_css('halaman')}\n</style>", unsafe_allow_html=True)


@st.dialog("Selamat datang")
def sambutan():
    """Pop-up sambutan."""
    st.write("Dashboard ini merangkum hasil model AdaBoost untuk memprediksi pengunjung yang akan membeli. "
             "Beberapa hal yang bisa dicoba:")
    st.markdown(
        "- **Kartu metrik**: klik tombol *Penjelasan*\n"
        "- **Pohon stump**: pilih stump, lalu pilih kotaknya\n"
        "- **Simulator**: geser slider\n"
        "- **Sidebar**: kamus istilah singkat")
    st.button("Mulai menjelajah", type="primary")


def tampilkan_sambutan_sekali():
    """Pop-up hanya muncul satu kali per sesi."""
    if "sudah_sambut" not in st.session_state:
        st.session_state.sudah_sambut = True
        sambutan()


def render_sidebar():
    """Sidebar: unggah dataset dan kamus istilah."""
    with st.sidebar:
        st.header("Dataset")
        st.file_uploader("Unggah CSV dataset (opsional)", type="csv", key="upload",
                         help="Atau letakkan file .csv di folder backend/dataset/")
        st.header("Kamus istilah")
        for i, (istilah, arti) in enumerate(ISTILAH):
            with st.expander(istilah, expanded=(i == 0)):
                st.write(arti)


def render_footer():
    st.divider()
    st.caption(f"{ID['nama']} · {ID['nim']} · Tugas {ID['matkul']}  \nDataset Online Shoppers Purchasing Intention")


# ================================================================ HALAMAN UTAMA
def main():
    st.set_page_config(page_title=ID["judul"], page_icon="🛒", layout="wide")
    pasang_gaya()
    tampilkan_sambutan_sekali()
    render_sidebar()

    components.html(hero_html(DATA), height=440)
    df, sumber = ambil_df()   # DataFrame dari CSV (atau None bila belum ada)

    # Pasangan (judul tab, fungsi yang mengisi tab), sesuai urutan tampil
    daftar_tab = [
        ("📦 Dataset",         lambda: render_data(df, sumber)),
        ("🎯 Fitur & Target",  lambda: render_fitur(df, sumber)),
        ("🧹 Preprocessing",   lambda: render_prep(df, sumber)),
        ("🧮 Tahapan",         render_tahap),
        ("Metrik",             render_metrik),
        ("Eksplorasi",         render_eksplorasi),
        ("Cross-validation",   render_cv),
        ("Pohon",              render_pohon),
        ("Tuning",             render_tuning),
        ("Evaluasi",           render_evaluasi),
        ("Simulator",          render_simulator),
        ("Galeri",             render_galeri),
    ]
    tab_st = st.tabs([judul for judul, _ in daftar_tab])
    for tab, (_, render) in zip(tab_st, daftar_tab):
        with tab:
            render()

    render_footer()


main()
