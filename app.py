# fix_structure.py
import os
import shutil

print("Creating services folder structure...")

# Create services directory
os.makedirs('services', exist_ok=True)

# List of service files to move (based on what you have)
service_files = [
    'arxiv_service.py',
    'duckduckgo_service.py', 
    'wikipedia_service.py',
    'weather_service.py',
    'openaq_service.py',
    'wikidata_service.py',
    'openlibrary_service.py',
    'pubmed_service.py',
    'nominatim_service.py',
    'dictionary_service.py',
    'countries_service.py',
    'quotes_service.py',
    'github_service.py',
    'stackexchange_service.py'
]

# Move only files that exist
moved_files = []
for file in service_files:
    if os.path.exists(file):
        shutil.move(file, f'services/{file}')
        moved_files.append(file)
        print(f"✓ Moved {file} to services/")

# Create __init__.py in services folder
with open('services/__init__.py', 'w') as f:
    f.write('# Services package\n')
print("✓ Created services/__init__.py")

print(f"\nDone! Moved {len(moved_files)} files.")
print("\nNow update your app.py to use the original imports:")
print("from services.arxiv_service import search_arxiv")
print("from services.duckduckgo_service import search_duckduckgo")
print("# ... etc.")
