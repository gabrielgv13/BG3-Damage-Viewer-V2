import pandas as pd
import json
import re
import sys
import io

# Force stdout to handle utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Define equipment types to extract
EQUIPMENT_TYPES = [
    "Heavy Armour", "Medium Armour", "Light Armour", "Clothing",
    "Shield", "Helmet", "Boots", "Gloves", "Amulet", "Ring", "Cloak"
]

# Define weapon types to extract
WEAPON_TYPES = [
    # One handed simple weapons
    "Club", "Dagger", "Handaxe", "Javelin", "Light Hammer", "Mace", "Sickle",
    # One handed martial weapons
    "Flail", "Morningstar", "Rapier", "Scimitar", "Shortsword", "War Pick",
    # One handed martial ranged weapons
    "Hand Crossbow",
    # Versatile simple weapons
    "Quarterstaff", "Spear",
    # Versatile martial weapons
    "Battleaxe", "Longsword", "Trident", "Warhammer",
    # Two handed simple weapons
    "Greatclub",
    # Two handed ranged simple weapons
    "Light Crossbow", "Shortbow",
    # Two handed martial weapons
    "Glaive", "Greataxe", "Greatsword", "Halberd", "Maul", "Pike",
    # Two handed ranged martial weapons
    "Heavy Crossbow", "Longbow"
]


def parse_armor_class(properties_text):
    """Extract armor class value from properties text."""
    if pd.isna(properties_text):
        return None
    
    # Look for patterns like "🛡️ + 2 AC" or "+ 2 AC"
    match = re.search(r'\+\s*(\d+)\s*AC', str(properties_text))
    if match:
        return int(match.group(1))
    
    return None


def parse_effects(properties, description):
    """Combine properties and description into a list of effects."""
    effects = []
    
    # Add properties if present
    if not pd.isna(properties):
        props_text = str(properties).strip()
        # Split by newline or other delimiters
        for line in props_text.split('\n'):
            line = line.strip()
            # Skip lines that only contain armor class info
            if line and not re.match(r'^🛡️?\s*\+\s*\d+\s*AC\s*$', line):
                effects.append(line)
    
    # Add description if present
    if not pd.isna(description):
        desc_text = str(description).strip()
        # Split by newline for multi-line descriptions
        for line in desc_text.split('\n'):
            line = line.strip()
            if line:
                effects.append(line)
    
    return effects


def load_and_parse_data(file_path):
    """Load the ODS file and extract equipment and weapon data."""
    equipment_data = []
    weapon_data = []
    
    # Load the Excel file
    xl = pd.ExcelFile(file_path, engine="odf")
    
    # Process each act sheet
    for sheet_name in ["ACT 1", "ACT 2", "ACT 3"]:
        print(f"Processing {sheet_name}...")
        df = xl.parse(sheet_name)
        
        # Iterate through rows
        for _, row in df.iterrows():
            item_name = row.get('Name')
            item_type = row.get('Type')
            item_rarity = row.get('Rarity')
            properties = row.get('Properties')
            description = row.get('Description')
            
            # Skip if essential fields are missing
            if pd.isna(item_name) or pd.isna(item_type):
                continue
            
            item_type = str(item_type).strip()
            
            # Check if it's equipment
            if item_type in EQUIPMENT_TYPES:
                armor_class = parse_armor_class(properties)
                effects = parse_effects(properties, description)
                
                equipment_item = {
                    "name": str(item_name).strip(),
                    "type": item_type,
                    "rarity": str(item_rarity).strip() if not pd.isna(item_rarity) else "Unknown",
                    "armor_class": armor_class,
                    "effects": effects
                }
                equipment_data.append(equipment_item)
            
            # Check if it's a weapon
            elif item_type in WEAPON_TYPES:
                effects = parse_effects(properties, description)
                
                weapon_item = {
                    "name": str(item_name).strip(),
                    "type": item_type,
                    "rarity": str(item_rarity).strip() if not pd.isna(item_rarity) else "Unknown",
                    "effects": effects
                }
                weapon_data.append(weapon_item)
    
    return equipment_data, weapon_data


def main():
    """Main function to populate the data files."""
    file_path = r"resources\BG3 Item Index Cheat Sheet.ods"
    
    print("Loading and parsing data...")
    equipment_data, weapon_data = load_and_parse_data(file_path)
    
    print(f"\nFound {len(equipment_data)} equipment items")
    print(f"Found {len(weapon_data)} weapon items")
    
    # Write to JSON files
    print("\nWriting to equip_data.json...")
    with open('equip_data.json', 'w', encoding='utf-8') as f:
        json.dump(equipment_data, f, indent=2, ensure_ascii=False)
    
    print("Writing to weap_data.json...")
    with open('weap_data.json', 'w', encoding='utf-8') as f:
        json.dump(weapon_data, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Data population complete!")
    
    # Print some sample data
    if equipment_data:
        print("\n--- Sample Equipment ---")
        print(json.dumps(equipment_data[0], indent=2, ensure_ascii=False))
    
    if weapon_data:
        print("\n--- Sample Weapon ---")
        print(json.dumps(weapon_data[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
