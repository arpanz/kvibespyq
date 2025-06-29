# python-script.py
#
# Generates two JSON indices consumed by the Flutter app:
#   • public/pyq-index.json   – previous-year question papers
#   • public/notes-index.json – lecture / lab notes
#
# PYQ paths now supported
#   1) pyq/<dept>/<sem>/<sub>/<year>/<exam>/<file>.pdf   ← legacy
#   2) pyq/<dept>/<sem>/<sub>/<exam>/<file>.pdf          ← year read from filename
#
# The filename may contain the year anywhere, e.g.
#   AFL_MIDSEM_2023.pdf ,  AFL 2023 Solution.pdf
#
# No changes are required on the Flutter side.

import json
import pathlib
import re

BASE_DIR = pathlib.Path("public")
BASE_URL = "https://kvibespyq.pages.dev"

# First 4-digit block in the filename that looks like a calendar year 1900-2099
YEAR_RE = re.compile(r"(19|20)\d{2}")

EXAM_TYPES = {"mid", "end"}  # folder names accepted for exam type


# --------------------------------------------------------------------------- #
#  PYQ INDEX                                                                  #
# --------------------------------------------------------------------------- #
def generate_pyq_index() -> None:
    entries = []

    for pdf_path in (BASE_DIR / "pyq").rglob("*.pdf"):
        parts = pdf_path.relative_to(BASE_DIR).parts
        if parts[0] != "pyq":
            continue

        # ------------------------------------------------------------------ #
        #  pattern 1: pyq/dep/sem/subj/year/exam/file.pdf   (7 segments)      #
        # ------------------------------------------------------------------ #
        if len(parts) == 7:
            _, dept, sem, subj, year, exam, filename = parts

        # ------------------------------------------------------------------ #
        #  pattern 2: pyq/dep/sem/subj/exam/file.pdf       (6 segments)       #
        #            ↳ year extracted from filename                           #
        # ------------------------------------------------------------------ #
        elif len(parts) == 6:
            _, dept, sem, subj, exam, filename = parts
            m = YEAR_RE.search(filename)
            if not m:
                print(f"SKIP  no year in filename: {pdf_path}")
                continue
            year = m.group(0)

        else:
            print(f"SKIP  malformed path: {pdf_path}")
            continue

        # Accept only 'mid' or 'end' folders for exam type
        exam_lc = exam.lower()
        if exam_lc not in EXAM_TYPES:
            print(f"SKIP  unknown exam type folder: {pdf_path}")
            continue

        entries.append(
            {
                "content_type": "pyq",
                "department": dept.upper(),
                "semester": sem,
                "subject": subj.replace("-", " ").title(),
                "year": year,
                "exam_type": exam_lc,
                "filename": filename,
                "url": f"{BASE_URL}/{'/'.join(parts)}",
            }
        )

    # Sort newest first per department/semester/subject
    entries.sort(
        key=lambda x: (x["department"], x["semester"], x["subject"], x["year"]),
        reverse=True,
    )

    (BASE_DIR / "pyq-index.json").write_text(json.dumps(entries, indent=2))
    print(f"Generated pyq-index.json with {len(entries)} entries")


# --------------------------------------------------------------------------- #
#  NOTES INDEX (unchanged)                                                    #
# --------------------------------------------------------------------------- #
def generate_notes_index() -> None:
    entries = []

    for pdf_path in (BASE_DIR / "notes").rglob("*.pdf"):
        parts = pdf_path.relative_to(BASE_DIR).parts  # notes/dep/sem/subj/file
        if len(parts) != 5 or parts[0] != "notes":
            print(f"SKIP  malformed notes path: {pdf_path}")
            continue

        _, dept, sem, subj, filename = parts

        entries.append(
            {
                "content_type": "notes",
                "department": dept.upper(),
                "semester": sem,
                "subject": subj.replace("-", " ").title(),
                "filename": filename,
                "url": f"{BASE_URL}/{'/'.join(parts)}",
            }
        )

    entries.sort(key=lambda x: (x["department"], x["semester"], x["subject"], x["filename"]))

    (BASE_DIR / "notes-index.json").write_text(json.dumps(entries, indent=2))
    print(f"Generated notes-index.json with {len(entries)} entries")


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    generate_pyq_index()
    generate_notes_index()
