

import json
import pathlib
import re

BASE_DIR = pathlib.Path("public")
BASE_URL = "https://kvibespyq.pages.dev"

# year not touching another digit on either side
YEAR_RE = re.compile(r"(?<!\d)(?:19|20)\d{2}(?!\d)", re.ASCII)

EXAM_TYPES = {"mid", "end"}                 # allowed exam-type folders


# ──────────────────────────────────────────────────────────────────────────────
# PYQ INDEX
# ──────────────────────────────────────────────────────────────────────────────
def generate_pyq_index() -> None:
    entries = []

    for pdf_path in (BASE_DIR / "pyq").rglob("*.pdf"):
        parts = pdf_path.relative_to(BASE_DIR).parts
        if parts[0] != "pyq":
            continue

        # pattern 1: pyq/dep/sem/subj/year/exam/file.pdf
        if len(parts) == 7:
            _, dept, sem, subj, year, exam, filename = parts

        # pattern 2: pyq/dep/sem/subj/exam/file.pdf  → year from filename
        elif len(parts) == 6:
            _, dept, sem, subj, exam, filename = parts
            m = YEAR_RE.search(filename)
            if not m:
                print(f"SKIP  no year in filename: {pdf_path.name}")
                continue
            year = m.group(0)

        else:
            print(f"SKIP  malformed path: {pdf_path}")
            continue

        exam_lc = exam.lower()
        if exam_lc not in EXAM_TYPES:
            print(f"SKIP  unknown exam-type folder: {pdf_path}")
            continue

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
            }
        )

    # newest first inside each grouping
    entries.sort(
        key=lambda x: (x["department"], x["semester"], x["subject"], x["year"]),
        reverse=True,
    )

    (BASE_DIR / "pyq-index.json").write_text(json.dumps(entries, indent=2))
    print(f"Generated pyq-index.json with {len(entries)} entries")


# ──────────────────────────────────────────────────────────────────────────────
# NOTES INDEX   (unchanged)
# ──────────────────────────────────────────────────────────────────────────────
def generate_notes_index() -> None:
    entries = []
    # Include both PDF and ZIP files
    for file_path in (BASE_DIR / "notes").rglob("*"):
        if file_path.suffix.lower() not in ['.pdf', '.zip']:
            continue
            
        parts = file_path.relative_to(BASE_DIR).parts
        if len(parts) != 5 or parts[0] != "notes":
            print(f"SKIP malformed notes path: {file_path}")
            continue

        _, dept, sem, subj, filename = parts

        entries.append({
            "content_type": "notes",
            "department": dept.upper(),
            "semester": sem,
            "subject": subj.replace("-", " ").title().upper(),
            "filename": filename,
            "url": f"{BASE_URL}/{'/'.join(parts)}",
        })

    entries.sort(key=lambda x: (x["department"], x["semester"], x["subject"], x["filename"]))
    (BASE_DIR / "notes-index.json").write_text(json.dumps(entries, indent=2))
    print(f"Generated notes-index.json with {len(entries)} entries")

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    generate_pyq_index()
    generate_notes_index()
