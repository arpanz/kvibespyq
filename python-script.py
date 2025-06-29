# python-script.py
#
# Generates two JSON indices that are consumed by the Flutter app:
#   • public/pyq-index.json   – previous-year question papers
#   • public/notes-index.json – lecture / lab notes
#
# The PYQ generator now understands **both** directory layouts:
#   1) pyq/<dept>/<sem>/<sub>/<year>/<exam>/<file>.pdf   ← old
#   2) pyq/<dept>/<sem>/<sub>/<exam>/<file>.pdf          ← new (year in filename)
#
# Nothing else in the app has to change – the JSON structure is identical to
# what the Flutter code expects[1].  The notes logic is untouched[2].

import json, pathlib, re

BASE_DIR = pathlib.Path("public")
BASE_URL = "https://kvibespyq.pages.dev"

YEAR_RE = re.compile(r"(\d{4})")          # first 4-digit number ⇒ year


def generate_pyq_index() -> None:
    result = []

    for pdf in (BASE_DIR / "pyq").rglob("*.pdf"):
        parts = pdf.relative_to(BASE_DIR).parts      # tuple of path segments
        if parts[0] != "pyq":
            continue

        # ------------------------------------------------------------------
        # pattern 1 – legacy: pyq/dep/sem/subj/year/exam/file.pdf  (7 parts)
        # ------------------------------------------------------------------
        if len(parts) == 7:
            _, dept, sem, subj, year, exam, filename = parts

        # ------------------------------------------------------------------
        # pattern 2 – new: pyq/dep/sem/subj/exam/file.pdf  (6 parts)
        #          year is read from the filename (e.g. 2023_algo.pdf)
        # ------------------------------------------------------------------
        elif len(parts) == 6:
            _, dept, sem, subj, exam, filename = parts
            m = YEAR_RE.search(filename)
            if not m:
                print("SKIP  no 4-digit year in filename:", pdf)
                continue
            year = m.group(1)

        # anything else is ignored
        else:
            print("SKIP malformed path:", "/".join(parts))
            continue

        # accept only “mid” or “end” folders for exam type
        if exam.lower() not in ("mid", "end"):
            print("SKIP unknown exam type:", pdf)
            continue

        result.append(
            {
                "content_type": "pyq",
                "department": dept.upper(),
                "semester": sem,
                "subject": subj.replace("-", " ").title(),
                "year": year,
                "exam_type": exam,
                "filename": filename,
                "url": f"{BASE_URL}/{'/'.join(parts)}",
            }
        )

    # newest first inside each grouping (same order the Flutter page expects[1])
    result.sort(
        key=lambda x: (
            x["department"],
            x["semester"],
            x["subject"],
            x["year"],
        ),
        reverse=True,
    )

    (BASE_DIR / "pyq-index.json").write_text(json.dumps(result, indent=2))
    print(f"Generated pyq-index.json with {len(result)} entries")


def generate_notes_index() -> None:  # unchanged[2]
    result = []
    for pdf in (BASE_DIR / "notes").rglob("*.pdf"):
        parts = pdf.relative_to(BASE_DIR).parts  # notes / dept / sem / sub / file
        if len(parts) != 5 or parts[0] != "notes":
            print("SKIP malformed path:", "/".join(parts))
            continue

        _, dept, sem, subj, filename = parts
        result.append(
            {
                "content_type": "notes",
                "department": dept.upper(),
                "semester": sem,
                "subject": subj.replace("-", " ").title(),
                "filename": filename,
                "url": f"{BASE_URL}/{'/'.join(parts)}",
            }
        )

    result.sort(
        key=lambda x: (
            x["department"],
            x["semester"],
            x["subject"],
            x["filename"],
        )
    )

    (BASE_DIR / "notes-index.json").write_text(json.dumps(result, indent=2))
    print(f"Generated notes-index.json with {len(result)} entries")


if __name__ == "__main__":
    generate_pyq_index()
    generate_notes_index()
