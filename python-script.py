import os
import json

BASE_DIR = './public'
BASE_URL = 'https://kvibespyq.pages.dev'
result = []

for root, dirs, files in os.walk(BASE_DIR):
    for file in files:
        if file.endswith('.pdf'):
            full_path = os.path.join(root, file)
            rel_path = full_path.replace(BASE_DIR + "/", "")
            parts = rel_path.split('/')
            
            if len(parts) >= 4:
                department = parts[0]
                semester = parts[1] 
                subject = parts[2]
                year = parts[3]
                
                if len(parts) == 6:  # dept/sem/subject/year/exam_type/filename
                    exam_type = parts[4]
                    filename = parts[5]
                else:  # dept/sem/subject/year/filename
                    filename = parts[4]
                    if 'mid' in filename.lower():
                        exam_type = 'mid'
                    elif 'end' in filename.lower():
                        exam_type = 'end'
                    else:
                        exam_type = 'general'
                
                result.append({
                    "department": department.upper(),
                    "semester": semester,
                    "subject": subject.replace('-', ' ').title(),
                    "year": year,
                    "exam_type": exam_type,
                    "filename": filename,
                    "url": f"{BASE_URL}/{rel_path}"
                })

result.sort(key=lambda x: (x['department'], x['semester'], x['subject'], x['year']), reverse=True)

with open('public/index.json', 'w') as f:  # Write to public folder
    json.dump(result, f, indent=2)

print(f"Generated index.json with {len(result)} PYQ files")
