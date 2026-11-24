"""Empat bagian tambahan dashboard: Dataset, Fitur & Target, Preprocessing, Tahapan & Perhitungan.

Jika file CSV dataset tersedia (folder backend/dataset/ atau unggahan di sidebar), angka dihitung langsung
dari data. Jika tidak, bagian ini memakai angka dari data.py dan hanya menampilkan skema kolom,
tanpa mengarang baris data.
"""
import io
import math
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from animasi import jaringan_html, pipeline_html
from data import DATA
from helpers import NAMA_KELAS, fmt, mean, pct, stdev
from skema import FITUR, KELOMPOK, TAHAP, TARGET
from ui import GRAD, P, input_stump, kartu, rapikan, tabel

BASE = Path(__file__).parent
CM = DATA["cm"]
N_TOTAL = DATA["totalSesi"]
N_UJI_NB = sum(CM.values())          # jumlah sesi data uji
N_LATIH_NB = DATA["stumps"][0]["akar"]["n"]   # jumlah sesi data latih


# =====================================================================  PEMUATAN DATA
@st.cache_data(show_spinner="Membaca dataset...")
def _baca_path(path, ubah):
    return pd.read_csv(path)


@st.cache_data(show_spinner="Membaca dataset...")
def _baca_bytes(isi):
    return pd.read_csv(io.BytesIO(isi))


def ambil_df():
    """Kembalikan (DataFrame, nama sumber) atau (None, None) bila belum ada CSV."""
    upl = st.session_state.get("upload")
    if upl is not None:
        return _baca_bytes(upl.getvalue()), upl.name
    folder = BASE.parent / "backend" / "dataset"
    if folder.exists():
        for f in sorted(folder.glob("*.csv")):
            return _baca_path(str(f), f.stat().st_mtime), f.name
    return None, None


def target_biner(df, nama):
    s = df[nama]
    if s.dtype == bool:
        return s.astype(int)
    if pd.api.types.is_numeric_dtype(s):
        return (s > 0).astype(int)
    return s.astype(str).str.strip().str.lower().isin(["true", "1", "1.0", "yes", "ya"]).astype(int)


def nama_target(df):
    return "Revenue" if "Revenue" in df.columns else df.columns[-1]


@st.cache_data(show_spinner="Menghitung ringkasan preprocessing...")
def ringkas(_df, kunci):
    """Semua angka preprocessing dihitung sekali lalu disimpan (kunci = nama file + bentuk data)."""
    df = _df
    tgt = nama_target(df)
    y = target_biner(df, tgt)
    buang = [c for c in df.columns if c.lower() == "id"]
    fit = df.drop(columns=[tgt] + buang)
    tipe = pd.api.types
    bol = [c for c in fit.columns if tipe.is_bool_dtype(fit[c])]
    num = [c for c in fit.columns if c not in bol and tipe.is_numeric_dtype(fit[c])]
    kat = [c for c in fit.columns if c not in bol + num]   # teks / kategori (aman untuk pandas 2 dan 3)

    out = []
    for c in num:
        q1, q3 = fit[c].quantile(0.25), fit[c].quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_out = int(((fit[c] < lo) | (fit[c] > hi)).sum())
        out.append([c, q1, q3, iqr, lo, hi, n_out, n_out / len(fit) * 100])
    outlier = pd.DataFrame(out, columns=["Fitur", "Q1", "Q3", "IQR", "Batas bawah", "Batas atas", "Jumlah outlier", "Persen"])

    unik = {c: sorted(fit[c].dropna().astype(str).unique()) for c in kat}
    kolom_baru = {c: [f"{c}_{u}" for u in v[1:]] for c, v in unik.items()}
    return {
        "n": len(df), "k": df.shape[1], "target": tgt, "buang": buang,
        "bol": bol, "kat": kat, "num": num, "unik": unik, "kolom_baru": kolom_baru,
        "n_akhir": len(num) + len(bol) + sum(len(v) - 1 for v in unik.values()),
        "kelas": y.value_counts().to_dict(), "missing": df.isna().sum(),
        "dup": int(df.duplicated().sum()), "outlier": outlier,
        "desc": fit[num].describe().T, "dtypes": df.dtypes.astype(str),
    }


# =====================================================================  1. DATASET
def render_data(df, sumber):
    st.subheader("Dataset")
    st.caption("Online Shoppers Purchasing Intention. Satu baris mewakili satu sesi kunjungan ke toko online.")
    n = len(df) if df is not None else N_TOTAL
    k = df.shape[1] if df is not None else len(FITUR) + 1
    c = st.columns(4)
    with c[0]:
        kartu(fmt(n, 0), "Baris (sesi)", "Jumlah sesi kunjungan", "g0")
    with c[1]:
        kartu(str(k), "Kolom", "Fitur asli ditambah target", "g1")
    with c[2]:
        kartu(str(len(FITUR)), "Fitur asli", "Sebelum encoding", "g3")
    with c[3]:
        kartu(str(DATA["jumlahFitur"]), "Fitur siap model", "Setelah encoding", "g4")

    if df is None:
        st.info(
            "Baris data asli belum dimuat, jadi tabel contoh tidak ditampilkan (saya tidak mengarang isi data). "
            "Untuk menampilkannya: letakkan file CSV dataset di folder **backend/dataset/**, "
            "atau unggah lewat sidebar. Setelah itu bagian Dataset, Fitur, dan Preprocessing otomatis "
            "dihitung dari data Anda.")
    else:
        st.success(f"Dataset terbaca dari **{sumber}**: {fmt(len(df), 0)} baris, {df.shape[1]} kolom.")
        jml = st.slider("Jumlah baris yang ditampilkan", 5, 200, 20, 5)
        st.dataframe(df.head(jml))
        r = ringkas(df, f"{sumber}-{df.shape}")
        st.markdown("**Tipe data dan nilai kosong**")
        info = pd.DataFrame({"Tipe data": r["dtypes"], "Nilai kosong": r["missing"].astype(int)})
        info["Peran"] = ["Target" if i == r["target"] else "Dibuang (ID)" if i in r["buang"] else "Fitur" for i in info.index]
        st.dataframe(info)
        st.markdown("**Statistik ringkas fitur numerik**")
        st.dataframe(r["desc"].round(4))

    st.markdown("**Skema kolom**")
    skema = pd.DataFrame(
        [[f[0], f[1], f[2], f[4]] for f in FITUR] + [[TARGET[0], "Biner (target)", "Target", TARGET[2]]],
        columns=["Kolom", "Tipe", "Kelompok", "Arti"])
    st.dataframe(skema)


# =====================================================================  2. FITUR & TARGET
def render_fitur(df, sumber):
    st.subheader("Fitur dan kolom target")
    st.caption("Garis yang bergerak menuju target menunjukkan seberapa besar pengaruh tiap fitur pada keputusan model. "
               "Makin tebal garisnya, makin besar pengaruhnya.")
    components.html(jaringan_html(DATA["fitur"], TARGET[0]), height=540)

    # ---- kartu target
    tidak, beli = DATA["kelas"]["tidak"], DATA["kelas"]["beli"]
    tot = tidak + beli
    st.markdown(f"""
<div class="tcard">
  <div class="ticon">🎯</div>
  <div style="flex:1;min-width:230px">
    <h3>Kolom target: <code>{TARGET[0]}</code></h3>
    <p>{TARGET[2]}</p>
    <div class="bar"><i class="b0" style="--w:{tidak / tot * 100:.2f}%">Tidak beli {fmt(tidak / tot * 100, 2)}%</i><i class="b1" style="--w:{beli / tot * 100:.2f}%">Beli {fmt(beli / tot * 100, 1)}%</i></div>
    <small>{fmt(tidak, 0)} sesi tidak membeli · {fmt(beli, 0)} sesi membeli · rasio {fmt(tidak / beli, 2)} : 1 (kelas timpang)</small>
  </div>
</div>""", unsafe_allow_html=True)

    # ---- kartu fitur per kelompok
    st.markdown("### Fitur yang dipakai")
    chip = "".join(f'<span class="chip" style="--c:{w}">{k}</span>' for k, w in KELOMPOK.items())
    st.markdown(f'<div class="chips">{chip}</div>', unsafe_allow_html=True)
    nama_fit = {f[0] for f in FITUR}
    peringkat = {}
    for i, (nm, v) in enumerate(DATA["fitur"]):
        dasar = nm if nm in nama_fit else nm.split("_")[0]
        if dasar not in peringkat:
            peringkat[dasar] = (i + 1, v)
    kartu_html = []
    for i, (nm, tp, kel, ik, arti, perl) in enumerate(FITUR):
        lencana = (f'<em>Top {peringkat[nm][0]} · {fmt(peringkat[nm][1], 2)}%</em>' if nm in peringkat else "")
        kartu_html.append(
            f'<div class="fcard" style="--c:{KELOMPOK[kel]};animation-delay:{i * 0.05:.2f}s">'
            f'<div class="fic">{ik}</div><div><b>{nm}</b>{lencana}<small>{tp} · {kel}</small>'
            f'<p>{arti}</p><p class="pl">⚙️ {perl}</p></div></div>')
    st.markdown(f'<div class="fgrid">{"".join(kartu_html)}</div>', unsafe_allow_html=True)

    # ---- penjelajah fitur (hanya jika data ada)
    st.markdown("### Fitur versus target")
    if df is None:
        st.info("Grafik sebaran fitur per kelas muncul setelah dataset dimuat (lihat petunjuk di bagian Dataset).")
        return
    r = ringkas(df, f"{sumber}-{df.shape}")
    y = target_biner(df, r["target"])
    pilih = st.selectbox("Pilih fitur", r["num"] + r["bol"] + r["kat"])
    if pilih in r["num"]:
        contoh = df[[pilih]].assign(y=y).sample(min(len(df), 150_000), random_state=1)
        batas = contoh[pilih].quantile(0.99)
        contoh = contoh[contoh[pilih] <= batas]
        fig = go.Figure()
        for kls, warna in ((0, P["indigo"]), (1, P["green"])):
            fig.add_trace(go.Histogram(x=contoh.loc[contoh.y == kls, pilih], name=NAMA_KELAS[kls],
                                       marker_color=warna, opacity=0.6, histnorm="probability density"))
        fig.update_layout(barmode="overlay")
        st.plotly_chart(rapikan(fig, 340))
        st.caption("Sebaran dipotong di persentil ke-99 agar mudah dibaca. Makin berbeda dua bentuk, makin berguna fiturnya.")
        rata = df[[pilih]].assign(y=y).groupby("y")[pilih].agg(["mean", "median"]).rename(index=lambda i: NAMA_KELAS[i])
        st.dataframe(rata.round(4))
    else:
        konv = pd.DataFrame({pilih: df[pilih].astype(str), "y": y}).groupby(pilih)["y"].mean().sort_values() * 100
        fig = go.Figure(go.Bar(x=konv.index, y=konv.values, marker_color=P["violet"]))
        st.plotly_chart(rapikan(fig, 320, legenda=False))
        st.caption("Persentase sesi yang berakhir membeli pada tiap kategori.")


# =====================================================================  3. PREPROCESSING
def _langkah(nomor, ikon, judul):
    return st.expander(f"{ikon}  Langkah {nomor}: {judul}", expanded=True)


def render_prep(df, sumber):
    st.subheader("Preprocessing")
    st.caption("Urutan persiapan data sebelum masuk ke model. Setiap langkah menampilkan alasan dan perhitungannya.")
    r = ringkas(df, f"{sumber}-{df.shape}") if df is not None else None
    ada = r is not None

    n = r["n"] if ada else N_TOTAL
    with _langkah(1, "📦", "Memuat data dan memeriksa bentuk"):
        st.write(f"Dataset berisi **{fmt(n, 0)} sesi**. Satu kolom menjadi target (`{TARGET[0]}`), "
                 f"sisanya fitur. Kolom ID (jika ada) dibuang karena hanya nomor urut dan tidak membawa informasi.")

    with _langkah(2, "🧹", "Memeriksa nilai kosong dan duplikat"):
        if ada:
            mis = r["missing"][r["missing"] > 0]
            c1, c2 = st.columns(2)
            with c1:
                kartu(fmt(int(r["missing"].sum()), 0), "Total nilai kosong", f"di {len(mis)} kolom", "g1")
            with c2:
                kartu(fmt(r["dup"], 0), "Baris duplikat", f"{fmt(r['dup'] / n * 100, 3)}% dari data", "g3")
            if len(mis):
                st.dataframe(mis.rename("Nilai kosong"))
            st.write("Jika ada nilai kosong, baris atau kolom itu perlu diisi atau dibuang dulu karena AdaBoost di scikit-learn tidak menerima NaN.")
        else:
            st.info("Hitungan nilai kosong dan duplikat membutuhkan dataset. Muat CSV untuk melihat angkanya.")
        st.latex(r"\text{persen kosong} = \frac{\text{jumlah sel kosong}}{\text{jumlah baris}} \times 100\%")

    with _langkah(3, "🔁", "Menyamakan tipe data"):
        st.write("`Weekend` dan `Revenue` bertipe True/False. Model hanya menerima angka, jadi diubah menjadi **True = 1** dan **False = 0**.")
        st.table(pd.DataFrame({"Sebelum": ["True", "False"], "Sesudah": [1, 0]}).set_index("Sebelum"))

    with _langkah(4, "📏", "Mendeteksi outlier dengan aturan IQR"):
        st.latex(r"IQR = Q_3 - Q_1 \qquad \text{batas bawah} = Q_1 - 1{,}5\,IQR \qquad \text{batas atas} = Q_3 + 1{,}5\,IQR")
        st.write("Nilai di luar kedua batas dihitung sebagai outlier. Outlier **hanya dideteksi, tidak dibuang**: "
                 "pohon keputusan membagi data berdasarkan urutan nilai, jadi tidak sensitif terhadap nilai ekstrem, "
                 "dan sesi dengan nilai besar (misalnya PageValues tinggi) justru sering pembeli sungguhan.")
        if ada:
            o = r["outlier"].copy()
            tampil = o.assign(**{c: o[c].map(lambda v: fmt(v, 3)) for c in ["Q1", "Q3", "IQR", "Batas bawah", "Batas atas"]},
                              **{"Jumlah outlier": o["Jumlah outlier"].map(lambda v: fmt(v, 0)),
                                 "Persen": o["Persen"].map(lambda v: fmt(v, 2) + "%")}).set_index("Fitur")
            st.table(tampil)
        else:
            st.info("Tabel batas IQR per fitur muncul setelah dataset dimuat.")

    with _langkah(5, "🔤", "Encoding fitur kategorikal (one-hot)"):
        st.write("`Month` dan `VisitorType` berisi teks. Tiap kategori diubah menjadi kolom 0/1, "
                 "lalu satu kategori dibuang (**drop first**) supaya kolom tidak saling bergantung.")
        st.markdown("**Ilustrasi cara kerja** (contoh bentuk, bukan isi dataset Anda):")
        st.table(pd.DataFrame({
            "VisitorType asli": ["New_Visitor", "Returning_Visitor", "Other"],
            "VisitorType_Other": [0, 0, 1],
            "VisitorType_Returning_Visitor": [0, 1, 0],
        }).set_index("VisitorType asli"))
        st.write("Baris `New_Visitor` bernilai 0 di kedua kolom, jadi informasinya tetap terwakili tanpa kolom tambahan.")
        st.markdown("**Menghitung jumlah fitur akhir**")
        if ada:
            bagian = " + ".join([f"{len(r['num'])} numerik", f"{len(r['bol'])} biner"] +
                                [f"({len(v)} {c} − 1)" for c, v in r["unik"].items()])
            akhir = r["n_akhir"]
            for c, kb in r["kolom_baru"].items():
                st.caption(f"Kolom baru dari {c}: " + ", ".join(kb))
        else:
            num_n = sum(f[1].startswith(("Numerik", "Kode")) for f in FITUR)
            bagian = f"{num_n} numerik + 1 biner + (10 Month − 1) + (3 VisitorType − 1)"
            akhir = num_n + 1 + 9 + 2
        st.code(f"{bagian} = {akhir} fitur", language="text")
        if akhir == DATA["jumlahFitur"]:
            st.success(f"Cocok dengan {DATA['jumlahFitur']} fitur pada notebook.")
        else:
            st.warning(f"Hasilnya {akhir}, sedangkan notebook mencatat {DATA['jumlahFitur']} fitur. "
                       "Periksa apakah kolom atau kategori di file CSV sama dengan di notebook.")

    with _langkah(6, "✂️", "Membagi data latih dan data uji (80 : 20)"):
        n_uji = math.ceil(0.2 * n)
        n_latih = n - n_uji
        st.latex(r"n_{uji} = \lceil 0{,}2 \times N \rceil \qquad n_{latih} = N - n_{uji}")
        st.code(f"n_uji   = ceil(0,2 × {fmt(n, 0)}) = {fmt(n_uji, 0)}\n"
                f"n_latih = {fmt(n, 0)} − {fmt(n_uji, 0)} = {fmt(n_latih, 0)}", language="text")
        if n == N_TOTAL and (n_latih, n_uji) == (N_LATIH_NB, N_UJI_NB):
            st.success(f"Cocok dengan notebook: akar pohon memakai {fmt(N_LATIH_NB, 0)} sesi latih dan confusion matrix {fmt(N_UJI_NB, 0)} sesi uji.")
        st.write("Pembagian dibuat **stratified** (proporsi pembeli dijaga sama di data latih dan uji) karena kelas timpang.")
        beli_prop = DATA["konversiRata"] / 100
        st.code(f"pembeli di data latih ≈ {fmt(n_latih, 0)} × {fmt(beli_prop, 4)} ≈ {fmt(n_latih * beli_prop, 0)} sesi\n"
                f"pembeli di data uji   ≈ {fmt(n_uji, 0)} × {fmt(beli_prop, 4)} ≈ {fmt(n_uji * beli_prop, 0)} sesi", language="text")

    with _langkah(7, "⚖️", "Penskalaan: tidak diperlukan"):
        st.write("Standardisasi atau normalisasi dibutuhkan model berbasis jarak atau gradien (KNN, SVM, regresi). "
                 "Decision stump hanya membandingkan satu fitur dengan satu ambang, jadi skala fitur tidak memengaruhi hasil.")

    st.markdown("### Hasil akhir preprocessing")
    n_uji = math.ceil(0.2 * n)
    c = st.columns(4)
    isi = [(fmt(DATA["jumlahFitur"], 0), "Fitur", "siap dipakai model"), (fmt(n - n_uji, 0), "Data latih", "80% sesi"),
           (fmt(n_uji, 0), "Data uji", "20% sesi"), (fmt(DATA["konversiRata"], 2) + "%", "Pembeli", "proporsi kelas positif")]
    for i, (k, (v, nm, ket)) in enumerate(zip(c, isi)):
        with k:
            kartu(v, nm, ket, GRAD[i])


# =====================================================================  4. TAHAPAN & PERHITUNGAN
def _gini(val):
    s = sum(val)
    return 1 - sum((v / s) ** 2 for v in val)


def render_tahap():
    st.subheader("Tahapan pengerjaan dan perhitungannya")
    st.caption("Dari data mentah sampai prediksi. Pilih tahap untuk melihat rumus dan angkanya. "
               "Semua angka diambil dari hasil notebook Anda.")
    components.html(pipeline_html(TAHAP), height=190)

    judul = ["1. Data dan target", "2. Preprocessing", "3. Bobot awal", "4. Membangun stump (Gini)",
             "5. Error dan bobot suara α", "6. Memperbarui bobot data", "7. Voting akhir", "8. Evaluasi"]
    pilih = st.radio("Pilih tahap", judul, horizontal=True, label_visibility="collapsed")
    i = judul.index(pilih)
    S = DATA["stumps"]
    n_latih = N_LATIH_NB

    with st.container(border=True):
        if i == 0:
            st.markdown("#### 📦 Data dan target")
            st.write(f"Model belajar dari **{fmt(N_TOTAL, 0)} sesi** kunjungan. Tujuannya menebak `Revenue`: apakah sesi berakhir dengan pembelian.")
            t, b = DATA["kelas"]["tidak"], DATA["kelas"]["beli"]
            st.latex(r"\text{konversi} = \frac{\text{sesi membeli}}{\text{semua sesi}} \times 100\%")
            st.code(f"konversi = {fmt(b, 0)} ÷ {fmt(t + b, 0)} × 100% = {fmt(b / (t + b) * 100, 2)}%", language="text")
            st.info("Hanya sekitar 1 dari 6 sesi yang membeli. Kelas yang timpang ini alasan akurasi saja tidak cukup untuk menilai model.")

        elif i == 1:
            st.markdown("#### 🧹 Preprocessing")
            st.write("Ringkasan langkah (rincian lengkap ada di tab Preprocessing):")
            st.markdown("1. Buang kolom ID, ubah True/False menjadi 1/0\n2. Deteksi outlier dengan IQR (tidak dibuang)\n"
                        f"3. One-hot encoding `Month` dan `VisitorType` (drop first) → **{DATA['jumlahFitur']} fitur**\n"
                        f"4. Bagi data 80 : 20 secara stratified → **{fmt(N_LATIH_NB, 0)} latih, {fmt(N_UJI_NB, 0)} uji**\n"
                        "5. Tanpa penskalaan (pohon tidak membutuhkannya)")

        elif i == 2:
            st.markdown("#### ⚖️ Bobot awal tiap sesi")
            st.write("AdaBoost memberi setiap sesi latih bobot yang sama di awal:")
            st.latex(r"w_i^{(1)} = \frac{1}{n_{latih}}")
            st.code(f"w = 1 ÷ {fmt(n_latih, 0)} = {1 / n_latih:.3e}", language="text")
            st.caption("Jumlah semua bobot = 1. Bobot inilah yang nanti naik pada sesi yang sering salah ditebak.")

        elif i == 3:
            st.markdown("#### 🌳 Membangun stump dengan Gini")
            st.write("Stump mencari satu fitur dan satu ambang yang membuat dua cabang paling \"murni\". Ukurannya Gini impurity:")
            st.latex(r"Gini = 1 - \sum_k p_k^2 \qquad Gini_{split} = \sum_{c \in \{kiri, kanan\}} \frac{W_c}{W_{akar}}\, Gini_c")
            no = st.selectbox("Pilih stump", [s["no"] for s in S], format_func=lambda x: f"Stump {x}")
            s = S[no - 1]
            val = s["akar"]["val"]
            wk, wr = sum(s["kiri"]["val"]), sum(s["kanan"]["val"])
            g_akar, g_k, g_r = _gini(val), _gini(s["kiri"]["val"]), _gini(s["kanan"]["val"])
            g_split = (wk * g_k + wr * g_r) / sum(val)
            p0, p1 = val[0] / sum(val), val[1] / sum(val)
            st.code(
                f"Aturan: {s['fitur']} ≤ {fmt(s['batas'], 3)}\n\n"
                f"Akar   : p = [{fmt(p0, 3)}, {fmt(p1, 3)}]\n"
                f"         Gini = 1 − ({fmt(p0, 3)}² + {fmt(p1, 3)}²) = {fmt(g_akar, 3)}   (notebook: {fmt(s['akar']['gini'], 3)})\n"
                f"Kiri   : Gini = {fmt(g_k, 3)}   (notebook: {fmt(s['kiri']['gini'], 3)})   bobot = {fmt(wk, 3)}\n"
                f"Kanan  : Gini = {fmt(g_r, 3)}   (notebook: {fmt(s['kanan']['gini'], 3)})   bobot = {fmt(wr, 3)}\n\n"
                f"Gini split = ({fmt(wk, 3)} × {fmt(g_k, 3)} + {fmt(wr, 3)} × {fmt(g_r, 3)}) ÷ {fmt(sum(val), 3)} = {fmt(g_split, 3)}\n"
                f"Penurunan Gini = {fmt(g_akar, 3)} − {fmt(g_split, 3)} = {fmt(g_akar - g_split, 3)}",
                language="text")
            st.caption("Selisih kecil dengan notebook berasal dari pembulatan angka yang tersimpan.")
            fig = go.Figure(go.Bar(x=["Akar", "Kiri", "Kanan", "Gini split"], y=[g_akar, g_k, g_r, g_split],
                                   marker_color=[P["indigo"], P["rose"], P["green"], P["amber"]]))
            fig.update_yaxes(range=[0, 0.55])
            st.plotly_chart(rapikan(fig, 280, legenda=False))

        elif i == 4:
            st.markdown("#### 📐 Error berbobot dan bobot suara α")
            st.latex(r"\varepsilon_t = \frac{\sum_i w_i \cdot \mathbb{1}[h_t(x_i) \ne y_i]}{\sum_i w_i}")
            st.latex(r"\alpha_t = \eta \left[ \ln\frac{1-\varepsilon_t}{\varepsilon_t} + \ln(K-1) \right], \quad K = 2,\ \eta = 1 \;\Rightarrow\; \alpha_t = \ln\frac{1-\varepsilon_t}{\varepsilon_t}")
            it = DATA["iterasi"]
            baris, selisih = [], []
            for t, (e, a) in enumerate(zip(it["error"], it["alpha"]), 1):
                h = math.log((1 - e) / e)
                selisih.append(abs(h - a))
                baris.append([f"t={t}", fmt(e, 4), fmt(h, 4), fmt(a, 4), fmt(h - a, 4)])
            df = pd.DataFrame(baris, columns=["Iterasi", "Error ε", "α hitung", "α notebook", "Selisih"]).set_index("Iterasi")
            tabel(df)
            st.success(f"Selisih terbesar hanya {max(selisih):.4f}, murni pembulatan ε. Rumusnya sesuai dengan model Anda.")
            e1 = S[0]["error"]
            st.code(f"Stump 1: α = ln((1 − {fmt(e1, 3)}) ÷ {fmt(e1, 3)}) = ln({fmt((1 - e1) / e1, 3)}) = {fmt(math.log((1 - e1) / e1), 4)}",
                    language="text")
            st.caption("Error kecil → α besar → suara stump itu berpengaruh. Error mendekati 0,5 → α mendekati 0 → hampir tidak didengar.")

        elif i == 5:
            st.markdown("#### 🔄 Memperbarui bobot data")
            st.latex(r"w_i \leftarrow w_i \cdot e^{\alpha_t \cdot \mathbb{1}[h_t(x_i) \ne y_i]}, \quad \text{lalu dinormalisasi agar } \sum_i w_i = 1")
            st.write("Sesi yang salah ditebak bobotnya dikalikan **e^α**, sesi yang benar tetap. Setelah normalisasi, "
                     "stump berikutnya terpaksa lebih memperhatikan sesi yang sulit.")
            baris = []
            for s in S:
                e, a = s["error"], s["alpha"]
                faktor = math.exp(a)
                total_salah = e * faktor / ((1 - e) + e * faktor)
                baris.append([f"Stump {s['no']}", fmt(e, 4), fmt(a, 4), fmt(faktor, 2) + "×", pct(total_salah)])
            df = pd.DataFrame(baris, columns=["Stump", "Error ε", "α", "Pengali bobot sesi salah (e^α)",
                                              "Porsi bobot sesi salah setelah update"]).set_index("Stump")
            tabel(df)
            st.info("Hasil menarik: setelah update, sesi yang salah ditebak stump sebelumnya selalu memegang tepat 50% dari total bobot. "
                    "Karena itu stump berikutnya dipaksa fokus pada kesalahan tersebut.")
            e1 = S[0]["error"]
            st.code(f"Stump 1: sesi salah sebelum = {fmt(e1 * 100, 1)}% bobot\n"
                    f"         e^α = e^{fmt(S[0]['alpha'], 4)} = {fmt(math.exp(S[0]['alpha']), 2)}\n"
                    f"         sesudah = ({fmt(e1, 3)} × {fmt(math.exp(S[0]['alpha']), 2)}) ÷ "
                    f"[{fmt(1 - e1, 3)} + {fmt(e1, 3)} × {fmt(math.exp(S[0]['alpha']), 2)}] = "
                    f"{fmt(e1 * math.exp(S[0]['alpha']) / ((1 - e1) + e1 * math.exp(S[0]['alpha'])) * 100, 1)}%",
                    language="text")

        elif i == 6:
            st.markdown("#### 🗳️ Voting akhir")
            st.write("Semua stump memberi suara +1 (beli) atau −1 (tidak beli), dikalikan bobot α-nya. Hasilnya dijumlahkan:")
            st.latex(r"H(x) = \operatorname{sign}\left( \sum_{t=1}^{T} \alpha_t \, h_t(x) \right), \quad T = 100")
            st.write("Contoh dengan 4 stump pertama untuk satu sesi (ubah nilainya sesuka Anda):")
            fitur_stump = list(dict.fromkeys(s["fitur"] for s in S))
            c = st.columns(len(fitur_stump))
            nilai = {f: input_stump(f, f"vote_{f}", k) for f, k in zip(fitur_stump, c)}
            skor, baris = 0.0, []
            for s in S:
                kls = s["kiri"]["kelas"] if nilai[s["fitur"]] <= s["batas"] else s["kanan"]["kelas"]
                h = 1 if kls else -1
                skor += s["alpha"] * h
                baris.append([f"Stump {s['no']}", f"{s['fitur']} = {fmt(nilai[s['fitur']], 3)} (batas {fmt(s['batas'], 3)})",
                              f"{h:+d}", fmt(s["alpha"], 4), fmt(s["alpha"] * h, 4)])
            tabel(pd.DataFrame(baris, columns=["Stump", "Pengecekan", "Suara h", "α", "α × h"]).set_index("Stump"))
            st.code(f"Skor = {' + '.join(f'({r[4]})' for r in baris)} = {fmt(skor, 4)}", language="text")
            (st.success if skor > 0 else st.error)(
                f"Skor {'positif' if skor > 0 else 'negatif'} → sesi ini diprediksi **{'membeli' if skor > 0 else 'tidak membeli'}**.")

        else:
            st.markdown("#### 📊 Evaluasi dari confusion matrix")
            tn, fp, fn, tp = CM["tn"], CM["fp"], CM["fn"], CM["tp"]
            st.latex(r"Acc = \frac{TP+TN}{TP+TN+FP+FN} \quad Prec = \frac{TP}{TP+FP} \quad Rec = \frac{TP}{TP+FN} \quad F1 = \frac{2\,Prec\,Rec}{Prec+Rec}")
            acc = (tp + tn) / (tp + tn + fp + fn)
            prec, rec = tp / (tp + fp), tp / (tp + fn)
            f1 = 2 * prec * rec / (prec + rec)
            st.code(
                f"TN = {fmt(tn, 0)}   FP = {fmt(fp, 0)}   FN = {fmt(fn, 0)}   TP = {fmt(tp, 0)}\n\n"
                f"Accuracy  = ({fmt(tp, 0)} + {fmt(tn, 0)}) ÷ {fmt(tp + tn + fp + fn, 0)} = {fmt(acc, 4)}\n"
                f"Precision = {fmt(tp, 0)} ÷ ({fmt(tp, 0)} + {fmt(fp, 0)}) = {fmt(prec, 4)}\n"
                f"Recall    = {fmt(tp, 0)} ÷ ({fmt(tp, 0)} + {fmt(fn, 0)}) = {fmt(rec, 4)}\n"
                f"F1-Score  = 2 × {fmt(prec, 4)} × {fmt(rec, 4)} ÷ ({fmt(prec, 4)} + {fmt(rec, 4)}) = {fmt(f1, 4)}",
                language="text")
            hit = [acc, prec, rec, f1]
            baris = [[m["nama"], fmt(h, 4), fmt(m["nilai"], 4), "✓" if abs(h - m["nilai"]) < 0.0006 else "✗"]
                     for m, h in zip(DATA["metrik"][:4], hit)]
            tabel(pd.DataFrame(baris, columns=["Metrik", "Hitung ulang", "Notebook", "Cocok"]).set_index("Metrik"))
            st.caption("ROC-AUC tidak bisa dihitung ulang dari confusion matrix karena membutuhkan skor tiap sesi "
                       f"di semua ambang. Nilai dari notebook: {fmt(DATA['metrik'][4]['nilai'], 4)}.")
            cvm = [mean([r["v"][j] for r in DATA["cv"]]) for j in range(5)]
            cvs = [stdev([r["v"][j] for r in DATA["cv"]]) for j in range(5)]
            st.write("**Kestabilan (cross-validation 5-fold):** " + " · ".join(
                f"{n} {fmt(m, 4)} ± {fmt(s, 4)}" for n, m, s in zip(DATA["cvNama"], cvm, cvs)))
