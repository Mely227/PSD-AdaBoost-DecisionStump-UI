"""Komponen tampilan yang dipakai bersama: palet, gaya grafik, kartu, tabel."""
import plotly.graph_objects as go  # noqa: F401  (dipakai modul lain lewat rapikan)
import streamlit as st

P = {"indigo": "#4f46e5", "violet": "#7c3aed", "cyan": "#06b6d4",
     "green": "#10b981", "rose": "#f43f5e", "amber": "#f59e0b"}
GRAD = ["g0", "g1", "g2", "g3", "g4"]


def rapikan(fig, tinggi=340, legenda=True):
    """Gaya seragam untuk semua grafik Plotly."""
    fig.update_layout(
        height=tinggi, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color="#475569"),
        showlegend=legenda, legend=dict(orientation="h", y=-0.15),
    )
    fig.update_yaxes(gridcolor="rgba(100,116,139,.15)")
    fig.update_xaxes(showgrid=False)
    return fig


def kartu(nilai, nama, ket, grad):
    st.markdown(
        f'<div class="kpi {grad}"><span class="v">{nilai}</span>'
        f'<span class="n">{nama}</span><span class="d">{ket}</span></div>',
        unsafe_allow_html=True)


def tabel(df, baris_tebal=None):
    """Tabel statis; satu baris bisa disorot."""
    def sorot(r):
        return (["font-weight:700; background-color:#eef2ff"] * len(r)
                if r.name == baris_tebal else [""] * len(r))
    st.table(df.style.apply(sorot, axis=1))


def input_stump(nama, kunci, wadah=None):
    """Widget untuk satu fitur yang dipakai stump: slider untuk fitur kontinu, saklar untuk fitur biner."""
    w = wadah or st
    if nama == "PageValues":
        return w.slider(nama, 0.0, 100.0, 10.0, 0.5, key=kunci)
    if nama in ("BounceRates", "ExitRates"):
        return w.slider(nama, 0.0, 0.2, 0.03 if nama == "BounceRates" else 0.05, 0.002, format="%.3f", key=kunci)
    if nama.startswith(("Month_", "VisitorType_")) or nama == "Weekend":
        return 1 if w.toggle(nama, value=(nama == "VisitorType_Returning_Visitor"), key=kunci) else 0
    return w.number_input(nama, value=0.0, key=kunci)
