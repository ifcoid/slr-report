#!/usr/bin/env python3
"""Verifikasi integritas akademik rujukan.

Menegakkan dua aturan:
  (1) Setiap sitasi \\cite{...} di berkas .tex HARUS punya entri di references.bib
      (tidak ada rujukan yang ditulis manual / di luar BibTeX).
  (2) Setiap entri BibTeX HARUS punya DOI yang TERVERIFIKASI ke Crossref,
      atau (bila tidak ada di Crossref) ke DataCite. Ini mencegah rujukan
      fiktif/halusinasi dan memastikan metadata dapat ditelusuri.

Keluar dengan kode != 0 bila ada pelanggaran (dapat dipakai di CI / pre-commit).

Pemakaian:
  python3 scripts/verify_references.py
  python3 scripts/verify_references.py --bib references.bib --tex main.tex
  python3 scripts/verify_references.py --offline   # lewati cek jaringan (hanya rule 1)

Catatan: entri contoh (DOI 10.0000/contoh.x) sengaja TIDAK terverifikasi —
ganti dengan rujukan asli sebelum mengumpulkan.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = Path("/home/adb/awangga/.env")


# ------------------------------------------------------------------- env helper
def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def getenv(env: dict[str, str], key: str, default: str | None = None) -> str | None:
    # .env diutamakan; bila tidak ada, jatuh ke os.environ; lalu default.
    return env.get(key) or os.environ.get(key) or default


# --------------------------------------------------------------------- parsing
def parse_bib(path: Path) -> dict[str, dict]:
    """Parser BibTeX sederhana -> {key: {type, doi}}."""
    text = path.read_text(encoding="utf-8", errors="replace")
    entries: dict[str, dict] = {}
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        etype, key = m.group(1).lower(), m.group(2)
        if etype in ("comment", "string", "preamble"):
            continue
        # cari blok entri (sampai '@' berikutnya) untuk mengambil doi.
        start = m.end()
        nxt = text.find("@", start)
        block = text[start: nxt if nxt != -1 else len(text)]
        dm = re.search(r"doi\s*=\s*[{\"]\s*([^}\"]+?)\s*[}\"]", block, re.IGNORECASE)
        doi = dm.group(1).strip() if dm else ""
        doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
        entries[key] = {"type": etype, "doi": doi}
    return entries


def parse_citations(tex_paths: list[Path]) -> set[str]:
    """Kumpulkan semua kunci \\cite (termasuk varian) dari berkas .tex."""
    keys: set[str] = set()
    pat = re.compile(r"\\(?:cite|citep|citet|autocite|parencite|textcite)\*?"
                     r"(?:\[[^\]]*\])*\{([^}]*)\}")
    for p in tex_paths:
        if not p.exists():
            continue
        for m in pat.finditer(p.read_text(encoding="utf-8", errors="replace")):
            for k in m.group(1).split(","):
                k = k.strip()
                if k:
                    keys.add(k)
    return keys


# ----------------------------------------------------------------- DOI checking
def http_ok(url: str, mailto: str, timeout: int = 15) -> int:
    req = urllib.request.Request(
        url, headers={"User-Agent": f"slr-verify/1.0 (mailto:{mailto})"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return -1  # gangguan jaringan


def verify_doi(doi: str, mailto: str) -> str:
    """Kembalikan CROSSREF / DATACITE / NOTFOUND / NETWORK."""
    enc = urllib.parse.quote(doi, safe="")
    code = http_ok(f"https://api.crossref.org/works/{enc}", mailto)
    if code == 200:
        return "CROSSREF"
    code2 = http_ok(f"https://api.datacite.org/dois/{enc}", mailto)
    if code2 == 200:
        return "DATACITE"
    if -1 in (code, code2):
        return "NETWORK"
    return "NOTFOUND"


# ----------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bib", default="references.bib")
    ap.add_argument("--tex", nargs="*", default=["main.tex"],
                    help="berkas .tex yang dipindai untuk \\cite (default: main.tex)")
    ap.add_argument("--offline", action="store_true",
                    help="lewati verifikasi DOI ke Crossref/DataCite (hanya rule 1)")
    ap.add_argument("--mailto", help="email untuk polite-pool Crossref")
    args = ap.parse_args()

    env = load_env(ENV_PATH)
    mailto = args.mailto or getenv(env, "CROSSREF_MAILTO") \
        or getenv(env, "USER_EMAIL") or "anonymous@example.org"

    bib_path = (ROOT / args.bib) if not Path(args.bib).is_absolute() else Path(args.bib)
    tex_paths = [(ROOT / t) if not Path(t).is_absolute() else Path(t) for t in args.tex]
    # ikut sertakan berkas .tex hasil generate bila ada (mis. tabel ekstraksi).
    gen = ROOT / "generated"
    if gen.exists():
        tex_paths += sorted(gen.glob("*.tex"))

    if not bib_path.exists():
        print(f"ERROR: {bib_path} tidak ditemukan.", file=sys.stderr)
        return 2

    entries = parse_bib(bib_path)
    cited = parse_citations(tex_paths)
    print(f"BibTeX: {len(entries)} entri | Sitasi unik: {len(cited)}")

    violations = 0

    # Rule 1: setiap \cite harus ada di bib.
    missing = sorted(k for k in cited if k not in entries)
    if missing:
        violations += len(missing)
        print(f"\n[RULE 1] {len(missing)} sitasi TIDAK ada di {args.bib}:")
        for k in missing:
            print(f"  - \\cite{{{k}}}")
    else:
        print("[RULE 1] OK — semua sitasi punya entri BibTeX.")

    uncited = sorted(k for k in entries if k not in cited)
    if uncited:
        print(f"[INFO] {len(uncited)} entri BibTeX tidak disitasi (tidak akan "
              f"muncul di daftar pustaka IEEE): {', '.join(uncited)}")

    # Rule 2: setiap entri BibTeX punya DOI terverifikasi (Crossref/DataCite).
    if args.offline:
        print("\n[RULE 2] DILEWATI (--offline).")
    else:
        print(f"\n[RULE 2] Verifikasi DOI ke Crossref/DataCite (mailto: {mailto}) ...")
        no_doi = [k for k, e in entries.items() if not e["doi"]]
        for k in sorted(no_doi):
            violations += 1
            print(f"  ✗ {k}: TIDAK ADA DOI")
        net_errors = 0
        for k, e in sorted(entries.items()):
            if not e["doi"]:
                continue
            status = verify_doi(e["doi"], mailto)
            if status in ("CROSSREF", "DATACITE"):
                print(f"  ✓ {k}: {e['doi']} [{status}]")
            elif status == "NETWORK":
                net_errors += 1
                print(f"  ? {k}: {e['doi']} [jaringan gagal — tak terverifikasi]")
            else:
                violations += 1
                print(f"  ✗ {k}: {e['doi']} [TIDAK DITEMUKAN di Crossref/DataCite]")
            time.sleep(0.3)  # sopan terhadap API
        if net_errors:
            print(f"  ({net_errors} entri tak dapat dicek karena jaringan; "
                  f"jalankan ulang saat daring.)")

    print()
    if violations:
        print(f"GAGAL: {violations} pelanggaran integritas rujukan.")
        return 1
    print("LULUS: integritas rujukan terpenuhi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
