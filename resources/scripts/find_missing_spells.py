import json
import re

# Read and parse spell names from allspells.txt
def parse_allspells_txt(filepath):
    """Extract spell names from allspells.txt with {{LgSAI|SpellName}} format"""
    spell_names = set()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match {{LgSAI|SpellName}} or {{LgSAI|DisplayName|ActualName}}
    pattern = r'\{\{LgSAI\|([^|}]+)(?:\|[^}]*)?\}\}'
    matches = re.findall(pattern, content)
    
    for match in matches:
        # Clean up the spell name
        spell_name = match.strip()
        # Handle special cases like "Bane (spell)" -> "Bane"
        if ' (' in spell_name:
            spell_name = spell_name.split(' (')[0]
        # Handle special cases like "Resistance (Cantrip)" -> "Resistance"
        spell_names.add(spell_name)
    
    return spell_names

# Read spell names from spells.json
def get_spells_from_json(filepath):
    """Extract spell names from spells.json"""
    with open(filepath, 'r', encoding='utf-8') as f:
        spells = json.load(f)
    
    return set(spell['name'] for spell in spells)

# Main comparison
def find_missing_spells():
    print("Loading spell lists...")
    
    allspells_txt = parse_allspells_txt('data/allspells.txt')
    spells_json = get_spells_from_json('data/spells.json')
    
    print(f"\nSpells in allspells.txt: {len(allspells_txt)}")
    print(f"Spells in spells.json: {len(spells_json)}")
    
    # Find missing spells
    missing_spells = allspells_txt - spells_json
    
    print(f"\n{'='*60}")
    print(f"MISSING SPELLS: {len(missing_spells)}")
    print(f"{'='*60}\n")
    
    if missing_spells:
        # Sort alphabetically for easier reading
        for spell in sorted(missing_spells):
            print(f"  - {spell}")
    else:
        print("No missing spells found! Database is complete.")
    
    # Also check for spells in JSON but not in txt (might be extras)
    extra_spells = spells_json - allspells_txt
    if extra_spells:
        print(f"\n{'='*60}")
        print(f"EXTRA SPELLS IN JSON (not in allspells.txt): {len(extra_spells)}")
        print(f"{'='*60}\n")
        for spell in sorted(extra_spells):
            print(f"  - {spell}")
    
    return missing_spells

if __name__ == "__main__":
    missing = find_missing_spells()
    
    if missing:
        print(f"\n{'='*60}")
        print("Next step: Fetch these spells from the BG3 wiki")
        print(f"{'='*60}")
