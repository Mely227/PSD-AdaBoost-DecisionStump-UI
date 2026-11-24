"""Skema dataset Online Shoppers Purchasing Intention: arti tiap kolom dan perlakuannya."""

KELOMPOK = {
    "Perilaku halaman": "#4f46e5",
    "Durasi": "#0ea5e9",
    "Metrik web": "#f43f5e",
    "Waktu": "#f59e0b",
    "Teknis": "#10b981",
    "Pengunjung": "#7c3aed",
}

APA_ADANYA = "Dipakai apa adanya (pohon tidak butuh penskalaan)"

# (nama, tipe, kelompok, ikon, arti, perlakuan)
FITUR = [
    ("Administrative", "Numerik (hitungan)", "Perilaku halaman", "🗂️",
     "Jumlah halaman administrasi (akun, profil, pengaturan) yang dibuka dalam satu sesi.", APA_ADANYA),
    ("Administrative_Duration", "Numerik (detik)", "Durasi", "⏱️",
     "Total waktu yang dihabiskan di halaman administrasi.", APA_ADANYA),
    ("Informational", "Numerik (hitungan)", "Perilaku halaman", "ℹ️",
     "Jumlah halaman informasi (kontak, tentang toko) yang dibuka.", APA_ADANYA),
    ("Informational_Duration", "Numerik (detik)", "Durasi", "🕒",
     "Total waktu yang dihabiskan di halaman informasi.", APA_ADANYA),
    ("ProductRelated", "Numerik (hitungan)", "Perilaku halaman", "🛍️",
     "Jumlah halaman produk yang dilihat.", APA_ADANYA),
    ("ProductRelated_Duration", "Numerik (detik)", "Durasi", "⏳",
     "Total waktu yang dihabiskan di halaman produk.", APA_ADANYA),
    ("BounceRates", "Numerik (0 sampai 1)", "Metrik web", "↩️",
     "Proporsi pengunjung yang pergi setelah melihat satu halaman saja.", APA_ADANYA),
    ("ExitRates", "Numerik (0 sampai 1)", "Metrik web", "🚪",
     "Proporsi kunjungan yang berakhir di halaman tertentu.", APA_ADANYA),
    ("PageValues", "Numerik", "Metrik web", "💎",
     "Rata-rata nilai halaman yang dikunjungi sebelum transaksi selesai. Sinyal terkuat niat beli.", APA_ADANYA),
    ("SpecialDay", "Numerik (0 sampai 1)", "Waktu", "🎁",
     "Kedekatan tanggal kunjungan dengan hari spesial seperti Valentine atau Hari Ibu.", APA_ADANYA),
    ("Month", "Kategorikal", "Waktu", "🗓️",
     "Bulan kunjungan.", "One-hot encoding, kategori pertama dibuang (drop first)"),
    ("OperatingSystems", "Kode (angka)", "Teknis", "💻",
     "Kode sistem operasi pengunjung.", "Dipakai sebagai angka (sudah berupa kode)"),
    ("Browser", "Kode (angka)", "Teknis", "🌐",
     "Kode peramban yang dipakai.", "Dipakai sebagai angka (sudah berupa kode)"),
    ("Region", "Kode (angka)", "Teknis", "📍",
     "Kode wilayah pengunjung.", "Dipakai sebagai angka (sudah berupa kode)"),
    ("TrafficType", "Kode (angka)", "Teknis", "🚦",
     "Kode sumber lalu lintas (iklan, pencarian, langsung, dan sebagainya).", "Dipakai sebagai angka (sudah berupa kode)"),
    ("VisitorType", "Kategorikal", "Pengunjung", "👤",
     "Jenis pengunjung: baru, kembali, atau lainnya.", "One-hot encoding, kategori pertama dibuang (drop first)"),
    ("Weekend", "Biner (True/False)", "Waktu", "🏖️",
     "Apakah kunjungan terjadi di akhir pekan.", "Diubah dari True/False menjadi 1/0"),
]

TARGET = ("Revenue", "🎯", "True (1) = sesi berakhir dengan pembelian. False (0) = tidak membeli.")

# ikon + label untuk animasi alur kerja
TAHAP = [("📦", "Data"), ("🧹", "Cleaning"), ("🔤", "Encoding"), ("✂️", "Split"),
         ("🌳", "Stump"), ("⚖️", "Boosting"), ("🗳️", "Voting"), ("📊", "Evaluasi")]


def ikon_untuk(nama):
    """Ikon untuk nama fitur, termasuk kolom hasil encoding (Month_Nov -> Month)."""
    kamus = {f[0]: f[3] for f in FITUR}
    return kamus.get(nama) or kamus.get(nama.split("_")[0], "🔹")
