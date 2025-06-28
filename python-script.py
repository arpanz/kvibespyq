# python-script.py
import os, json, pathlib

BASE_DIR = pathlib.Path("public")
BASE_URL = "https://kvibespyq.pages.dev"


def generate_pyq_index() -> None:
    result = []
    for pdf in (BASE_DIR / "pyq").rglob("*.pdf"):
        parts = pdf.relative_to(BASE_DIR).parts           # tuple
        # pyq / dept / sem / subject / year / mid|end / file
        if len(parts) != 7 or parts[0] != "pyq":
            print("SKIP malformed path:", "/".join(parts))
            continue

        _, dept, sem, subj, year, exam, filename = parts
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

    result.sort(key=lambda x: (x["department"], x["semester"],
                               x["subject"], x["year"]), reverse=True)

    (BASE_DIR / "pyq-index.json").write_text(json.dumps(result, indent=2))
    print(f"Generated pyq-index.json with {len(result)} files")


def generate_notes_index() -> None:
    result = []
    for pdf in (BASE_DIR / "notes").rglob("*.pdf"):
        parts = pdf.relative_to(BASE_DIR).parts           # notes / dept / sem / subject / file
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

    result.sort(key=lambda x: (x["department"], x["semester"],
                               x["subject"], x["filename"]))

    (BASE_DIR / "notes-index.json").write_text(json.dumps(result, indent=2))
    print(f"Generated notes-index.json with {len(result)} files")


if __name__ == "__main__":
    generate_pyq_index()
    generate_notes_index()
