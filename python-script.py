import os
import json

BASE_DIR = 'public'
result = []

print(f"Current working directory: {os.getcwd()}")
print(f"Looking for files in: {os.path.abspath(BASE_DIR)}")
print(f"Directory exists: {os.path.exists(BASE_DIR)}")
print(f"Directory contents: {os.listdir('.') if os.path.exists('.') else 'Not found'}")

if os.path.exists(BASE_DIR):
    print(f"Contents of {BASE_DIR}: {os.listdir(BASE_DIR)}")

for root, dirs, files in os.walk(BASE_DIR):
    print(f"\nChecking directory: {root}")
    print(f"Subdirectories found: {dirs}")
    print(f"Files found: {files}")
    
    for file in files:
        print(f"Processing file: {file}")
        if file.endswith('.pdf'):
            print(f"✅ Found PDF: {file}")
            full_path = os.path.join(root, file)
            # Fix Windows path separator issues
            rel_path = full_path.replace(BASE_DIR + os.sep, "").replace(os.sep, "/")
            parts = rel_path.split('/')
            
            print(f"Relative path: {rel_path}")
            print(f"Path parts: {parts}")
            
            if len(parts) >= 3:
                branch = parts[0]
                subject = parts[1]
                filename = parts[2]
                
                file_entry = {
                    "branch": branch,
                    "subject": subject,
                    "filename": filename,
                    "url": f"https://kvibespyq.netlify.app/{rel_path}"
                }
                result.append(file_entry)
                print(f"Added to result: {file_entry}")
            else:
                print(f"⚠️ Skipping file with unexpected path structure: {rel_path}")

print(f"\nTotal PDFs found: {len(result)}")
print(f"Final result: {result}")

with open('public/index.json', 'w') as f:
    json.dump(result, f, indent=2)

print("index.json file created successfully!")
