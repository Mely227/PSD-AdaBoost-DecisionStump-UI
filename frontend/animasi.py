"""Animasi HTML/SVG murni (tanpa library tambahan) untuk ditampilkan lewat components.html."""
import math

from gaya import muat_css
from helpers import fmt
from skema import ikon_untuk

FONT = '<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">'


# ------------------------------------------------------------------ HERO
def hero_html(data):
    ident = data["identitas"]
    stat = [
        (data["totalSesi"], "int", "Sesi kunjungan"),
        (data["jumlahFitur"], "int", "Fitur setelah encoding"),
        (data["konversiRata"], "pct", "Sesi berakhir membeli"),
        (data["metrik"][4]["nilai"], "auc", "ROC-AUC data uji"),
    ]
    stat_html = "".join(
        f'<div class="st"><b data-to="{n}" data-fmt="{t}">0</b><span>{lbl}</span></div>'
        for n, t, lbl in stat)

    # simpul ikon (ikon, x%, y%) dan garis penghubung antar simpul
    simpul = [("🛒", 62, 14), ("💳", 88, 16), ("📈", 75, 38), ("🌳", 60, 52),
              ("🎯", 91, 48), ("⚡", 78, 66), ("🧮", 68, 28)]
    garis = [(0, 6), (6, 2), (1, 2), (2, 3), (2, 4), (3, 5), (4, 5), (2, 5), (0, 1)]
    svg_garis = "".join(
        f'<line x1="{simpul[a][1]}" y1="{simpul[a][2]}" x2="{simpul[b][1]}" y2="{simpul[b][2]}" '
        f'class="gr" style="animation-delay:-{i * 0.35}s"/>' for i, (a, b) in enumerate(garis))
    ikon_html = "".join(
        f'<div class="ik" style="left:{x}%;top:{y}%;animation-delay:-{i * 0.9}s">{e}</div>'
        for i, (e, x, y) in enumerate(simpul))

    return """<!DOCTYPE html><html><head><meta charset="utf-8">""" + FONT + "<style>" + muat_css("hero") + """</style></head><body>
<div class="hero">
  <div class="net"><svg viewBox="0 0 100 100" preserveAspectRatio="none">""" + svg_garis + """</svg>""" + ikon_html + """</div>
  <span class="tag">AdaBoost · Decision Stump</span>
  <h1>Siapa yang akhirnya membeli?</h1>
  <p class="lead">Prediksi niat beli pengunjung toko online, dilatih pada """ + fmt(data["totalSesi"], 0) + """ sesi kunjungan.</p>
  <p class="nama">""" + ident["nama"] + " · " + ident["nim"] + " · " + ident["matkul"] + """</p>
  <div class="stats">""" + stat_html + """</div>
</div>
<script>
const idf=(n,d)=>n.toLocaleString('id-ID',{minimumFractionDigits:d,maximumFractionDigits:d});
const fm=(v,t)=>t==='int'?Math.round(v).toLocaleString('id-ID'):t==='pct'?idf(v,2)+'%':idf(v,4);
document.querySelectorAll('[data-to]').forEach(el=>{
  const akhir=+el.dataset.to,t=el.dataset.fmt,m0=performance.now();
  const f=now=>{const p=Math.min(1,(now-m0)/1400),e=1-Math.pow(1-p,3);el.textContent=fm(akhir*e,t);if(p<1)requestAnimationFrame(f)};
  requestAnimationFrame(f);
});
</script></body></html>"""


# ------------------------------------------------------------------ ALUR KERJA
def pipeline_html(tahap, detik=2.0):
    n = len(tahap)
    total = n * detik
    langkah = "".join(
        f'<div class="s" style="animation-delay:{i * detik}s"><div class="b" style="animation-delay:{i * detik}s">{ik}</div>'
        f'<span>{i + 1}. {lbl}</span></div>' for i, (ik, lbl) in enumerate(tahap))
    return """<!DOCTYPE html><html><head><meta charset="utf-8">""" + FONT + "<style>" + muat_css("alur", total=f"{total}s", p85=round(100 / n * 0.85, 1), p100=round(100 / n, 1)) + """</style></head><body>
<div class="wrap"><div class="rel"><div class="garis"><i></i></div><div class="dot"></div>
<div class="steps">""" + langkah + """</div></div></div></body></html>"""


# ------------------------------------------------------------------ JARINGAN FITUR -> TARGET
def jaringan_html(fitur, target="Revenue"):
    """fitur = [(nama, persen), ...]. Tebal garis mengikuti besar pengaruh fitur."""
    cx, cy, rx, ry = 400, 238, 310, 165
    maks = max(v for _, v in fitur)
    n = len(fitur)
    isi = []
    for i, (nama, v) in enumerate(fitur):
        sdt = -math.pi / 2 + i * 2 * math.pi / n
        x, y = cx + rx * math.cos(sdt), cy + ry * math.sin(sdt)
        w = 1.5 + v / maks * 7
        alpha = 0.35 + 0.55 * v / maks
        isi.append(
            f'<path id="p{i}" d="M{x:.1f},{y:.1f} L{cx},{cy}" stroke="rgba(79,70,229,{alpha:.2f})" stroke-width="{w:.1f}" '
            f'stroke-linecap="round" fill="none" class="alir"/>'
            f'<circle r="{3 + v / maks * 3:.1f}" fill="#06b6d4"><animateMotion dur="{2 + (i % 4) * 0.4}s" begin="-{i * 0.3}s" '
            f'repeatCount="indefinite"><mpath href="#p{i}"/></animateMotion></circle>'
            f'<g class="nd" style="animation-delay:-{i * 0.5}s"><circle cx="{x:.1f}" cy="{y:.1f}" r="{26 + v / maks * 8:.1f}" fill="#fff" '
            f'stroke="#7c3aed" stroke-width="2.5"/><text x="{x:.1f}" y="{y + 8:.1f}" text-anchor="middle" font-size="24">{ikon_untuk(nama)}</text>'
            f'<text x="{x:.1f}" y="{y + 52:.1f}" text-anchor="middle" class="lb">{nama}</text>'
            f'<text x="{x:.1f}" y="{y + 67:.1f}" text-anchor="middle" class="pc">{fmt(v, 2)}%</text></g>')
    return """<!DOCTYPE html><html><head><meta charset="utf-8">""" + FONT + "<style>" + muat_css("jaringan") + """</style></head><body><div class="box">
<svg viewBox="0 0 800 480" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="gp" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f43f5e"/><stop offset="1" stop-color="#fb923c"/></linearGradient></defs>
""" + "".join(isi) + f"""
<circle cx="{cx}" cy="{cy}" r="46" class="ring"/>
<g class="pusat"><circle cx="{cx}" cy="{cy}" r="50" fill="url(#gp)" stroke="#fff" stroke-width="4"/>
<text x="{cx}" y="{cy + 2}" text-anchor="middle" font-size="30">🎯</text>
<text x="{cx}" y="{cy + 26}" text-anchor="middle" font-size="13" font-weight="700" fill="#fff">{target}</text></g>
</svg></div></body></html>"""
