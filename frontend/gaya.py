"""Pemuat gaya.css: satu file CSS yang dibagi per BAGIAN.

Dipakai oleh app.py (bagian "halaman") dan animasi.py (bagian "hero", "alur", "jaringan").
Bagian "token" (warna dasar) otomatis disertakan di setiap bagian.
"""
import re
from functools import lru_cache
from pathlib import Path

BERKAS = Path(__file__).parent / "gaya.css"
PENANDA = re.compile(r"/\* #{5} BAGIAN: (\w+) #{5} \*/")


@lru_cache(maxsize=1)
def _baca_bagian():
    """Baca gaya.css sekali, pecah menjadi {nama bagian: isi CSS}."""
    teks = BERKAS.read_text(encoding="utf-8")
    penanda = list(PENANDA.finditer(teks))
    hasil = {}
    for i, m in enumerate(penanda):
        akhir = penanda[i + 1].start() if i + 1 < len(penanda) else len(teks)
        hasil[m.group(1)] = teks[m.end():akhir].strip()
    return hasil


def muat_css(bagian, **isi):
    """CSS satu bagian (plus token). isi = nilai pengganti untuk penanda __NAMA__ di CSS."""
    semua = _baca_bagian()
    css = semua["token"] + "\n" + semua[bagian]
    for kunci, nilai in isi.items():
        css = css.replace(f"__{kunci.upper()}__", str(nilai))
    return css
