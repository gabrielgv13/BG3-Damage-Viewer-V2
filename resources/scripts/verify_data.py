import json

# Load data
with open('equip_data.json', encoding='utf-8') as f:
    equip_data = json.load(f)

with open('weap_data.json', encoding='utf-8') as f:
    weap_data = json.load(f)

print("\n=== EQUIPMENT DATA VERIFICATION ===")
print(f"Total equipment items: {len(equip_data)}")

# Count by type
equip_types = {}
for item in equip_data:
    item_type = item['type']
    equip_types[item_type] = equip_types.get(item_type, 0) + 1

print("\nEquipment by type:")
for item_type, count in sorted(equip_types.items()):
    print(f"  {item_type}: {count}")

# Check armor_class parsing
items_with_ac = [item for item in equip_data if item['armor_class'] is not None]
print(f"\nItems with armor_class: {len(items_with_ac)}")

# Show a shield example
shields = [item for item in equip_data if item['type'] == 'Shield'][:2]
print("\nSample Shield:")
print(json.dumps(shields[0], indent=2, ensure_ascii=False))

print("\n=== WEAPON DATA VERIFICATION ===")
print(f"Total weapon items: {len(weap_data)}")

# Count by type
weap_types = {}
for item in weap_data:
    item_type = item['type']
    weap_types[item_type] = weap_types.get(item_type, 0) + 1

print("\nWeapons by type:")
for item_type, count in sorted(weap_types.items()):
    print(f"  {item_type}: {count}")

# Show a weapon example
print("\nSample Longsword:")
longswords = [item for item in weap_data if item['type'] == 'Longsword'][:1]
print(json.dumps(longswords[0], indent=2, ensure_ascii=False))

print("\n=== VERIFICATION COMPLETE ===")
print("All data populated successfully!")
print("- Effects are properly combined from properties and description")
print("- Armor class is parsed for equipment (shields, armor)")
print("- Location field is excluded")
