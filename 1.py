#!/usr/bin/env python3
"""
Builds two index files for the study-materials app:

  • public/pyq-index.json   – previous-year question papers
  • public/notes-index.json – lecture / reference notes
    (Cloudflare-hosted files **plus** any files listed in drive-notes.json)

Run the script from the repository root whenever you add / rename files.
"""

import json
import os
import pathlib
import re
from typing import List, Dict

# ────────────── configuration ────────────────────────────────────────────
BASE_DIR = pathlib.Path("public")           # folder scanned for PDFs / ZIPs
BASE_URL = "https://kvstudy.netlify.app"    # base URL

EXAM_TYPES = {"mid", "end"}                 # accepted folder names for PYQs
YEAR_RE = re.compile(r"(?<!\d)\d{4}(?!\d)") # exactly 4 successive digits
# -------------------------------------------------------------------------


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format (KB, MB, GB)"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


# ═════════════════════════════════════════════════════════════════════════
#                           PYQ  •  INDEX
# ═════════════════════════════════════════════════════════════════════════
def generate_pyq_index() -> None:
    """Scan public/pyq/** and write pyq-index.json"""
    entries: List[Dict] = []

    for pdf_path in (BASE_DIR / "pyq").rglob("*.pdf"):
        parts = pdf_path.relative_to(BASE_DIR).parts
        if parts[0] != "pyq":
            continue

        # Pattern 1  pyq/dep/sem/subj/year/exam/file.pdf
        if len(parts) == 7:
            _, dept, sem, subj, year, exam, filename = parts

        # Pattern 2  pyq/dep/sem/subj/exam/file.pdf  → year inside filename
        elif len(parts) == 6:
            _, dept, sem, subj, exam, filename = parts
            m = YEAR_RE.search(filename)
            if not m:
                print(f"SKIP no year in filename: {pdf_path.name}")
                continue
            year = m.group(0)
        else:
            print(f"SKIP malformed PYQ path: {pdf_path}")
            continue

        exam_lc = exam.lower()
        if exam_lc not in EXAM_TYPES:
            print(f"SKIP unknown exam-type folder: {pdf_path}")
            continue

        # Get file size
        file_size_bytes = pdf_path.stat().st_size
        
        entries.append(
            {
                "content_type": "pyq",
                "department": dept.upper(),
                "semester": sem,
                "subject": subj.replace("-", " ").title().upper(),
                "year": year,
                "exam_type": exam_lc,
                "filename": filename,
                "url": f"{BASE_URL}/{'/'.join(parts)}",
                "file_size_bytes": file_size_bytes,
                "file_size": format_file_size(file_size_bytes),
            }
        )

    # newest year first inside each grouping
    entries.sort(
        key=lambda x: (x["department"], x["semester"], x["subject"], x["year"]),
        reverse=True,
    )

    (BASE_DIR / "pyq-index.json").write_text(json.dumps(entries, indent=2))
    print(f"✅ Generated pyq-index.json with {len(entries)} entries")


# ═════════════════════════════════════════════════════════════════════════
#                         NOTES  •  GOOGLE-DRIVE
# ═════════════════════════════════════════════════════════════════════════
def load_drive_notes() -> List[Dict]:
    """
    Read public/drive-notes.json and return rows ready to be merged into
    notes-index.json.

    Expected JSON shape:
      [
        {
          "filename": "large_file.pdf",
          "url"     : "https://drive.google.com/uc?export=download&id=...",
          "department": "CSE",
          "semester"  : "sem4",
          "subject"   : "DBMS"
        },
        ...
      ]
    """
    fp = BASE_DIR / "drive-notes.json"
    if not fp.exists():
        print("ℹ️  No drive-notes.json found — skipping Drive files")
        return []

    try:
        raw: List[Dict] = json.loads(fp.read_text())
        rows: List[Dict] = []

        for item in raw:
            # basic validation
            if not item.get("filename") or not item.get("url"):
                print(f"SKIP malformed entry in drive-notes.json: {item}")
                continue

            rows.append(
                {
                    "content_type": "notes",
                    "department": item.get("department", "").upper(),
                    "semester": item.get("semester", ""),
                    "subject": item.get("subject", "").upper(),
                    "filename": item["filename"],
                    "url": item["url"],
                }
            )
        print(f"↪︎ Added {len(rows)} Drive notes")
        return rows

    except Exception as exc:
        print(f"⚠️  drive-notes.json invalid: {exc}")
        return []


# ═════════════════════════════════════════════════════════════════════════
#                           NOTES  •  INDEX
# ═════════════════════════════════════════════════════════════════════════
def generate_notes_index() -> None:
    """Scan public/notes/** + Drive list and write notes-index.json"""
    entries: List[Dict] = []

    # ---------- Local (Cloudflare) files ----------
    for file_path in (BASE_DIR / "notes").rglob("*"):
        if file_path.suffix.lower() not in {".pdf", ".zip"}:
            continue

        parts = file_path.relative_to(BASE_DIR).parts
        if len(parts) != 5 or parts[0] != "notes":
            print(f"SKIP malformed notes path: {file_path}")
            continue

        _, dept, sem, subj, filename = parts
        
        # Get file size
        file_size_bytes = file_path.stat().st_size
        
        entries.append(
            {
                "content_type": "notes",
                "department": dept.upper(),
                "semester": sem,
                "subject": subj.replace("-", " ").title().upper(),
                "filename": filename,
                "url": f"{BASE_URL}/{'/'.join(parts)}",
                "file_size_bytes": file_size_bytes,
                "file_size": format_file_size(file_size_bytes),
            }
        )

    # ---------- Google-Drive files ----------
    entries.extend(load_drive_notes())

    # consistent ordering
    entries.sort(
        key=lambda x: (
            x["department"],
            x["semester"],
            x["subject"],
            x["filename"],
        )
    )

    (BASE_DIR / "notes-index.json").write_text(json.dumps(entries, indent=2))
    print(f"✅ Generated notes-index.json with {len(entries)} entries")


# ═════════════════════════════════════════════════════════════════════════
#                               MAIN
# ═════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    generate_pyq_index()
    generate_notes_index()
