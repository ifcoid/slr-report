# slr-report

Laporan Lengkap SLR dari Proses sampai Finish.

Template **LaTeX** untuk Laporan *Systematic Literature Review* (SLR) Program
Diploma IV Teknik Informatika, Universitas Logistik dan Bisnis Internasional
(ULBI). Template ini merupakan hasil konversi dari `templateslr.docx`.

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
- Bagian awal bernomor romawi (`i, ii, iii, …`): Abstrak, Abstract,
  Kata Pengantar, Daftar Isi, Daftar Gambar, Daftar Tabel, Daftar Lampiran.
- Penomoran halaman isi **per-BAB**: `I-1`, `II-1`, `III-1`, `IV-1`.
- Judul bab berformat **BAB I**, **BAB II**, … (angka Romawi), sedangkan
  sub-bab, gambar, dan tabel memakai angka Arab (`1`, `1.1`, `2.1`).
- Struktur lengkap: BAB I Pendahuluan, BAB II Landasan Teori,
  BAB III Metodologi Penelitian, BAB IV Penutup, dan Daftar Pustaka.
- Contoh tabel panjang (`longtable`), penyisipan gambar, dan sitasi IEEE.

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
