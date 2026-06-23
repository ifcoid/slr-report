#!/usr/bin/env python3
"""Generate data-driven LaTeX artefacts for the SLR report from MongoDB.

Membaca state SLR (read-only) sesuai ../nsa/GENERATEREPORT.md dan menghasilkan
berkas yang di-\\input oleh main.tex:

  generated/prisma_counts.tex   -> menimpa makro \\n... (angka PRISMA)
  generated/extraction_table.tex-> Lampiran A: tabel ekstraksi (landscape longtable)
  generated/included_summary.tex-> ringkasan studi yang disertakan
  generated/figs/pub_year.png   -> distribusi tahun publikasi

Prinsip GENERATEREPORT.md:
  * Satu sesi = satu SLR (slr_sessions._id).
  * Angka PRISMA DIHITUNG ULANG dari slr_screening (+ data_mining_log), bukan
    disalin dari narasi manuscript.
  * Read-only; kredensial dari /home/adb/awangga/.env (MONGO_URI, DB_NAME).
    Bila .env tidak ada, dibaca dari variabel lingkungan (os.environ).

Pemakaian:
  python3 scripts/generate_report.py --session <SID> [--db slr_agentic_db]
  python3 scripts/generate_report.py --list           # daftar sesi tersedia
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = Path("/home/adb/awangga/.env")
OUT_DIR = ROOT / "generated"
FIG_DIR = OUT_DIR / "figs"


# --------------------------------------------------------------------------- env
def load_env(path: Path) -> dict[str, str]:
    """Baca .env bila ada (nilai .env diutamakan)."""
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def getenv(env: dict[str, str], key: str, default: str | None = None) -> str | None:
    """Ambil dari .env; bila tidak ada, jatuh ke os.environ; lalu default."""
    return env.get(key) or os.environ.get(key) or default


# ------------------------------------------------------------------ tex helpers
import unicodedata

_LATEX_SPECIALS = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}
# Karakter Unicode dari data -> ekuivalen aman untuk pdflatex (inputenc utf8/T1).
_UNICODE_MAP = {
    " ": " ", " ": " ", " ": " ", " ": " ", " ": " ",
    "≈": r"$\approx$", "≤": r"$\le$", "≥": r"$\ge$",
    "≠": r"$\neq$", "×": r"$\times$", "±": r"$\pm$",
    "−": "-", "–": "--", "—": "---", "→": r"$\rightarrow$",
    "“": "``", "”": "''", "‘": "`", "’": "'",
    "…": r"\dots{}", "°": r"$^\circ$", "′": "'", "″": "''",
    "̀": "", "́": "", "̃": "", "̈": "",
    "α": r"$\alpha$", "β": r"$\beta$", "γ": r"$\gamma$",
    "δ": r"$\delta$", "ε": r"$\epsilon$", "θ": r"$\theta$",
    "λ": r"$\lambda$", "μ": r"$\mu$", "π": r"$\pi$",
    "ρ": r"$\rho$", "σ": r"$\sigma$", "τ": r"$\tau$",
    "φ": r"$\phi$", "χ": r"$\chi$", "ψ": r"$\psi$",
    "ω": r"$\omega$", "Δ": r"$\Delta$", "Σ": r"$\Sigma$",
}


def tex_escape(s) -> str:
    """Escape LaTeX specials + petakan Unicode agar aman untuk pdflatex."""
    if s is None:
        return ""
    s = unicodedata.normalize("NFC", str(s)).replace("\n", " ").replace("\r", " ")
    out: list[str] = []
    for c in s:
        if c in _LATEX_SPECIALS:
            out.append(_LATEX_SPECIALS[c])
        elif c in _UNICODE_MAP:
            out.append(_UNICODE_MAP[c])
        elif ord(c) < 128:
            out.append(c)
        else:
            # fallback: transliterasi ke ASCII; bila kosong, abaikan.
            out.append(unicodedata.normalize("NFKD", c).encode("ascii", "ignore").decode())
    return "".join(out)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)}")


# ---------------------------------------------------------------- PRISMA (recompute)
def _abstract_included(p: dict) -> bool:
    """ab = Final_Decision==INCLUDE OR (!Final_Decision && Screener_1==INCLUDE)."""
    fd = p.get("Final_Decision")
    if fd:
        return fd == "INCLUDE"
    return p.get("Screener_1_Decision") == "INCLUDE"


def _abstract_excluded(p: dict) -> bool:
    fd = p.get("Final_Decision")
    if fd:
        return fd == "EXCLUDE"
    return p.get("Screener_1_Decision") == "EXCLUDE"


def _final_full_decision(p: dict) -> str:
    """finalFullDecision (GENERATEREPORT §4)."""
    if p.get("Final_Decision_Full"):
        return p["Final_Decision_Full"]
    d1 = p.get("Screener_1_Decision_Full")
    d2 = p.get("Screener_2_Decision_Full")
    if d1 == "INCLUDE" and d2 == "INCLUDE":
        return "INCLUDE"
    if d1 == "EXCLUDE" and d2 == "EXCLUDE":
        return "EXCLUDE"
    return "UNCERTAIN"


def compute_prisma(screening: list[dict], session: dict) -> tuple[dict, list[str], Counter]:
    """Hitung ulang angka PRISMA dari keputusan final per-paper."""
    dml = session.get("data_mining_log", {}) or {}
    qa = dml.get("QualityAudit", {}) or {}
    dedup = dml.get("Dedup", {}) or {}

    screened = len(screening)
    identified = qa.get("TotalRecords") or (screened + (dedup.get("TotalDuplicates") or 0))
    duplicates = dedup.get("TotalDuplicates") or 0

    included_ta = [p for p in screening if _abstract_included(p)]
    excluded_ta = sum(1 for p in screening if _abstract_excluded(p))
    uncertain_ta = screened - len(included_ta) - excluded_ta

    sought = len(included_ta)
    retrieved = [p for p in included_ta if p.get("full_text_retrieved")]
    not_retrieved = sought - len(retrieved)
    assessed = len(retrieved)

    ft_reasons: Counter = Counter()
    excluded_ft = 0
    included = 0
    for p in retrieved:
        ftd = _final_full_decision(p)
        if ftd == "EXCLUDE":
            excluded_ft += 1
            reason = p.get("Screener_1_Reason_Code_Full") or "Tidak disebutkan"
            ft_reasons[reason] += 1
        elif ftd == "INCLUDE":
            included += 1

    counts = {
        "Identified": identified,
        "Duplicates": duplicates,
        "Screened": screened,
        "ExcludedTA": excluded_ta,
        "UncertainTA": uncertain_ta,
        "Sought": sought,
        "NotRetrieved": not_retrieved,
        "Assessed": assessed,
        "ExcludedFT": excluded_ft,
        "Included": included,
    }

    warnings: list[str] = []
    if screened != len(included_ta) + excluded_ta + uncertain_ta:
        warnings.append("Aritmetika screening title/abstract tidak menutup.")
    if assessed != excluded_ft + included + sum(
        1 for p in retrieved if _final_full_decision(p) == "UNCERTAIN"
    ):
        warnings.append("Aritmetika full-text tidak menutup (ada UNCERTAIN).")
    return counts, warnings, ft_reasons


def emit_prisma_counts(counts: dict) -> None:
    lines = ["% Dibuat otomatis oleh scripts/generate_report.py — JANGAN diedit manual.",
             "% Angka PRISMA dihitung ulang dari slr_screening (GENERATEREPORT.md §9)."]
    for key, macro in [
        ("Identified", "nIdentified"), ("Duplicates", "nDuplicates"),
        ("Screened", "nScreened"), ("ExcludedTA", "nExcludedTA"),
        ("Sought", "nSought"), ("NotRetrieved", "nNotRetrieved"),
        ("Assessed", "nAssessed"), ("ExcludedFT", "nExcludedFT"),
        ("Included", "nIncluded"),
    ]:
        lines.append(f"\\renewcommand{{\\{macro}}}{{{counts[key]}}}")
    write(OUT_DIR / "prisma_counts.tex", "\n".join(lines) + "\n")


# ---------------------------------------------------------------- extraction table
def emit_extraction_table(session: dict, extraction: list[dict]) -> None:
    fs = session.get("framework_selection", {}) or {}
    columns = fs.get("Columns") or fs.get("columns") or []
    # Kunci kolom kerangka ekstraksi.
    keys = [c.get("Key") or c.get("key") for c in columns if (c.get("Key") or c.get("key"))]
    if not keys:
        # fallback: kumpulkan semua key yang muncul di fields
        seen: list[str] = []
        for d in extraction:
            for f in d.get("fields", []) or []:
                k = f.get("key")
                if k and k not in seen:
                    seen.append(k)
        keys = seen
    if not keys:
        print("  (lewati extraction_table: tidak ada kolom/kerangka)")
        return

    header = ["Studi"] + keys
    ncol = len(header)
    colspec = "p{2.2cm} " + " ".join(["p{2.6cm}"] * (ncol - 1))

    rows = []
    for d in sorted(extraction, key=lambda x: str(x.get("Year") or "")):
        if not d.get("extracted"):
            continue
        cite = d.get("paper_id") or d.get("DOI") or d.get("Title") or "?"
        vals = {f.get("key"): f.get("value") for f in (d.get("fields") or [])}
        cells = [tex_escape(cite)] + [tex_escape(vals.get(k, "")) for k in keys]
        rows.append(" & ".join(cells) + r" \\")

    head_tex = " & ".join(f"\\textbf{{{tex_escape(h)}}}" for h in header) + r" \\"
    body = "\n".join(rows) if rows else r"\multicolumn{%d}{c}{(belum ada data)} \\" % ncol
    cont = r"\multicolumn{%d}{r}{\small\itshape bersambung\dots} \\" % ncol
    tex = f"""% Dibuat otomatis oleh scripts/generate_report.py.
\\begin{{landscape}}
\\footnotesize
\\begin{{longtable}}{{{colspec}}}
\\caption{{Tabel Ekstraksi Data Lengkap}}\\label{{tab:ekstraksi}}\\\\
\\toprule {head_tex}
\\midrule \\endfirsthead
\\multicolumn{{{ncol}}}{{l}}{{\\small\\itshape Lanjutan Tabel \\thetable}}\\\\
\\toprule {head_tex}
\\midrule \\endhead
\\midrule {cont}
\\endfoot
\\bottomrule \\endlastfoot
{body}
\\end{{longtable}}
\\end{{landscape}}
"""
    write(OUT_DIR / "extraction_table.tex", tex)


def emit_included_summary(extraction: list[dict]) -> None:
    """Ringkasan studi disertakan (kolom umum bila tersedia)."""
    def pick(d, *names):
        vals = {f.get("key", "").lower(): f.get("value") for f in (d.get("fields") or [])}
        for n in names:
            if vals.get(n):
                return vals[n]
        return ""

    rows = []
    for d in sorted(extraction, key=lambda x: str(x.get("Year") or "")):
        if not d.get("extracted"):
            continue
        cite = tex_escape(d.get("paper_id") or d.get("DOI") or "?")
        method = tex_escape(pick(d, "method", "methods", "metode"))
        model = tex_escape(pick(d, "model", "algorithm", "algoritma"))
        outcome = tex_escape(pick(d, "outcome", "objective", "tujuan"))
        metric = tex_escape(pick(d, "metric", "evaluation", "metrik", "performance"))
        rows.append(f"{cite} & {method} & {model} & {outcome} & {metric} \\\\")
    if not rows:
        print("  (lewati included_summary: tidak ada data ekstraksi)")
        return
    head = (r"\textbf{Studi} & \textbf{Metode} & \textbf{Model} & "
            r"\textbf{Tujuan} & \textbf{Metrik Evaluasi} \\")
    tex = f"""% Dibuat otomatis oleh scripts/generate_report.py.
\\begin{{longtable}}{{>{{\\raggedright}}p{{1.6cm}} p{{2.2cm}} p{{2.4cm}} p{{3.6cm}} p{{3cm}}}}
\\caption{{Ringkasan Studi yang Disertakan}}\\label{{tab:included}}\\\\
\\toprule {head}
\\midrule \\endfirsthead
\\multicolumn{{5}}{{l}}{{\\small\\itshape Lanjutan Tabel \\thetable}}\\\\
\\toprule {head}
\\midrule \\endhead
\\midrule \\multicolumn{{5}}{{r}}{{\\small\\itshape bersambung\\dots}} \\\\ \\endfoot
\\bottomrule \\endlastfoot
{chr(10).join(rows)}
\\end{{longtable}}
"""
    write(OUT_DIR / "included_summary.tex", tex)


# ---------------------------------------------------------------- figure
def emit_pub_year_figure(screening: list[dict]) -> None:
    years: Counter = Counter()
    for p in screening:
        if not (_abstract_included(p) and p.get("full_text_retrieved")
                and _final_full_decision(p) == "INCLUDE"):
            continue
        y = p.get("Year")
        m = re.search(r"(19|20)\d{2}", str(y or ""))
        if m:
            years[int(m.group())] += 1
    if not years:
        print("  (lewati figur tahun: tidak ada tahun pada studi disertakan)")
        return
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:  # pragma: no cover
        print(f"  (lewati figur: matplotlib tidak tersedia: {e})")
        return
    xs = sorted(years)
    ys = [years[x] for x in xs]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.bar([str(x) for x in xs], ys, color="#1f3a93")
    ax.set_xlabel("Tahun publikasi")
    ax.set_ylabel("Jumlah studi")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / "pub_year.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"  wrote {out.relative_to(ROOT)}")


# ---------------------------------------------------------------- references.bib
def emit_references(session: dict) -> None:
    man = session.get("manuscript", {}) or {}
    bib = None
    for k in ("bib", "references_bib", "bibtex", "references"):
        v = man.get(k)
        if isinstance(v, str) and "@" in v:
            bib = v
            break
    if not bib:
        print("  (lewati references.bib: manuscript tidak memuat .bib)")
        return
    write(OUT_DIR / "references.bib", bib)
    print("  -> salin generated/references.bib ke ./references.bib bila ingin dipakai")


# ----------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", help="slr_sessions._id")
    ap.add_argument("--db", help="nama database (default dari .env / slr_agentic_db)")
    ap.add_argument("--list", action="store_true", help="tampilkan daftar sesi")
    args = ap.parse_args()

    env = load_env(ENV_PATH)
    uri = getenv(env, "MONGO_URI")
    db_name = args.db or getenv(env, "DB_NAME", "slr_agentic_db")
    if not uri:
        print("ERROR: MONGO_URI tidak ditemukan (cek .env atau variabel lingkungan).",
              file=sys.stderr)
        return 2

    from pymongo import MongoClient
    from bson.codec_options import CodecOptions
    # Sebagian dokumen lama bisa memuat byte UTF-8 rusak -> ganti, jangan crash.
    codec = CodecOptions(unicode_decode_error_handler="replace")
    client = MongoClient(uri, serverSelectionTimeoutMS=8000)
    db = client.get_database(db_name, codec_options=codec)

    if args.list or not args.session:
        print(f"Sesi pada '{db_name}':")
        for s in db.slr_sessions.find({}, {"_id": 1, "topic": 1, "status": 1}):
            print(f"  {s['_id']}  [{s.get('status','?')}]  {s.get('topic','')}")
        if not args.session:
            print("\nJalankan ulang dengan --session <id>.")
            return 0

    sid = args.session
    session = db.slr_sessions.find_one({"_id": sid})
    if not session:
        print(f"ERROR: sesi '{sid}' tidak ditemukan.", file=sys.stderr)
        return 1
    screening = list(db.slr_screening.find({"session_id": sid}))
    extraction = list(db.slr_extraction.find({"session_id": sid}))

    print(f"Sesi: {sid}  status={session.get('status','?')}")
    print(f"  slr_screening: {len(screening)} dok | slr_extraction: {len(extraction)} dok")

    counts, warnings, ft_reasons = compute_prisma(screening, session)
    print("PRISMA (recompute):", ", ".join(f"{k}={v}" for k, v in counts.items()))
    for w in warnings:
        print(f"  ⚠ WARNING: {w}")
    if ft_reasons:
        print("  Alasan eksklusi full-text:",
              ", ".join(f"{k}={v}" for k, v in ft_reasons.most_common()))

    print("Menulis artefak:")
    emit_prisma_counts(counts)
    emit_extraction_table(session, extraction)
    emit_included_summary(extraction)
    emit_pub_year_figure(screening)
    emit_references(session)
    print("Selesai. Kompilasi ulang: latexmk -pdf main.tex")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
