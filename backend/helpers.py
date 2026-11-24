"""Fungsi bantu: format angka gaya Indonesia, statistik, dan pembuat SVG pohon stump."""
from statistics import fmean, pstdev

NAMA_KELAS = ["Tidak Beli (0)", "Beli (1)"]


def fmt(angka, desimal=2):
    """1234.5 -> '1.234,50'"""
    teks = f"{angka:,.{desimal}f}"
    return teks.replace(",", "§").replace(".", ",").replace("§", ".")


def pct(angka):
    """0.9342 -> '93,42%'"""
    return fmt(angka * 100, 2) + "%"


def mean(a):
    return fmean(a)


def stdev(a):
    """Simpangan baku populasi (sama dengan versi PHP)."""
    return pstdev(a)


def svg_stump(s):
    """Gambar pohon stump sebagai string SVG."""
    def node(x, y, w, h, d, judul):
        baris = ([judul] if judul else []) + [
            f"gini = {fmt(d['gini'], 3)}",
            f"samples = {fmt(d['n'], 0)}",
            f"value = [{fmt(d['val'][0], 3)}, {fmt(d['val'][1], 3)}]",
            f"class = {NAMA_KELAS[d['kelas']]}",
        ]
        lh = 18
        top = y + (h - len(baris) * lh) / 2 + 13
        stroke = "#059669" if d["kelas"] else "#e11d48"
        teks = "".join(
            f'<text x="{x + w / 2}" y="{top + i * lh}" text-anchor="middle" '
            f'font-weight="{700 if judul and i == 0 else 400}">{t}</text>'
            for i, t in enumerate(baris)
        )
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" '
                f'fill="url(#g{d["kelas"]})" stroke="{stroke}" stroke-width="2"/>{teks}')

    h_akar, h_daun = 112, 92
    b = fmt(s["batas"], 3)
    return f"""
<svg viewBox="0 0 680 360" width="640" style="display:block;margin:0 auto" xmlns="http://www.w3.org/2000/svg"
     font-family="Inter, system-ui, sans-serif" font-size="13" fill="#1e293b">
  <defs>
    <linearGradient id="g0" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe4e6"/><stop offset="1" stop-color="#fda4af"/></linearGradient>
    <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d1fae5"/><stop offset="1" stop-color="#6ee7b7"/></linearGradient>
  </defs>
  <line x1="340" y1="{16 + h_akar}" x2="150" y2="230" stroke="#64748b" stroke-width="2"/>
  <line x1="340" y1="{16 + h_akar}" x2="530" y2="230" stroke="#64748b" stroke-width="2"/>
  <text x="215" y="190" fill="#64748b">True (≤ {b})</text>
  <text x="480" y="190" fill="#64748b">False (&gt; {b})</text>
  {node(230, 16, 220, h_akar, s["akar"], f"{s['fitur']} ≤ {b}")}
  {node(40, 230, 220, h_daun, s["kiri"], "")}
  {node(420, 230, 220, h_daun, s["kanan"], "")}
</svg>"""
