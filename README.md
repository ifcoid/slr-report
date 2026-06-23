# slr-report

Laporan Lengkap SLR dari Proses sampai Finish.

Template **LaTeX** umum untuk Laporan *Systematic Literature Review* (SLR)
Program Diploma IV Teknik Informatika, Universitas Logistik dan Bisnis
Internasional (ULBI). Format sampul/tata letak mengikuti `templateslr.docx`,
sedangkan **kerangka isi** disesuaikan dengan `../nsa/GENERATEREPORT.md` agar
menjadi laporan SLR yang **komprehensif** dan **layak sebagai artikel Q1**:
mengikuti struktur **IMRaD + PRISMA 2020** dengan elemen transparansi/provenans.

> **Ini hanya kerangka (skeleton) + aturan penulisan.** Setiap penulis mengisi
> isinya dengan datanya sendiri — diambil dari **MongoDB masing-masing** melalui
> pipeline SLR. Repositori ini **tidak** memuat data milik siapa pun; berkas
> hasil isi (`generated/`) di-*ignore* oleh git.
>
> Aturan penulisan lengkap: **[PANDUAN-PENULISAN.md](PANDUAN-PENULISAN.md)**.

## Struktur berkas

| Berkas | Keterangan |
|--------|------------|
| `main.tex` | Dokumen utama (preamble + kerangka laporan). Mulai dari sini. |
| `references.bib` | Daftar pustaka BibTeX (gaya IEEE) — berisi entri **contoh**. |
| `images/logo-ulbi.png` | Logo ULBI untuk halaman sampul. |
| `PANDUAN-PENULISAN.md` | **Aturan penulisan** (format, penomoran, sitasi, dll). |
| `scripts/generate_report.py` | (Opsional) pengisi artefak dari MongoDB sendiri. |
| `scripts/verify_references.py` | Cek integritas rujukan (sitasi↔BibTeX, DOI↔Crossref/DataCite). |

## Cara kompilasi

Butuh distribusi TeX (TeX Live / MiKTeX). Cara paling mudah:

```bash
latexmk -pdf main.tex
```

Atau manual (untuk memproses sitasi IEEE):

```bash
pdflatex main
bibtex   main
pdflatex main
pdflatex main
```

Hasilnya adalah `main.pdf`.

## Yang sudah diatur sesuai format docx

- Kertas **A4**, font **Times New Roman** (via `newtxtext`), spasi **1,5**.
- Halaman sampul **Bahasa Indonesia** dan **Bahasa Inggris** dengan logo ULBI.
- **Abstrak terstruktur** (Latar Belakang/Tujuan/Metode/Hasil/Kesimpulan) ID + EN.
- Bagian awal bernomor romawi (`i, ii, iii, …`): Abstrak, Abstract,
  Kata Pengantar, Daftar Isi, Daftar Gambar, Daftar Tabel, Daftar Lampiran.
- Penomoran halaman isi **per-BAB**: `I-1`, `II-1`, `III-1`, dst.
- Daftar Isi menampilkan **BAB I**, **BAB II**, … (angka Romawi), sedangkan
  sub-bab, gambar, dan tabel memakai angka Arab (`1`, `1.1`, `4.1`).
- Contoh `longtable`, tabel PICO/PRISMA/GRADE, gambar, dan sitasi IEEE.

## Kerangka komprehensif (IMRaD + PRISMA 2020)

Disesuaikan dengan `../nsa/GENERATEREPORT.md` (alur modul M1–M9):

- **BAB I Pendahuluan** — latar belakang & gap, rumusan masalah (RQ),
  tujuan/manfaat, ruang lingkup, sistematika.
- **BAB II Tinjauan Pustaka** — landasan teori, **matriks review terdahulu &
  kebaruan**, state of the art, kesenjangan (evidence/empirical gap).
- **BAB III Metodologi (PRISMA)** — protokol a priori, **kriteria PICO**,
  strategi pencarian (reproducible), seleksi studi (dua penilai + *kappa*),
  ekstraksi data, penilaian kualitas, strategi sintesis, **GRADE**, serta
  **transparansi/provenans** (evidence, atribusi model, `xai_log`).
- **BAB IV Hasil & Pembahasan** — **diagram alur PRISMA** (angka *dihitung ulang*
  dari basis data), karakteristik studi, sintesis per-RQ, GRADE, bibliometrik
  (opsional), pembahasan (+ keterbatasan).
- **BAB V Penutup** — kesimpulan & arah penelitian lanjutan.
- **Lampiran A–F** — tabel ekstraksi lengkap, daftar eksklusi, string pencarian,
  provenans/xAI, checklist PRISMA 2020, dan catatan deviasi protokol.

> Setiap sub-bab di `main.tex` diberi komentar `[sumber: <koleksi.field>]` yang
> memetakan langsung ke state MongoDB (`slr_sessions` / `slr_screening` /
> `slr_extraction`) sesuai `GENERATEREPORT.md`, sehingga isi dapat diisi dari
> pipeline SLR. **Angka PRISMA dihitung ulang dari `slr_screening`**, bukan
> disalin dari narasi.

## Cara menyesuaikan (manual)

1. **Identitas laporan** — ubah blok `METADATA` di bagian atas `main.tex`
   (judul ID/EN, nama penulis, NIM, prodi, kota, bulan/tahun).
2. **Lembar pengesahan** — sisipkan hasil scan pada bagian yang ditandai
   `LEMBAR PENGESAHAN` di `main.tex` menggunakan `\includegraphics`.
3. **Isi** — ganti semua placeholder (`\dots`, "Tuliskan …") pada tiap
   `\section` / `\subsection` yang sudah disiapkan.
4. **Referensi** — ganti entri contoh pada `references.bib`, lalu sitasi dengan
   `\cite{kunci}`.
5. **Margin jilid** — jika dibutuhkan margin kiri 4 cm, ubah `left=3cm`
   menjadi `left=4cm` pada paket `geometry` di `main.tex`.

## (Opsional) Mengisi dari MongoDB masing-masing

Bagi yang memakai pipeline SLR, isi data dapat dihasilkan otomatis dari sesi
MongoDB **milik sendiri** (read-only). Kredensial dibaca dari
`/home/adb/awangga/.env` (`MONGO_URI`, `DB_NAME`).

```bash
pip install pymongo matplotlib                 # prasyarat
python3 scripts/generate_report.py --list      # lihat daftar sesi
python3 scripts/generate_report.py --session <ID_SESI>
latexmk -pdf main.tex                           # kompilasi ulang
```

Script menulis ke folder `generated/` (di-*ignore* git):

| Berkas | Dipakai untuk |
|--------|---------------|
| `prisma_counts.tex` | mengisi angka diagram PRISMA (dihitung ulang dari `slr_screening`) |
| `extraction_table.tex` | Lampiran A — tabel ekstraksi lengkap (landscape) |
| `included_summary.tex` | ringkasan studi yang disertakan (BAB IV) |
| `figs/pub_year.png` | grafik distribusi tahun publikasi |
| `references.bib` | daftar pustaka dari `manuscript` (bila tersedia) |

`main.tex` otomatis memakai berkas tersebut bila ada; bila tidak, template tetap
tampil dengan placeholder. **Angka PRISMA selalu dihitung ulang dari basis
data**, bukan disalin dari narasi.

Kredensial dibaca dari `.env`; **bila `.env` tidak ada, diambil dari variabel
lingkungan** (`MONGO_URI`, `DB_NAME`, opsional `CROSSREF_MAILTO`).

## Integritas akademik rujukan

Sesuai **[PANDUAN-PENULISAN.md](PANDUAN-PENULISAN.md)**: setiap sitasi harus
berasal dari BibTeX, dan setiap entri BibTeX wajib punya DOI yang terverifikasi
ke **Crossref** (atau **DataCite**). Jalankan pengecek:

```bash
python3 scripts/verify_references.py            # cek sitasi↔BibTeX + DOI (online)
python3 scripts/verify_references.py --offline  # hanya cek sitasi↔BibTeX
```

Keluar dengan kode ≠ 0 bila ada pelanggaran (cocok untuk *pre-commit*/CI).
