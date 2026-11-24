"""Tab hasil model: Metrik, Eksplorasi, Cross-validation, Pohon, Tuning, Evaluasi, Simulator, Galeri.

Setiap tab adalah satu fungsi render_*() yang dipanggil dari app.py.
Semua angka dibaca dari backend/data.py.
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from plotly.subplots import make_subplots

from data import DATA
from helpers import NAMA_KELAS, fmt, mean, pct, stdev, svg_stump
from ui import GRAD, P, input_stump, kartu, rapikan, tabel

BASE = Path(__file__).parent
CM = DATA["cm"]             # confusion matrix: tn, fp, fn, tp
N_UJI = sum(CM.values())    # jumlah sesi data uji


# ================================================================  DATA TEKS PENJELASAN
def nilai_metrik(m):
    return fmt(m["nilai"], 4) if m["nama"] == "ROC-AUC" else pct(m["nilai"])


PENJELASAN = [
    {"rumus": "(TP + TN) ÷ semua sesi",
     "arti": f"Dari 100 sesi, sekitar {round(DATA['metrik'][0]['nilai'] * 100)} ditebak dengan benar.",
     "catatan": (f"Hati-hati: {fmt(DATA['kelas']['tidak'] / DATA['totalSesi'] * 100, 1)}% sesi memang "
                 f"tidak membeli, jadi menebak \"tidak membeli\" terus pun sudah menghasilkan sekitar "
                 f"{round(DATA['kelas']['tidak'] / DATA['totalSesi'] * 100)}%. "
                 "Karena itu Precision dan Recall perlu dilihat juga.")},
    {"rumus": "TP ÷ (TP + FP)",
     "arti": f"Dari {fmt(CM['tp'] + CM['fp'], 0)} sesi yang ditebak membeli, {fmt(CM['tp'], 0)} benar-benar membeli.",
     "catatan": "Precision tinggi berarti model jarang salah menuduh. Cocok jika kesalahan menebak membeli itu mahal, misalnya promo yang terbuang."},
    {"rumus": "TP ÷ (TP + FN)",
     "arti": f"Dari {fmt(CM['tp'] + CM['fn'], 0)} pembeli sungguhan, {fmt(CM['tp'], 0)} berhasil ditemukan model.",
     "catatan": f"Ini titik terlemah model: {fmt(CM['fn'], 0)} pembeli (sekitar {round(CM['fn'] / (CM['tp'] + CM['fn']) * 100)}%) terlewat."},
    {"rumus": "2 × (Precision × Recall) ÷ (Precision + Recall)",
     "arti": "Satu angka yang menggabungkan Precision dan Recall.",
     "catatan": "F1 tertarik ke angka yang lebih kecil, jadi Recall yang rendah ikut menurunkan F1."},
    {"rumus": "Luas di bawah kurva ROC",
     "arti": "Peluang model memberi skor lebih tinggi pada pembeli daripada non-pembeli, jika diambil satu pasang acak.",
     "catatan": "0,5 berarti sama dengan tebakan acak, 1 berarti sempurna."},
]

INFO_CM = {
    "tn": ("Benar: tidak membeli", "Sesi yang memang tidak membeli dan ditebak tidak membeli.",
           CM["tn"] / (CM["tn"] + CM["fp"]), "dari semua sesi yang aslinya tidak membeli"),
    "fp": ("Salah tuduh", "Sesi yang aslinya tidak membeli, tetapi ditebak membeli. Dampaknya: promo atau perhatian terbuang.",
           CM["fp"] / (CM["tn"] + CM["fp"]), "dari semua sesi yang aslinya tidak membeli"),
    "fn": ("Terlewat", "Pembeli sungguhan yang ditebak tidak membeli. Dampaknya: peluang penjualan terlewat.",
           CM["fn"] / (CM["tp"] + CM["fn"]), "dari semua pembeli sungguhan"),
    "tp": ("Benar: membeli", "Pembeli sungguhan yang berhasil ditebak membeli.",
           CM["tp"] / (CM["tp"] + CM["fn"]), "dari semua pembeli sungguhan"),
}


# ================================================================  METRIK
def render_metrik():
    """Tab Metrik: radar performa dan kartu metrik dengan penjelasan."""
    st.subheader("Performa model")
    st.caption(f"Hasil pada {fmt(N_UJI, 0)} sesi data uji yang belum pernah dilihat model. "
               "Klik tombol Penjelasan di bawah tiap kartu.")
    kiri, kanan = st.columns([5, 7])
    with kiri:
        nama = [m["nama"] for m in DATA["metrik"]]
        nilai = [m["nilai"] for m in DATA["metrik"]]
        fig = go.Figure(go.Scatterpolar(
            r=nilai + nilai[:1], theta=nama + nama[:1], fill="toself",
            fillcolor="rgba(124,58,237,.25)", line=dict(color=P["violet"], width=2),
            marker=dict(color=P["indigo"])))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0.5, 1], tickvals=[0.5, 0.6, 0.7, 0.8, 0.9, 1])))
        st.plotly_chart(rapikan(fig, 380, legenda=False))
    with kanan:
        for baris in (DATA["metrik"][:3], DATA["metrik"][3:]):
            kolom = st.columns(3)
            for k, m in zip(kolom, baris):
                i = DATA["metrik"].index(m)
                with k:
                    kartu(nilai_metrik(m), m["nama"], m["ket"], GRAD[i % 5])
                    with st.popover("Penjelasan"):
                        p = PENJELASAN[i]
                        st.markdown(f"### {nilai_metrik(m)}")
                        st.progress(min(1.0, m["nilai"]))
                        st.write(p["arti"])
                        st.markdown(f'<code class="formula">{p["rumus"]}</code>', unsafe_allow_html=True)
                        st.info(p["catatan"])


# ================================================================  EKSPLORASI
def render_eksplorasi():
    """Tab Eksplorasi: proporsi kelas dan konversi per tipe pengunjung / bulan."""
    st.subheader("Eksplorasi data")
    st.caption(f"Dari {fmt(DATA['totalSesi'], 0)} sesi, hanya sekitar {fmt(DATA['konversiRata'], 0)}% yang "
               "berakhir dengan pembelian. Kelas ini timpang, jadi akurasi saja tidak cukup untuk menilai model.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Proporsi kelas**")
        fig = go.Figure(go.Pie(
            labels=["Tidak membeli", "Membeli"],
            values=[DATA["kelas"]["tidak"], DATA["kelas"]["beli"]],
            hole=0.62, marker=dict(colors=[P["indigo"], P["green"]]),
            hovertemplate="%{label}: %{value:,} sesi<extra></extra>"))
        st.plotly_chart(rapikan(fig))
    for kol, judul, d, warna in ((c2, "Konversi per tipe pengunjung (%)", DATA["visitor"], P["cyan"]),
                                 (c3, "Konversi per bulan (%)", DATA["bulan"], P["violet"])):
        with kol:
            st.markdown(f"**{judul}**")
            fig = go.Figure(go.Bar(x=d["label"], y=d["nilai"], marker_color=warna))
            fig.update_yaxes(rangemode="tozero")
            st.plotly_chart(rapikan(fig, legenda=False))


# ================================================================  CROSS-VALIDATION
def render_cv():
    """Tab Cross-validation: hasil 5-fold (kartu, grafik, tabel)."""
    st.subheader("Cross-validation 5-fold")
    st.caption("Data latih dibagi 5 lipatan. Model dilatih 5 kali, tiap kali menguji di satu lipatan "
               "berbeda. Garis yang datar berarti model stabil.")
    semua_fold = [r["v"] for r in DATA["cv"]]
    kolom = st.columns(5)
    for i, (k, nama) in enumerate(zip(kolom, DATA["cvNama"])):
        arr = [f[i] for f in semua_fold]
        with k:
            kartu(fmt(mean(arr), 4), nama, f"± {fmt(stdev(arr), 4)} antar fold", GRAD[i])

    kiri, kanan = st.columns([2, 1])
    label_fold = [f"Fold {r['fold']}" for r in DATA["cv"]]
    warna = [P["indigo"], P["cyan"], P["rose"], P["amber"], P["green"]]
    with kiri:
        st.markdown("**Metrik di setiap fold**")
        fig = go.Figure()
        for i, nama in enumerate(DATA["cvNama"]):
            fig.add_trace(go.Scatter(
                x=label_fold, y=[r["v"][i] for r in DATA["cv"]], name=nama, mode="lines+markers",
                line=dict(color=warna[i], width=3, shape="spline"), marker=dict(size=9)))
        fig.update_yaxes(range=[0.55, 1])
        st.plotly_chart(rapikan(fig, 380))
    with kanan:
        st.markdown("**Waktu pelatihan (detik)**")
        fig = go.Figure(go.Bar(x=label_fold, y=[r["waktu"] for r in DATA["cv"]], marker_color=P["amber"]))
        fig.update_yaxes(rangemode="tozero")
        st.plotly_chart(rapikan(fig, 380, legenda=False))

    st.markdown("**Tabel hasil per fold**")
    baris = [[f"Fold {r['fold']}"] + [fmt(x, 4) for x in r["v"]] + [fmt(r["waktu"], 1)] for r in DATA["cv"]]
    rata = [fmt(mean([f[i] for f in semua_fold]), 4) for i in range(5)]
    baris.append(["Rata-rata"] + rata + [fmt(mean([r["waktu"] for r in DATA["cv"]]), 1)])
    df = pd.DataFrame(baris, columns=["Fold", "Acc", "Prec", "Recall", "F1", "AUC", "Waktu (dtk)"]).set_index("Fold")
    tabel(df, baris_tebal="Rata-rata")


# ================================================================  POHON
def render_pohon():
    """Tab Pohon: lihat tiap stump AdaBoost beserta detail kotaknya."""
    st.subheader("Pohon keputusan (stump)")
    st.caption("AdaBoost memakai 100 pohon sedalam satu aturan. Setiap pohon memberi suara dengan bobot α, "
               "dan hasil akhirnya adalah jumlah suara berbobot. Pilih stump, lalu pilih kotak untuk melihat detailnya.")
    no = st.radio("Pilih stump", [s["no"] for s in DATA["stumps"]], horizontal=True,
                  format_func=lambda n: f"Stump {n}")
    s = DATA["stumps"][no - 1]
    components.html(svg_stump(s), height=700)

    k, r = s["kiri"]["kelas"], s["kanan"]["kelas"]
    batas = fmt(s["batas"], 3)
    ringkas = (f"Kedua cabang menebak **{NAMA_KELAS[k]}**, jadi stump ini hanya menggeser skor akhir ke arah itu."
               if k == r else
               f"Jika {s['fitur']} ≤ {batas} maka tebakannya **{NAMA_KELAS[k]}**, selain itu **{NAMA_KELAS[r]}**.")
    st.markdown(f"**Stump {s['no']}** · Error {fmt(s['error'], 4)} · Bobot suara α {fmt(s['alpha'], 4)}  \n{ringkas}")

    bagian = st.radio("Lihat detail kotak", ["akar", "kiri", "kanan"], horizontal=True,
                      format_func=lambda x: {"akar": "Akar", "kiri": "Cabang True", "kanan": "Cabang False"}[x])
    d = s[bagian]
    aturan = {"akar": f"{s['fitur']} ≤ {batas}", "kiri": f"{s['fitur']} ≤ {batas} (True)",
              "kanan": f"{s['fitur']} > {batas} (False)"}[bagian]
    murni = ("hampir murni, hampir semua sesi di sini satu kelas" if d["gini"] < 0.2
             else "cukup murni" if d["gini"] < 0.4 else "masih bercampur antara dua kelas")
    porsi = d["n"] / s["akar"]["n"] * 100
    with st.container(border=True):
        st.write("Aturan inilah yang memecah data latih menjadi dua cabang." if bagian == "akar"
                 else "Sesi yang memenuhi kondisi ini masuk ke kotak ini.")
        st.markdown(f'<code class="formula">{aturan}</code>', unsafe_allow_html=True)
        st.progress(min(1.0, porsi / 100))
        st.markdown(
            f"- **Jumlah sampel**: {fmt(d['n'], 0)} ({fmt(porsi, 1)}% data latih)\n"
            f"- **Gini**: {fmt(d['gini'], 3)}: {murni}\n"
            f"- **Value**: [{fmt(d['val'][0], 3)}, {fmt(d['val'][1], 3)}]\n"
            f"- **Tebakan**: {NAMA_KELAS[d['kelas']]}")
        st.caption("Gini 0 berarti satu kelas saja, 0,5 berarti campuran seimbang. Value adalah bobot "
                   "[tidak beli, beli] di kotak ini sebagai bagian dari seluruh bobot data.")

    st.markdown("**Error dan bobot suara pada 10 iterasi pertama**")
    it = DATA["iterasi"]
    label_t = [f"t={i + 1}" for i in range(len(it["alpha"]))]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=label_t, y=it["alpha"], name="Bobot suara α", marker_color=P["violet"]),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=label_t, y=it["error"], name="Weighted error ε", mode="lines+markers",
                             line=dict(color=P["rose"], width=3, shape="spline")), secondary_y=True)
    fig.update_yaxes(title_text="α", secondary_y=False)
    fig.update_yaxes(title_text="ε", range=[0, 0.5], showgrid=False, secondary_y=True)
    st.plotly_chart(rapikan(fig, 380))
    st.caption(f"Stump pertama paling akurat (error {fmt(DATA['stumps'][0]['error'], 3)}) sehingga suaranya "
               "paling besar. Pada stump-stump berikutnya error naik mendekati 0,5 (tebakan acak) dan suaranya mengecil.")


# ================================================================  TUNING
def render_tuning():
    """Tab Tuning: perbandingan kombinasi hyperparameter."""
    HY = DATA["hyper"]
    terbaik = max(range(len(HY)), key=lambda i: HY[i]["v"][3])   # F1 tertinggi (indeks 3)
    best = HY[terbaik]
    st.subheader("Perbandingan hyperparameter")
    st.caption(f"Lima kombinasi jumlah stump dan learning rate. Kombinasi {best['n']} stump dengan "
               f"learning rate {fmt(best['lr'], 1)} memberi F1-Score tertinggi.")
    kiri, kanan = st.columns([7, 5])
    label_h = [f"{h['n']} stump, LR {fmt(h['lr'], 1)}" for h in HY]
    with kiri:
        st.markdown("**Precision, Recall, dan F1**")
        fig = go.Figure()
        for idx, nama, warna_ in ((1, "Precision", P["cyan"]), (2, "Recall", P["amber"]), (3, "F1-Score", P["green"])):
            fig.add_trace(go.Bar(x=label_h, y=[h["v"][idx] for h in HY], name=nama, marker_color=warna_))
        fig.update_layout(barmode="group")
        fig.update_yaxes(range=[0.4, 1])
        st.plotly_chart(rapikan(fig, 380))
    with kanan:
        st.markdown("**Tabel lengkap**")
        baris = [[lbl] + [fmt(x, 4) for x in h["v"]] for lbl, h in zip(label_h, HY)]
        df = pd.DataFrame(baris, columns=["Kombinasi", "Acc", "Prec", "Recall", "F1", "AUC"]).set_index("Kombinasi")
        tabel(df, baris_tebal=label_h[terbaik])


# ================================================================  EVALUASI
def render_evaluasi():
    """Tab Evaluasi: confusion matrix, fitur terpenting, dan catatan recall."""
    st.subheader("Evaluasi akhir")
    st.caption("Pilih tiap kotak confusion matrix untuk melihat artinya.")
    kiri, kanan = st.columns([5, 7])
    with kiri:
        st.markdown("**Confusion matrix**")
        maks = CM["tn"]

        def sel(kunci, ket, benar):
            a = max(0.35, CM[kunci] / maks)
            warna_ = f"rgba(79,70,229,{a:.2f})" if benar else f"rgba(244,63,94,{a:.2f})"
            return f'<div class="cm-cell" style="background:{warna_}"><b>{fmt(CM[kunci], 0)}</b><span>{ket}</span></div>'

        st.markdown(
            '<div class="cm"><span></span><span class="cm-h">Ditebak tidak beli</span><span class="cm-h">Ditebak beli</span>'
            f'<span class="cm-h">Aslinya tidak beli</span>{sel("tn", "Benar", True)}{sel("fp", "Salah tuduh", False)}'
            f'<span class="cm-h">Aslinya beli</span>{sel("fn", "Terlewat", False)}{sel("tp", "Benar", True)}</div>',
            unsafe_allow_html=True)
        kunci = st.radio("Lihat arti kotak", ["tn", "fp", "fn", "tp"], horizontal=True,
                         format_func=lambda x: {"tn": "Benar (tidak beli)", "fp": "Salah tuduh",
                                                "fn": "Terlewat", "tp": "Benar (beli)"}[x])
        judul, arti, porsi_k, ket_porsi = INFO_CM[kunci]
        with st.container(border=True):
            st.markdown(f"#### {judul}: {fmt(CM[kunci], 0)}")
            st.progress(min(1.0, porsi_k))
            st.write(arti)
            st.markdown(f"- **Porsi**: {fmt(porsi_k * 100, 2)}% {ket_porsi}\n"
                        f"- **Porsi dari data uji**: {fmt(CM[kunci] / N_UJI * 100, 2)}% dari {fmt(N_UJI, 0)} sesi")
    with kanan:
        st.markdown("**10 fitur paling berpengaruh (%)**")
        fig = go.Figure(go.Bar(x=[f[1] for f in DATA["fitur"]], y=[f[0] for f in DATA["fitur"]],
                               orientation="h", marker_color=P["indigo"]))
        fig.update_yaxes(autorange="reversed", showgrid=False)
        fig.update_xaxes(showgrid=True, gridcolor="rgba(100,116,139,.15)")
        st.plotly_chart(rapikan(fig, 420, legenda=False))

    prec, rec = DATA["metrik"][1]["nilai"], DATA["metrik"][2]["nilai"]
    st.markdown(
        f'<div class="alert-g"><b>Yang perlu diperhatikan:</b> precision {pct(prec)} dan recall '
        f'{pct(rec)}. Dari sesi yang ditebak membeli, sekitar {fmt((1 - prec) * 100, 0)}% salah tuduh, dan model '
        f'melewatkan sekitar {fmt((1 - rec) * 100, 0)}% pembeli sungguhan.</div>', unsafe_allow_html=True)


# ================================================================  SIMULATOR
def render_simulator():
    """Tab Simulator: geser slider, lihat suara 4 stump pertama."""
    st.subheader("Coba sendiri")
    st.caption("Geser nilainya untuk melihat suara 4 stump pertama. Ini penyederhanaan dari model lengkap "
               "yang memakai 100 stump.")
    kiri, kanan = st.columns([5, 7])
    with kiri:
        fitur_stump = list(dict.fromkeys(s["fitur"] for s in DATA["stumps"]))
        nilai_sim = {f: input_stump(f, f"sim_{f}") for f in fitur_stump}
    skor, html_suara = 0.0, ""
    for s in DATA["stumps"]:
        kelas = s["kiri"]["kelas"] if nilai_sim[s["fitur"]] <= s["batas"] else s["kanan"]["kelas"]
        skor += s["alpha"] if kelas else -s["alpha"]
        html_suara += (f'<div class="vote {"yes" if kelas else "no"}">'
                       f'<span>Stump {s["no"]}: {s["fitur"]} ≤ {fmt(s["batas"], 3)}</span>'
                       f'<b>{"+" if kelas else "−"}{fmt(s["alpha"], 2)}</b></div>')
    membeli = skor > 0
    with kanan:
        st.markdown(html_suara, unsafe_allow_html=True)
        st.markdown(
            f'<div class="verdict {"yes" if membeli else "no"}">Skor total '
            f'<b>{"+" if membeli else "−"}{fmt(abs(skor), 2)}</b>: sesi ini cenderung '
            f'<b>{"membeli" if membeli else "tidak membeli"}</b>.</div>', unsafe_allow_html=True)

    lama = st.session_state.get("arah_lama")
    if lama is not None and lama != membeli:
        st.toast(f"Skor berbalik: sesi ini sekarang cenderung {'membeli' if membeli else 'tidak membeli'}.",
                 icon="🔄")
    st.session_state["arah_lama"] = membeli


# ================================================================  GALERI
def render_galeri():
    """Tab Galeri: gambar-gambar dari notebook."""
    st.subheader("Galeri gambar notebook")
    st.caption("Visualisasi asli dari notebook. Arahkan kursor ke gambar lalu klik ikon layar penuh untuk memperbesar.")
    kolom = st.columns(3)
    for i, (berkas, judul_gambar) in enumerate(DATA["galeri"]):
        with kolom[i % 3]:
            st.image(str(BASE / "assets" / berkas), caption=judul_gambar)
