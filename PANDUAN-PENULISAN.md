# Panduan Penulisan Laporan SLR (Aturan Penulisan)

Template ini bersifat **umum**: setiap penulis mengisi tiap bagian dengan data
miliknya sendiri (mis. hasil pipeline SLR dari MongoDB masing-masing). Dokumen
ini merangkum **aturan penulisan** agar laporan konsisten, sistematis, dan layak
sebagai artikel **Q1**.

## 1. Format fisik

| Aspek | Ketentuan |
|------|-----------|
| Kertas | A4 (21 × 29,7 cm) |
| Font | Times New Roman 12 pt (badan teks) |
| Spasi | 1,5 (kutipan panjang & abstrak boleh 1) |
| Margin | 3 cm semua sisi (ubah ke kiri 4 cm bila perlu margin jilid) |
| Perataan | Rata kiri-kanan (*justify*) |

Pengaturan ini sudah otomatis di `main.tex` — **jangan diubah** kecuali aturan
program studi berbeda.

## 2. Penomoran halaman

- **Bagian awal** (Abstrak s.d. Daftar Lampiran): angka Romawi kecil
  `i, ii, iii, …`.
- **Bagian isi** (BAB I dst.): format **per-BAB** `I-1`, `II-1`, `III-1`, …
  (nomor halaman ditaruh di tengah bawah).
- **Daftar Pustaka & Lampiran**: angka biasa.

## 3. Penomoran bab, sub-bab, gambar, tabel

- Judul bab: **BAB I, BAB II, …** (Romawi), huruf kapital, rata tengah, tebal.
- Sub-bab memakai angka Arab dan **dimulai ulang tiap bab**: `1`, `1.1`, `1.1.1`.
- Gambar/tabel: `Gambar <bab>.<nomor>` dan `Tabel <bab>.<nomor>`
  (mis. `Gambar 4.1`, `Tabel 3.2`).
- **Judul tabel di ATAS** tabel; **judul gambar di BAWAH** gambar; keduanya
  rata tengah.
- Setiap gambar/tabel **wajib dirujuk** di dalam teks (mis. "… pada
  Tabel 3.1") dan diberi **sumber** bila bukan olahan sendiri.

## 4. Kutipan dan daftar pustaka

- Gaya **IEEE numerik**: rujukan ditandai `[1]`, `[2]`, `[3]`–`[5]` sesuai urutan
  kemunculan. Dalam LaTeX gunakan `\cite{kunci}`.
- Daftar pustaka diberi judul **DAFTAR PUSTAKA**, dibuat dari `references.bib`
  (BibTeX) dengan gaya `IEEEtran`.
- Gunakan sumber primer mutakhir dan **bereputasi** (jurnal/konferensi
  terindeks). Untuk Q1, perbanyak rujukan Q1/Q2 yang relevan.

## 5. Kaidah bahasa

- Ikuti **PUEBI/EYD**; kalimat baku, lugas, dan objektif.
- **Istilah/frasa asing dimiringkan** (*italic*), mis. *machine learning*,
  *research gap*, *Systematic Literature Review*.
- Singkatan ditulis lengkap saat pertama kali muncul, diikuti akronim dalam
  kurung, mis. "Produk Domestik Bruto (PDB)".
- Hindari kata ganti orang pertama; gunakan kalimat pasif/impersonal.

## 6. Abstrak

- **Terstruktur**: Latar Belakang → Tujuan → Metode → Hasil → Kesimpulan.
- Satu paragraf, ~200–300 kata, dalam **Bahasa Indonesia** dan **Bahasa Inggris**.
- Diakhiri **3–6 kata kunci** (*keywords*).

## 7. Struktur wajib laporan SLR (PRISMA 2020)

Laporan mengikuti **IMRaD + PRISMA 2020**. Tiap bagian harus ada:

1. **Pendahuluan** — latar belakang & kesenjangan, **pertanyaan penelitian (RQ)**,
   tujuan/manfaat, ruang lingkup.
2. **Tinjauan Pustaka** — landasan teori, **matriks review terdahulu** (untuk
   menegaskan kebaruan/*novelty*), dan kesenjangan penelitian.
3. **Metodologi** — **protokol *a priori***, **kriteria PICO** (inklusi/eksklusi),
   **strategi pencarian yang reproducible** (basis data, kata kunci, *search
   string*, log), seleksi studi **dua penilai + koefisien *kappa***, ekstraksi
   data, penilaian kualitas, strategi sintesis, dan **GRADE**.
4. **Hasil & Pembahasan** — **diagram alur PRISMA**, karakteristik studi,
   sintesis per-RQ, kepastian bukti (GRADE), pembahasan, dan **keterbatasan**.
5. **Penutup** — kesimpulan (menjawab tiap RQ) dan saran/arah penelitian.

## 8. Aturan khusus (defensible untuk Q1)

- **Angka PRISMA dihitung ulang dari data** keputusan per-paper
  (`slr_screening`), **bukan disalin** dari narasi. Pastikan aritmetika alur
  menutup (identified = duplikat + tersaring; tersaring = eksklusi + lanjut; dst.).
- **Reliabilitas antar-penilai** (*kappa*) wajib dilaporkan untuk skrining
  abstrak dan teks lengkap.
- **Transparansi/provenans**: tiap nilai ekstraksi membawa **bukti** (kutipan +
  bagian sumber); tiap keluaran AI mencantumkan **penyedia + nama model**;
  **deviasi protokol** (koreksi keputusan) dilaporkan apa adanya.
- **Keterbatasan** dilaporkan jujur (mis. paper tak terakses, verifikasi yang
  tidak berjalan, heterogenitas).

## 9. Gambar & tabel hasil olah data

- Diagram alur PRISMA tersedia sebagai **gambar TikZ** di `main.tex` (angka
  mengikuti makro `\n...` yang dapat diisi otomatis).
- Tabel ekstraksi/ringkasan dan grafik dapat dihasilkan otomatis dari MongoDB
  masing-masing dengan `scripts/generate_report.py` (lihat `README.md`).
- Tabel lebar disajikan **landscape**; gunakan `longtable` untuk tabel
  multi-halaman.

## 10. Sebelum mengumpulkan

- [ ] Semua placeholder (`\dots`, "Tuliskan …", NAMA/NIM) sudah diisi.
- [ ] Semua gambar/tabel dirujuk di teks dan bernomor benar.
- [ ] Semua sitasi `\cite{}` punya entri di `references.bib`.
- [ ] Angka PRISMA konsisten antara diagram, tabel rekap, dan narasi.
- [ ] Abstrak ID & EN selaras; kata kunci 3–6.
- [ ] Lampiran lengkap (ekstraksi, eksklusi, *search string*, provenans,
      checklist PRISMA 2020, deviasi protokol).
