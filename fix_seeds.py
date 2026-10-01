import os
import re

files_to_fix = [
    r'c:\Users\vboys\OneDrive\Desktop\Documents\Car Guide\backend\seed_data_comprehensive.py',
    r'c:\Users\vboys\OneDrive\Desktop\Documents\Car Guide\backend\seed_data.py'
]

for file_path in files_to_fix:
    if not os.path.exists(file_path):
        continue
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace Decimal("0.00") with Decimal("0.08") for electric
    content = re.sub(r'\"electric\":\s*\[\(None,\s*Decimal\(\"0\.00\"\)\)\]', '\"electric\": [(None, Decimal(\"0.08\"))]', content)
    content = re.sub(r'fuel_type=\"electric\",\s*min_price=Decimal\(\"0\"\),\s*max_price=None,\s*defaults={\"rate\":\s*Decimal\(\"0\.00\"\)}', 'fuel_type=\"electric\", min_price=Decimal(\"0\"), max_price=None, defaults={\"rate\": Decimal(\"0.08\")}', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Seed files updated.")
