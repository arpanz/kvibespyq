#!/usr/bin/env python3
"""
Build subject-only JSON indexes for the study-materials app:

  - public/pyq.json   (previous-year question papers)
  - public/notes.json (lecture / reference notes)
"""

import json
import pathlib
import re
from typing import Dict, List

BASE_DIR = pathlib.Path("public")
BASE_URL = "https://kvibespyq.netlify.app"

EXAM_TYPES = {"mid", "end"}
YEAR_RE = re.compile(r"(?<!\d)\d{4}(?!\d)")
TOKEN_SPLIT_RE = re.compile(r"[^a-zA-Z0-9]+")

# Heuristic expansions for common academic abbreviations.
ABBREV_EXPANSIONS = {
    "AFL": "AUTOMATA AND FORMAL LANGUAGES",
    "AI": "ARTIFICIAL INTELLIGENCE",
    "ML": "MACHINE LEARNING",
    "DL": "DEEP LEARNING",
    "NLP": "NATURAL LANGUAGE PROCESSING",
    "DSA": "DATA STRUCTURES AND ALGORITHMS",
    "DS": "DATA STRUCTURES",
    "DBMS": "DATABASE MANAGEMENT SYSTEMS",
    "OS": "OPERATING SYSTEMS",
    "OOP": "OBJECT ORIENTED PROGRAMMING",
    "OOPJ": "OBJECT ORIENTED PROGRAMMING IN JAVA",
    "CC": "CLOUD COMPUTING",
    "CN": "COMPUTER NETWORKS",
    "COA": "COMPUTER ORGANIZATION AND ARCHITECTURE",
    "TOC": "THEORY OF COMPUTATION",
    "SE": "SOFTWARE ENGINEERING",
    "CD": "COMPILER DESIGN",
    "CG": "COMPUTER GRAPHICS",
    "HPC": "HIGH PERFORMANCE COMPUTING",
    "IOT": "INTERNET OF THINGS",
    "DMDW": "DATA MINING AND DATA WAREHOUSING",
    "DOS" : "DISTRIBUTED OPERATING SYSTEMS",
    "IEC" : "INTERNATIONAL ECONOMIC "
}


def format_file_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def subject_in_full(raw_subject: str) -> str:
    tokens = [t for t in TOKEN_SPLIT_RE.split(raw_subject.strip()) if t]
    expanded: List[str] = []
    for token in tokens:
        token_upper = token.upper()
        if token_upper in ABBREV_EXPANSIONS:
            expanded.append(ABBREV_EXPANSIONS[token_upper])
        elif token.isalpha() and len(token) <= 4:
            expanded.append(token_upper)
        else:
            expanded.append(token.lower().title())
    return " ".join(expanded).upper()


def generate_pyq_json() -> None:
    entries: List[Dict] = []

    for pdf_path in (BASE_DIR / "pyq").rglob("*.pdf"):
        parts = pdf_path.relative_to(BASE_DIR).parts
        if parts[0] != "pyq":
            continue

        # Pattern 1  pyq/dep/sem/subj/year/exam/file.pdf
        if len(parts) == 7:
            _, _, _, subj, year, exam, filename = parts

        # Pattern 2  pyq/dep/sem/subj/exam/file.pdf -> year inside filename
        elif len(parts) == 6:
            _, _, _, subj, exam, filename = parts
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

        file_size_bytes = pdf_path.stat().st_size

        entries.append(
            {
                "content_type": "pyq",
                "subject": subj.upper(),
                "in_full": subject_in_full(subj),
                "year": year,
                "exam_type": exam_lc,
                "filename": filename,
                "url": f"{BASE_URL}/{'/'.join(parts)}",
                "file_size_bytes": file_size_bytes,
                "file_size": format_file_size(file_size_bytes),
            }
        )

    entries.sort(
        key=lambda x: (x["subject"], x["year"], x["exam_type"], x["filename"]),
        reverse=True,
    )

    (BASE_DIR / "pyq.json").write_text(json.dumps(entries, indent=2))
    print(f"Generated pyq.json with {len(entries)} entries")


def load_drive_notes() -> List[Dict]:
    fp = BASE_DIR / "drive-notes.json"
    if not fp.exists():
        print("No drive-notes.json found — skipping Drive files")
        return []

    try:
        raw: List[Dict] = json.loads(fp.read_text())
        rows: List[Dict] = []

        for item in raw:
            if not item.get("filename") or not item.get("url"):
                print(f"SKIP malformed entry in drive-notes.json: {item}")
                continue

            subject = item.get("subject", "")
            rows.append(
                {
                    "content_type": "notes",
                    "subject": subject.upper(),
                    "in_full": subject_in_full(subject),
                    "filename": item["filename"],
                    "url": item["url"],
                }
            )
        print(f"Added {len(rows)} Drive notes")
        return rows

    except Exception as exc:
        print(f"drive-notes.json invalid: {exc}")
        return []


def generate_notes_json() -> None:
    entries: List[Dict] = []

    for file_path in (BASE_DIR / "notes").rglob("*"):
        if file_path.suffix.lower() not in {".pdf", ".zip"}:
            continue

        parts = file_path.relative_to(BASE_DIR).parts
        if len(parts) != 5 or parts[0] != "notes":
            print(f"SKIP malformed notes path: {file_path}")
            continue

        _, _, _, subj, filename = parts

        file_size_bytes = file_path.stat().st_size

        entries.append(
            {
                "content_type": "notes",
                "subject": subj.upper(),
                "in_full": subject_in_full(subj),
                "filename": filename,
                "url": f"{BASE_URL}/{'/'.join(parts)}",
                "file_size_bytes": file_size_bytes,
                "file_size": format_file_size(file_size_bytes),
            }
        )

    entries.extend(load_drive_notes())

    entries.sort(
        key=lambda x: (
            x["subject"],
            x["in_full"],
            x["filename"],
        )
    )

    (BASE_DIR / "notes.json").write_text(json.dumps(entries, indent=2))
    print(f"Generated notes.json with {len(entries)} entries")


if __name__ == "__main__":
    generate_pyq_json()
    generate_notes_json()
