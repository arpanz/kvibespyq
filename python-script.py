#!/usr/bin/env python3
# python-script.py
# ────────────────────────────────────────────────────────────────
# Generates  public/pyq-index.json  and  public/notes-index.json
# ────────────────────────────────────────────────────────────────

import json
import pathlib
import re

BASE_DIR = pathlib.Path("public")          # root of stored files
BASE_URL = "https://kvibespyq.pages.dev"   # URL prefix

# 4-digit year that is NOT attached to another digit
YEAR_RE = re.compile(r"(?<!\d)(?:19|20)\d{2}(?!\d)")

EXAM_TYPES = {"mid", "end", "suppl"}       # extend if needed

# ───────────────────────── PYQ INDEX ────────────────────────────
def generate_pyq_index() -> None:
    entries: list[dict] = []

    for pdf in (BASE_DIR / "pyq").rglob("*.pdf"):
        parts = pdf.relative_to(BASE_DIR).parts

        # wanted:  pyq/dep/sem/subj/exam/file.pdf   (=6 items)
        if len(parts) != 6 or parts[0] != "pyq":
            print(f"SKIP malformed PYQ path: {pdf}")
            continue

        _, dep, sem, subj, exam_folder, filename = parts
        exam_lc = exam_folder.lower()

        if exam_lc not in EXAM_TYPES:
            print(f"SKIP unknown exam folder: {pdf}")
            continue

        m = YEAR_RE.search(filename)
        if not m:
            print(f"SKIP no year in filename: {filename}")
            continue
        year = m.group(0)

        entries.append(
            {
                "content_type": "pyq",
                "department": dep.upper(),
                "semester": sem,
                "subject": subj.replace("-", " ").upper(),
                "year": year,
                "exam_type": exam_lc,
                "filename": filename,
                "url": f"{BASE_URL}/{'/'.join(parts)}",
            }
        )

    # newest year first, then by exam-type/file name
    entries.sort(
        key=lambda x: (
            x["department"],
            int(x["semester"].replace("sem", "0")),
            x["subject"],
            -int(x["year"]),
            x["exam_type"],
            x["filename"],
        )
    )

    (BASE_DIR / "pyq-index.json").write_text(json.dumps(entries, indent=2))
    print(f"Generated pyq-index.json with {len(entries)} entries")

# ───────────────────────── NOTES INDEX ──────────────────────────
def generate_notes_index() -> None:
    entries: list[dict] = []

    for fp in (BASE_DIR / "notes").rglob("*"):
        if fp.suffix.lower() not in {".pdf", ".zip"}:
            continue

        parts = fp.relative_to(BASE_DIR).parts
        # wanted: notes/dep/sem/subj/file.(pdf|zip)  (=5 items)
        if len(parts) != 5 or parts[0] != "notes":
            print(f"SKIP malformed notes path: {fp}")
            continue

        _, dep, sem, subj, filename = parts
        entries.append(
            {
                "content_type": "notes",
                "department": dep.upper(),
                "semester": sem,
                "subject": subj.replace("-", " ").upper(),
                "filename": filename,
                "url": f"{BASE_URL}/{'/'.join(parts)}",
            }
        )

    entries.sort(
        key=lambda x: (
            x["department"],
            x["semester"],
            x["subject"],
            x["filename"],
        )
    )

    (BASE_DIR / "notes-index.json").write_text(json.dumps(entries, indent=2))
    print(f"Generated notes-index.json with {len(entries)} entries")

# ───────────────────────── MAIN ────────────────────────────────
if __name__ == "__main__":
    generate_pyq_index()
    generate_notes_index()
