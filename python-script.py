import os, json, pathlib

BASE_DIR = pathlib.Path("public")          # <-- start here, not “.”
BASE_URL = "https://kvibespyq.pages.dev"

result = []

for pdf in BASE_DIR.rglob("*.pdf"):
    parts = pdf.relative_to(BASE_DIR).parts   # dept/sem/subject/year/mid-end/file
    if len(parts) != 6:                       # exactly 6 pieces expected
        print("SKIP", pdf)                    # helps you debug later
        continue

    dept, sem, subj, year, exam, filename = parts

    result.append({
        "department": dept.upper(),
        "semester"  : sem,
        "subject"   : subj,
        "year"      : year,
        "exam_type" : exam,
        "filename"  : filename,
        "url"       : f"{BASE_URL}/{'/'.join(parts)}"
    })

result.sort(key=lambda x: (x['department'], x['semester'],
                           x['subject'], x['year']), reverse=True)

with open("index.json", "w") as f:
    json.dump(result, f, indent=2)

print(f"Generated index.json with {len(result)} PYQ files")
