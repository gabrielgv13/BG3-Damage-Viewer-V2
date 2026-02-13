import json
import re
import sys
import io

# Force stdout to handle utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# Emoji to text mapping based on the damage type table
EMOJI_MAP = {
    # Damage types
    '🔨': 'Bludgeoning',
    '🗡️': 'Piercing',
    '🔪': 'Slashing',
    '🧪': 'Acid',
    '⚗️': 'Acid',  # Alembic/flask emoji also represents Acid
    '❄️': 'Cold',
    '🔥': 'Fire',
    '🧨': 'Poison',  # Flask/Poison
    '🐍': 'Poison',  # Snake emoji also represents Poison
    '☠️': 'Necrotic',
    '💀': 'Necrotic',  # Skull emoji also represents Necrotic
    '👁️': 'Psychic',
    '💥': 'Force',
    '✨': 'Radiant',
    '☀️': 'Radiant',  # Sun emoji also represents Radiant
    '⚡': 'Lightning',
    '🌩️': 'Thunder',
    '⛈️': 'Thunder',  # Storm emoji also represents Thunder
    
    # Other common emojis in the data
    '🛡️': 'Shield',
    '🎁': '',  # Gift box - often just indicates loot, can be removed
    '🏹': 'Bow',
    '⚔️': 'Weapon',
}


def replace_emojis_in_text(text):
    """Replace emojis with their text equivalents."""
    if not text:
        return text
    
    # Replace known emojis
    for emoji, replacement in EMOJI_MAP.items():
        if replacement:
            text = text.replace(emoji, replacement)
        else:
            # Remove emoji if replacement is empty
            text = text.replace(emoji, '')
    
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


def remove_spoiler_effects(effects):
    """Remove effects containing 'SPOILER IN NOTE'."""
    if not effects:
        return effects
    
    return [effect for effect in effects if 'SPOILER IN NOTE' not in effect]


def format_item(item):
    """Format a single item by replacing emojis and removing spoilers."""
    # Process effects
    if 'effects' in item and item['effects']:
        # Replace emojis in each effect
        item['effects'] = [replace_emojis_in_text(effect) for effect in item['effects']]
        
        # Remove spoiler effects
        item['effects'] = remove_spoiler_effects(item['effects'])
    
    return item


def format_json_file(input_file, output_file):
    """Format a JSON file by applying all transformations."""
    print(f"\nProcessing {input_file}...")
    
    # Load data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Count spoiler effects before removal
    spoiler_count = sum(
        1 for item in data 
        for effect in item.get('effects', []) 
        if 'SPOILER IN NOTE' in effect
    )
    
    print(f"  Items before formatting: {len(data)}")
    if spoiler_count > 0:
        print(f"  Spoiler effects to remove: {spoiler_count}")
    
    # Format each item
    formatted_data = [format_item(item) for item in data]
    
    # Save formatted data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, indent=2, ensure_ascii=False)
    
    print(f"  Saved formatted data to {output_file}")
    print(f"  Items after formatting: {len(formatted_data)}")


def main():
    """Main function to format both JSON files."""
    print("=" * 60)
    print("BG3 JSON Data Formatter")
    print("=" * 60)
    print("\nOperations:")
    print("  1. Replace emojis with text equivalents")
    print("  2. Remove 'SPOILER IN NOTE' effects")
    print("  3. Clean up extra whitespace")
    
    # Format equipment data
    format_json_file('equip_data.json', 'equip_data.json')
    
    # Format weapon data
    format_json_file('weap_data.json', 'weap_data.json')
    
    print("\n" + "=" * 60)
    print("Formatting Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
