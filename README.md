# slr-report

Laporan Lengkap SLR dari Proses sampai Finish.

Template **LaTeX** untuk Laporan *Systematic Literature Review* (SLR) Program
Diploma IV Teknik Informatika, Universitas Logistik dan Bisnis Internasional
(ULBI). Format sampul/tata letak mengikuti `templateslr.docx`, sedangkan
**kerangka isi** disesuaikan dengan `../nsa/GENERATEREPORT.md` agar menjadi
laporan SLR yang **komprehensif** dan **layak sebagai artikel Q1**: mengikuti
struktur **IMRaD + PRISMA 2020** dengan elemen transparansi/provenans (xAI).

## Struktur berkas

| Berkas | Keterangan |
|--------|------------|
| `main.tex` | Dokumen utama (preamble + isi laporan). Mulai mengedit dari sini. |
| `references.bib` | Daftar pustaka dalam format BibTeX (gaya IEEE). |
| `images/logo-ulbi.png` | Logo ULBI untuk halaman sampul. |

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

## Cara menyesuaikan

1. **Identitas laporan** — ubah blok `METADATA` di bagian atas `main.tex`
   (judul ID/EN, nama penulis, NIM, prodi, kota, bulan/tahun).
2. **Lembar pengesahan** — sisipkan hasil scan pada bagian yang ditandai
   `LEMBAR PENGESAHAN` di `main.tex` menggunakan `\includegraphics`.
3. **Isi** — tulis pada tiap `\section` / `\subsection` yang sudah disiapkan.
4. **Referensi** — tambahkan entri pada `references.bib`, lalu sitasi dengan
   `\cite{kunci}`.
5. **Margin jilid** — jika dibutuhkan margin kiri 4 cm, ubah `left=3cm`
   menjadi `left=4cm` pada paket `geometry` di `main.tex`.
