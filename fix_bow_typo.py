
import json
import os

def fix_file(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple string replacement
    # The user identified "Bow(" -> "Piercing("
    # e.g., "1h Bow(1d4 + 1)" -> "1h Piercing(1d4 + 1)"
    new_content = content.replace("Bow(", "Piercing(")
    
    if content != new_content:
        print(f"Fixed 'Bow(' typos in {filename}")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        print(f"No 'Bow(' typos found in {filename}")

if __name__ == "__main__":
    fix_file("equip_data.json")
    fix_file("weap_data.json")
