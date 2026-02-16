
import dearpygui.dearpygui as dpg
import json
import os
import re
from class_features_loader import ClassFeaturesLoader

# --- Data Loading ---

def load_data():
    equip_data_path = os.path.join(os.path.dirname(__file__), 'data', 'equipment.json')
    weap_data_path = os.path.join(os.path.dirname(__file__), 'data', 'weapons.json')

    with open(equip_data_path, 'r', encoding='utf-8') as f:
        equip_data = json.load(f)

    with open(weap_data_path, 'r', encoding='utf-8') as f:
        weap_data = json.load(f)
    
    return equip_data, weap_data

EQUIP_DATA, WEAP_DATA = load_data()

# --- Load Class Features ---
print("[*] Loading class features, feats, and spells...")
FEATURES_LOADER = ClassFeaturesLoader(data_path="data")
print("[OK] Features loader initialized\n")

# --- Data Parsing & Organization ---

# Categories for simple slots
HELMETS = sorted([i['name'] for i in EQUIP_DATA if i['type'] == 'Helmet'])
ARMOR_CLOTHING = sorted([i['name'] for i in EQUIP_DATA if i['type'] in ['Medium Armour', 'Heavy Armour', 'Light Armour', 'Clothing']])
BOOTS = sorted([i['name'] for i in EQUIP_DATA if i['type'] == 'Boots'])
CAPES = sorted([i['name'] for i in EQUIP_DATA if i['type'] in ['Cape', 'Cloak']])
GLOVES = sorted([i['name'] for i in EQUIP_DATA if i['type'] == 'Gloves'])
AMULETS = sorted([i['name'] for i in EQUIP_DATA if i['type'] == 'Amulet'])
RINGS = sorted([i['name'] for i in EQUIP_DATA if i['type'] == 'Ring'])
SHIELDS = sorted([i['name'] for i in EQUIP_DATA if i['type'] == 'Shield'])

# Weapon categorization
MELEE_1H = []
MELEE_2H = []
RANGED_1H = []
RANGED_2H = []

# Helper to check handedness
def get_weapon_handedness(weapon_item):
    """
    Returns a set containing '1h' and/or '2h' based on effects.
    Also returns 'ranged' if it appears to be a ranged weapon (checks for 'bow' or 'crossbow' in TYPE).
    """
    effects_str = " ".join(weapon_item.get('effects', [])).lower()
    w_type = weapon_item.get('type', '').lower()
    
    modes = set()
    if '1h ' in effects_str or '1h' == effects_str[:2]:
        modes.add('1h')
    if '2h ' in effects_str or '2h' == effects_str[:2]:
        modes.add('2h')
    
    # Updated: Rely strictly on type string for ranged classification to avoid effect description/damage type confusion
    is_ranged = 'bow' in w_type or 'crossbow' in w_type
    
    if is_ranged:
        modes.add('ranged')
    else:
        modes.add('melee')
        
    return modes

for w in WEAP_DATA:
    name = w['name']
    modes = get_weapon_handedness(w)
    
    if 'melee' in modes:
        if '1h' in modes:
            MELEE_1H.append(name)
        if '2h' in modes:
            MELEE_2H.append(name)
    elif 'ranged' in modes:
        if '1h' in modes:
            RANGED_1H.append(name)
        if '2h' in modes:
            RANGED_2H.append(name)
        
        # Fallback for ranged logic if effect parsing wasn't perfect
        # Most bows/xbows are 2h, hand crossbows are 1h.
        w_type = w.get('type', '').lower()
        if 'hand crossbow' in w_type:
            if name not in RANGED_1H: RANGED_1H.append(name)
        elif 'bow' in w_type or 'crossbow' in w_type:
             if name not in RANGED_2H: RANGED_2H.append(name)

MELEE_1H.sort()
MELEE_2H.sort()
RANGED_1H.sort()
RANGED_2H.sort()

# --- UI Logic ---

def update_melee_slots(sender, app_data, user_data):
    """
    Logic:
    - If Main Hand has a STRICTLY 2H weapon (is in MELEE_2H but NOT in MELEE_1H), disable Off Hand.
    - Otherwise, enable Off Hand.
    """
    main_hand_name = dpg.get_value("melee_main")

    if main_hand_name == "Unarmed":
        dpg.set_value("melee_off", "None")
        dpg.configure_item("melee_off", enabled=False)
        return
    
    # Check if selected item is strictly 2H
    is_2h = main_hand_name in MELEE_2H
    is_1h = main_hand_name in MELEE_1H
    
    if is_2h and not is_1h:
        # Strictly 2H
        dpg.set_value("melee_off", "")
        dpg.configure_item("melee_off", enabled=False)
    else:
        # 1H or Versatile or Empty
        dpg.configure_item("melee_off", enabled=True)

def update_ranged_slots(sender, app_data, user_data):
    main_hand_name = dpg.get_value("ranged_main")
    
    is_2h = main_hand_name in RANGED_2H
    is_1h = main_hand_name in RANGED_1H
    
    if is_2h and not is_1h:
        dpg.set_value("ranged_off", "")
        dpg.configure_item("ranged_off", enabled=False)
    else:
        dpg.configure_item("ranged_off", enabled=True)


# --- UI Construction ---

# Helper Maps for fast lookup
dpg.create_context()

EQUIP_MAP = {i['name']: i for i in EQUIP_DATA}
WEAP_MAP = {i['name']: i for i in WEAP_DATA}

DAMAGE_TYPE_COLORS = {
    "slashing": "#C8C8C8",
    "bludgeoning": "#C8C8C8",
    "piercing": "#C8C8C8",
    "cold": "#77C4DE",
    "acid": "#D0DE15",
    "necrotic": "#84C69E",
    "poison": "#91A049",
    "psychic": "#B56BA4",
    "radiant": "#F2D57D",
    "force": "#D36B6C",
    "thunder": "#8266A6",
    "lightning": "#5F93DD",
}

DAMAGE_TYPE_ICON_NAMES = {
    "acid": "Acid.png",
    "bludgeoning": "Bludgeoning.png",
    "cold": "Cold.png",
    "fire": "Fire.png",
    "force": "Force.png",
    "lightning": "Lightning.png",
    "necrotic": "Necrotic.png",
    "piercing": "Piercing.png",
    "poison": "Poison.png",
    "psychic": "Psychic.png",
    "radiant": "Radiant.png",
    "slashing": "Slashing.png",
    "thunder": "Thunder.png",
}

DAMAGE_TYPE_TEXTURES = {}

ABILITIES = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
BASE_COSTS = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
TOTAL_POINTS = 27

# --- Class and Level System ---
# Dynamically load classes from features loader
CLASSES = [name.capitalize() for name in FEATURES_LOADER.get_available_classes()]
MAX_CHARACTER_LEVEL = 12

# Character state: tracks levels in each class
# Format: {"Barbarian": 3, "Fighter": 2, ...}
character_levels = {}

# Character subclass choices
# Format: {"Barbarian": "berserker", "Bard": "college_of_lore", ...}
character_subclasses = {}

# Pending subclass selection when leveling up
# Format: (class_name, level) when waiting for subclass selection
pending_subclass_level = ("", 0)

def get_class_features_display(class_name, level, subclass_name=None):
    """
    Get formatted string of features a character gains from a class at a specific level.
    
    Includes subclass features if the subclass has been selected.
    """
    features = FEATURES_LOADER.get_features_at_level(class_name.lower(), level)
    subclass_features = []
    
    if subclass_name:
        subclass_features = FEATURES_LOADER.get_subclass_features_at_level(
            class_name.lower(), subclass_name.lower(), level
        )
    
    if not features and not subclass_features:
        return ""
    
    lines = [f"\n{'='*60}"]
    lines.append(f"{class_name} - Level {level} Features")
    lines.append('='*60)
    
    for feature in features:
        name = feature.get("name", "Unknown")
        feature_type = feature.get("type", "feature")
        
        if feature_type == "subclassSelection":
            lines.append(f"\n🎭 {name}")
            lines.append(f"   → {feature.get('description', 'Choose your subclass')}")
        else:
            lines.append(f"\n⭐ {name}")
    
    for feature in subclass_features:
        name = feature.get("name", "Unknown")
        lines.append(f"\n📘 {name} (Subclass)")
    
    return "\n".join(lines)

def has_subclass_choice(class_name, level):
    """Check if a class has a subclass choice at a specific level."""
    return FEATURES_LOADER.has_subclass_choice_at_level(class_name.lower(), level)

def get_subclass_choices(class_name):
    """Get available subclass options for a class."""
    choices = FEATURES_LOADER.get_subclass_options(class_name.lower())
    return [choice.replace('_', ' ').title() for choice in choices]

# --- Parsing Logic ---

def parse_dice_string(dice_str):
    # Parses "1d8" -> (1, 8)
    if not dice_str: return (0, 0)
    parts = dice_str.lower().split('d')
    if len(parts) != 2: return (0, 0)
    return (int(parts[0]), int(parts[1]))

def parse_damage_value(value_str):
    """Parse a damage value like '1d8 + 1' or '2' into (count, sides, flat)."""
    if not value_str:
        return 0, 0, 0
    value_str = value_str.strip()
    dice_match = re.match(r"^(\d+)d(\d+)(?:\s*\+\s*(\d+))?$", value_str)
    if dice_match:
        count = int(dice_match.group(1))
        sides = int(dice_match.group(2))
        flat = int(dice_match.group(3)) if dice_match.group(3) else 0
        return count, sides, flat
    flat_match = re.match(r"^(\d+)$", value_str)
    if flat_match:
        return 0, 0, int(flat_match.group(1))
    return 0, 0, 0

def extract_handedness_segment(effects_str, handedness):
    tokens = list(re.finditer(r"(?:^|\s|\))(?P<h>1h|2h)\s+", effects_str))
    for idx, token in enumerate(tokens):
        if token.group("h").lower() == handedness.lower():
            start = token.end()
            end = tokens[idx + 1].start() if idx + 1 < len(tokens) else len(effects_str)
            return effects_str[start:end]
    return ""

def parse_weapon_base_components(item, handedness, source_name):
    effects_str = " ".join(item.get("effects", []))
    segment = extract_handedness_segment(effects_str, handedness)
    if not segment:
        return []
    components = []
    for match in re.finditer(r"([A-Za-z]+)\(([^)]+)\)", segment):
        dmg_type = match.group(1)
        value_str = match.group(2)
        count, sides, flat = parse_damage_value(value_str)
        components.append({
            "type": dmg_type,
            "dice_count": count,
            "dice_sides": sides,
            "flat": flat,
            "source": source_name,
        })
    return components

def parse_additional_damage_components(effects_str, source_name):
    components = []
    pattern = r"(?:deal\s+)?an\s+additional\s+(?:([A-Za-z]+)|🎲)\(([^)]+)\)"
    for match in re.finditer(pattern, effects_str, re.IGNORECASE):
        dmg_type = match.group(1) or "Unspecified"
        value_str = match.group(2)
        count, sides, flat = parse_damage_value(value_str)
        if count == 0 and sides == 0 and flat == 0:
            continue
        components.append({
            "type": dmg_type,
            "dice_count": count,
            "dice_sides": sides,
            "flat": flat,
            "source": source_name,
        })
    return components

def get_equipment_damage_components(is_unarmed=False):
    flat_total = 0
    components = []
    slots = ["slot_helmet", "slot_cape", "slot_armor", "slot_gloves", "slot_boots", "slot_amulet", "slot_ring1", "slot_ring2"]
    for tag in slots:
        item_name = dpg.get_value(tag)
        if not item_name or item_name not in EQUIP_MAP:
            continue
        item = EQUIP_MAP[item_name]
        effects_str = " ".join(item.get("effects", []))
        if (not is_unarmed) and re.search(r"\bunarmed\b", effects_str, re.IGNORECASE):
            continue
        item_components = parse_additional_damage_components(effects_str, f"{item_name} (equipment)")
        for comp in item_components:
            components.append(comp)
            if comp["dice_count"] == 0 and comp["flat"]:
                flat_total += comp["flat"]
    return flat_total, components

def format_damage_components(components):
    lines = []
    for comp in components:
        dmg_type = comp["type"]
        source = comp["source"]
        count = comp["dice_count"]
        sides = comp["dice_sides"]
        flat = comp["flat"]
        if count > 0:
            d_min = count
            d_max = count * sides
            d_avg = (count * (sides + 1)) / 2
            line = f"{dmg_type} ({source}): {count}d{sides} -> {d_min}-{d_max} (Avg {d_avg:.1f})"
            if flat:
                sign = "+" if flat > 0 else ""
                line += f" {sign}{flat} flat"
        else:
            sign = "+" if flat >= 0 else ""
            line = f"{dmg_type} ({source}): {sign}{flat} flat"
        lines.append(line)
    return lines

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return [int(hex_str[i:i + 2], 16) for i in (0, 2, 4)]

def get_damage_type_color(damage_type):
    return DAMAGE_TYPE_COLORS.get(damage_type.lower(), "#FFFFFF")

def normalize_damage_type(damage_type):
    if not damage_type:
        return "Unspecified"
    return damage_type.strip().capitalize()

def get_damage_texture_tag(damage_type):
    return DAMAGE_TYPE_TEXTURES.get(damage_type.lower())

def load_damage_type_textures():
    icon_dir = os.path.join(os.path.dirname(__file__), "icons", "damage_types")
    if not os.path.isdir(icon_dir):
        return

    for dmg_key, filename in DAMAGE_TYPE_ICON_NAMES.items():
        file_path = os.path.join(icon_dir, filename)
        if not os.path.isfile(file_path):
            continue
        width, height, channels, data = dpg.load_image(file_path)
        texture_tag = f"tex_damage_{dmg_key}"
        if not dpg.does_item_exist(texture_tag):
            dpg.add_static_texture(width, height, data, tag=texture_tag)
        DAMAGE_TYPE_TEXTURES[dmg_key] = texture_tag

def render_damage_breakdown(parent_tag, components):
    if not dpg.does_item_exist(parent_tag):
        return
    dpg.delete_item(parent_tag, children_only=True)
    if not components:
        dpg.add_text("(no damage breakdown)", parent=parent_tag, color=[180, 180, 180])
        return

    for comp in components:
        dmg_type_raw = comp["type"]
        dmg_type = normalize_damage_type(dmg_type_raw)
        color = hex_to_rgb(get_damage_type_color(dmg_type_raw))
        texture_tag = get_damage_texture_tag(dmg_type_raw)
        count = comp["dice_count"]
        sides = comp["dice_sides"]
        flat = comp["flat"]
        source = comp["source"]

        if count > 0:
            d_min = count
            d_max = count * sides
            d_avg = (count * (sides + 1)) / 2
            detail = f"{count}d{sides} -> {d_min}-{d_max} (Avg {d_avg:.1f})"
            if flat:
                sign = "+" if flat > 0 else ""
                detail += f" {sign}{flat} flat"
        else:
            sign = "+" if flat >= 0 else ""
            detail = f"{sign}{flat} flat"

        with dpg.group(horizontal=True, parent=parent_tag):
            if texture_tag:
                dpg.add_image(texture_tag, width=16, height=16)
            dpg.add_text(dmg_type, color=color)
            dpg.add_text(f"({source}): {detail}")

with dpg.texture_registry():
    load_damage_type_textures()

# --- Level Management Functions ---

def get_total_level():
    """Returns the total character level across all classes."""
    return sum(character_levels.values())

def can_add_level():
    """Check if a level can be added (total < 12 and a class is selected)."""
    selected_class = dpg.get_value("class_selector")
    return get_total_level() < MAX_CHARACTER_LEVEL and selected_class and selected_class != ""

def on_class_selection_change(sender, app_data, user_data):
    """Called when a class is selected."""
    selected_class = dpg.get_value("class_selector")
    if not selected_class or selected_class == "":
        # Clear UI
        dpg.configure_item("add_level_button", enabled=False)
        dpg.configure_item("subclass_selector_group", show=False)
        dpg.set_value("character_features_text", "")
        return
    
    # Enable Add Level button
    dpg.configure_item("add_level_button", enabled=True)
    dpg.configure_item("subclass_selector_group", show=False)
    dpg.set_value("character_features_text", "")
    update_total_level_display()

def add_level_to_class(sender, app_data, user_data):
    """Add a level to the currently selected class (linear progression)."""
    global pending_subclass_level
    
    selected_class = dpg.get_value("class_selector")
    
    if not selected_class or get_total_level() >= MAX_CHARACTER_LEVEL:
        return
    
    # Get current level for this class
    current_level = character_levels.get(selected_class, 0)
    new_level = current_level + 1
    
    # Check if this new level requires subclass selection
    if has_subclass_choice(selected_class, new_level):
        # Don't add level yet - show subclass selector first
        pending_subclass_level = (selected_class, new_level)
        
        # Show subclass selector
        subclass_options = get_subclass_choices(selected_class)
        dpg.configure_item("subclass_selector", items=subclass_options)
        dpg.set_value("subclass_selector", "")
        dpg.configure_item("subclass_selector_group", show=True)
        dpg.configure_item("add_level_button", enabled=False)
    else:
        # Add level directly
        character_levels[selected_class] = new_level
        pending_subclass_level = ("", 0)
        update_features_display()
        update_total_level_display()
        
        # Check if next level would require subclass selection
        next_level = new_level + 1
        if next_level <= MAX_CHARACTER_LEVEL and has_subclass_choice(selected_class, next_level):
            dpg.configure_item("add_level_button", enabled=True)
        elif new_level < MAX_CHARACTER_LEVEL:
            dpg.configure_item("add_level_button", enabled=True)
        else:
            dpg.configure_item("add_level_button", enabled=False)

def on_subclass_selection_change(sender, app_data, user_data):
    """Called when a subclass is selected during level-up."""
    global pending_subclass_level
    
    selected_subclass = dpg.get_value("subclass_selector")
    
    if not selected_subclass or not pending_subclass_level or pending_subclass_level == ("", 0):
        return
    
    selected_class, new_level = pending_subclass_level
    
    # Convert to lowercase with underscores
    subclass_key = selected_subclass.lower().replace(" ", "_")
    character_subclasses[selected_class] = subclass_key
    
    # Now add the level
    character_levels[selected_class] = new_level
    pending_subclass_level = ("", 0)
    
    # Hide subclass selector
    dpg.configure_item("subclass_selector_group", show=False)
    dpg.set_value("subclass_selector", "")
    
    # Update displays
    update_features_display()
    update_total_level_display()
    
    # Re-enable Add Level if not at max
    if get_total_level() < MAX_CHARACTER_LEVEL:
        dpg.configure_item("add_level_button", enabled=True)
    else:
        dpg.configure_item("add_level_button", enabled=False)

def update_features_display():
    """Display all class features for the current character progression."""
    selected_class = dpg.get_value("class_selector")
    
    if not selected_class or selected_class not in character_levels:
        dpg.set_value("character_features_text", "Select a class and add levels to view features.")
        return
    
    current_level = character_levels.get(selected_class, 0)
    if current_level == 0:
        dpg.set_value("character_features_text", "Add a level to view features.")
        return
    
    subclass = character_subclasses.get(selected_class)
    
    # Get all features from level 1 up to current level
    all_features_text = []
    
    for lvl in range(1, current_level + 1):
        class_features = FEATURES_LOADER.get_features_at_level(selected_class.lower(), lvl)
        
        if class_features:
            all_features_text.append(f"\n{'-' * 50}")
            all_features_text.append(f"{selected_class} - Level {lvl}")
            all_features_text.append('-' * 50)
            
            for feature in class_features:
                name = feature.get("name", "Unknown")
                feature_type = feature.get("type", "feature")
                
                if feature_type == "subclassSelection":
                    all_features_text.append(f"\n  [CHOOSE] {name}")
                else:
                    all_features_text.append(f"  [+] {name}")
        
        # Add subclass features if subclass is selected and we've reached subclass level
        if subclass:
            subclass_level = FEATURES_LOADER.get_subclass_level(selected_class.lower())
            if lvl >= subclass_level:
                subclass_features = FEATURES_LOADER.get_subclass_features_at_level(
                    selected_class.lower(), subclass, lvl
                )
                if subclass_features:
                    if lvl == subclass_level and class_features:
                        # Subclass features start at subclass level
                        all_features_text.append(f"\n  {' ' * 8}(From {subclass.replace('_', ' ').title()} Subclass)")
                    for feature in subclass_features:
                        name = feature.get("name", "Unknown")
                        all_features_text.append(f"  ★ {name} (Subclass)")
    
    features_text = "\n".join(all_features_text) if all_features_text else "No features to display"
    dpg.set_value("character_features_text", features_text)

def update_total_level_display():
    """Update total level and class breakdown display."""
    total_level = get_total_level()
    
    # Update total level display
    dpg.set_value("total_level_text", f"Total Level: {total_level} / {MAX_CHARACTER_LEVEL}")
    
    # Update class breakdown
    class_breakdown = []
    for class_name in sorted(character_levels.keys()):
        if character_levels[class_name] > 0:
            class_breakdown.append(f"{class_name} {character_levels[class_name]}")
    
    if class_breakdown:
        dpg.set_value("class_breakdown_text", " / ".join(class_breakdown))
    else:
        dpg.set_value("class_breakdown_text", "No levels assigned")

def reset_levels(sender, app_data, user_data):
    """Reset all character levels and subclasses."""
    global character_levels, character_subclasses, pending_subclass_level
    character_levels.clear()
    character_subclasses.clear()
    pending_subclass_level = ("", 0)
    dpg.set_value("class_selector", "")
    dpg.configure_item("add_level_button", enabled=False)
    dpg.configure_item("subclass_selector_group", show=False)
    dpg.set_value("character_features_text", "")
    update_total_level_display()


def get_mean_damage(dice_str, flat_bonus=0, modifier=0):
    count, sides = parse_dice_string(dice_str)
    return (count * (sides + 1) / 2) + flat_bonus + modifier

def parse_weapon_damage(item, handedness='1h'):
    # Returns (dice_str, enchantment)
    # Regex to find "1h Slashing(1d8 + 1)" or "1h Piercing(1d6)"
    # Pattern: <handedness> <type>(<dice> [ + <enchant>])
    effects = " ".join(item.get('effects', []))
    pattern = rf"{handedness}\s+\w+\(([\d]+d[\d]+)(?:\s*\+\s*(\d+))?\)"
    match = re.search(pattern, effects, re.IGNORECASE)
    
    if match:
        dice = match.group(1)
        enchant = int(match.group(2)) if match.group(2) else 0
        return dice, enchant
    
    # Fallback/Try loose search if strict pattern fails
    loose_pattern = rf"\(([\d]+d[\d]+)(?:\s*\+\s*(\d+))?\)"
    match = re.search(loose_pattern, effects)
    if match:
        return match.group(1), (int(match.group(2)) if match.group(2) else 0)
        
    return "0d0", 0

def get_global_damage_bonuses():
    flat_total, _ = get_equipment_damage_components(is_unarmed=False)
    return flat_total

# --- Calculation ---

def calculate_mod(score):
    return (score - 10) // 2

def update_abilities(sender, app_data, user_data):
    # Enforce unique checkboxes
    if sender:
        # If +2 is clicked, clear all other +2s
        if "p2_" in sender:
            val = dpg.get_value(sender)
            if val:
                # Disable all other p2 checkboxes
                for ab in ABILITIES:
                    if f"p2_{ab}" != sender: dpg.set_value(f"p2_{ab}", False)
                
                # Also ensure p1 isn't selected for THIS ability (mutually exclusive per ability)
                this_ab = sender.replace("p2_", "")
                dpg.set_value(f"p1_{this_ab}", False)

        # If +1 is clicked, clear all other +1s
        if "p1_" in sender:
            val = dpg.get_value(sender)
            if val:
                # Disable all other p1 checkboxes
                for ab in ABILITIES:
                    if f"p1_{ab}" != sender: dpg.set_value(f"p1_{ab}", False)
                
                # Also ensure p2 isn't selected for THIS ability
                this_ab = sender.replace("p1_", "")
                dpg.set_value(f"p2_{this_ab}", False)
    
    used_points = 0
    for ab in ABILITIES:
        # Read Base Value from Text Tag
        base_str = dpg.get_value(f"base_val_{ab}")
        if not base_str: base_val = 8
        else: base_val = int(base_str)
        
        p2 = dpg.get_value(f"p2_{ab}")
        p1 = dpg.get_value(f"p1_{ab}")
        
        # Cost
        cost = BASE_COSTS.get(base_val, 0)
        used_points += cost
        # dpg.set_value(f"cost_{ab}", str(cost)) # Removed cost column for simplicity? Visual layout doesn't have it explicitly shown in new code block but logic had it. It's fine.
        
        # Total
        bonus = (2 if p2 else 0) + (1 if p1 else 0)
        total = base_val + bonus
        dpg.set_value(f"total_{ab}", str(total))
        
        # Modifier
        mod = calculate_mod(total)
        sign = "+" if mod >= 0 else ""
        dpg.set_value(f"mod_{ab}", f"{sign}{mod}")
        
    dpg.set_value("points_display", f"Points Used: {used_points} / {TOTAL_POINTS}")
    if used_points > TOTAL_POINTS:
        dpg.configure_item("points_display", color=[255, 50, 50])
    else:
        dpg.configure_item("points_display", color=[255, 255, 255])

def recalculate_stats():
    # --- Ability Calculation (Redundant but safe for robust updates) ---
    scores = {}
    mods = {}
    for ab in ABILITIES:
        base_val_str = dpg.get_value(f"base_val_{ab}")
        if not base_val_str: base_val = 8
        else: base_val = int(base_val_str)
        
        p2 = dpg.get_value(f"p2_{ab}")
        p1 = dpg.get_value(f"p1_{ab}")
        
        bonus = (2 if p2 else 0) + (1 if p1 else 0)
        total = base_val + bonus
        scores[ab] = total
        mods[ab] = calculate_mod(total)

    # --- AC Calculation ---
    dex_mod = mods.get("Dexterity", 0)
    
    base_ac = 10
    armor_name = dpg.get_value("slot_armor")
    armor_item = EQUIP_MAP.get(armor_name)
    max_dex_bonus = 99 # Uncapped by default
    
    active_ac_bonus = 0
    
    if armor_item and armor_name != "None":
        itype = armor_item.get('type', '')
        effects = " ".join(armor_item.get('effects', []))
        
        # Parse Base AC from "Shield X AC"
        match = re.search(r"Shield (\d+) AC", effects)
        if match:
            base_ac = int(match.group(1))
        elif armor_item.get('armor_class'):
             # Fallback
             base_ac = armor_item['armor_class']
             
        if 'Medium' in itype:
            max_dex_bonus = 2
        elif 'Heavy' in itype:
            max_dex_bonus = 0
    
    # Shield
    offhand = dpg.get_value("melee_off")
    if offhand in SHIELDS and offhand != "None": # SHIELDS list exists in global scope
        shield_item = EQUIP_MAP.get(offhand) or WEAP_MAP.get(offhand) # Shields in equip data usually
        if shield_item:
            # Check AC explicit or effect
            if shield_item.get('armor_class'):
                active_ac_bonus += shield_item['armor_class']
            else:
                active_ac_bonus += 2 # Default Assumption
    
    # Misc Bonuses (Bracers of Defence, Rings +1 AC)
    # Check all slots for "Shield + X AC" or "Saving Throw +1" -> No, stick to AC
    slots = ["slot_helmet", "slot_cape", "slot_armor", "slot_gloves", "slot_boots", "slot_amulet", "slot_ring1", "slot_ring2", "melee_main", "melee_off"]
    
    is_unarmored = (not armor_name or armor_name == "None") or (armor_item and armor_item.get('type') == 'Clothing')
    has_shield = (offhand in SHIELDS and offhand != "None")
    
    for tag in slots:
        item_name = dpg.get_value(tag)
        if not item_name or item_name == "None": continue
        # Could be weapon or equip
        item = EQUIP_MAP.get(item_name) or WEAP_MAP.get(item_name)
        if not item: continue
        
        effects = " ".join(item.get('effects', []))
        
        # Generic AC bonus "Shield + 1 AC"
        matches = re.findall(r"Shield \+ (\d+) AC", effects)
        for m in matches:
            # Correction: Verify conditional "Bracers of Defence"
            if item['name'] == "Bracers of Defence":
                if is_unarmored and not has_shield:
                    active_ac_bonus += int(m)
            else:
                active_ac_bonus += int(m)
                
    # Final AC
    effective_dex = min(dex_mod, max_dex_bonus)
    final_ac = base_ac + effective_dex + active_ac_bonus
    
    dpg.set_value("stat_ac", f"Armor Class: {final_ac} (Base {base_ac} + Dex {effective_dex} + Bonus {active_ac_bonus})")
    
    # --- Damage Calculation Functions ---
    def calculate_dmg_range(dice_str, total_mod):
        # returns (min, max, avg, crit_min, crit_max, crit_avg)
        count, sides = parse_dice_string(dice_str)
        if count == 0: return (0, 0, 0, 0, 0, 0)
        
        # Normal
        v_min = count + total_mod
        v_max = (count * sides) + total_mod
        v_avg = (count * (sides + 1) / 2) + total_mod
        
        # Crit (Double Dice, flat mod stays same)
        c_min = (count * 2) + total_mod
        c_max = (count * 2 * sides) + total_mod
        c_avg = (count * 2 * (sides + 1) / 2) + total_mod
        
        return v_min, v_max, v_avg, c_min, c_max, c_avg

    str_mod = mods.get("Strength", 0)
    
    # --- Main Hand ---
    mh_name = dpg.get_value("melee_main")
    mh_stats = "None"
    mh_breakdown_components = []
    
    if mh_name == "Unarmed":
        dice = "1d1"
        ability_mod = str_mod
        flat_bonuses, equipment_components = get_equipment_damage_components(is_unarmed=True)
        total_mod = ability_mod + flat_bonuses

        v_min, v_max, v_avg, c_min, c_max, c_avg = calculate_dmg_range(dice, total_mod)

        breakdown_components = [
            {
                "type": "Bludgeoning",
                "dice_count": 0,
                "dice_sides": 0,
                "flat": 1,
                "source": "Unarmed base",
            }
        ]
        breakdown_components.extend(equipment_components)
        if ability_mod:
            breakdown_components.append({
                "type": "Bludgeoning",
                "dice_count": 0,
                "dice_sides": 0,
                "flat": ability_mod,
                "source": "Ability modifier",
            })

        mh_breakdown_components = breakdown_components

        mh_stats = (f"{dice} + {total_mod}\n"
                    f"Damage: {v_min}-{v_max} (Avg {v_avg:.1f})\n"
                    f"Crit:   {c_min}-{c_max} (Avg {c_avg:.1f})")

    elif mh_name and mh_name in WEAP_MAP and mh_name != "None":
        w_item = WEAP_MAP[mh_name]
        is_versatile = "2h" in " ".join(w_item.get('effects', [])) and "1h" in " ".join(w_item.get('effects', []))
        
        # Determine strict handedness
        main_hand_dice_mode = '1h'
        if (not offhand or offhand == "None") and is_versatile:
            main_hand_dice_mode = '2h'
        elif mh_name in MELEE_2H and mh_name not in MELEE_1H:
            main_hand_dice_mode = '2h'
            
        dice, enchant = parse_weapon_damage(w_item, main_hand_dice_mode)
        
        # Ability Mod (Finesse check could be added here, assuming STR for now for melee)
        types = w_item.get('type', '').lower()
        use_dex = False
        if 'finesse' in " ".join(w_item.get('effects', [])).lower():
            if dex_mod > str_mod: use_dex = True
            
        ability_mod = dex_mod if use_dex else str_mod
        flat_bonuses, equipment_components = get_equipment_damage_components(is_unarmed=False)
        
        total_mod = ability_mod + enchant + flat_bonuses
        
        v_min, v_max, v_avg, c_min, c_max, c_avg = calculate_dmg_range(dice, total_mod)
        
        breakdown_components = []
        base_components = parse_weapon_base_components(w_item, main_hand_dice_mode, f"{mh_name} (weapon)")
        breakdown_components.extend(base_components)
        breakdown_components.extend(parse_additional_damage_components(
            " ".join(w_item.get("effects", [])), f"{mh_name} (weapon effect)"
        ))
        breakdown_components.extend(equipment_components)

        base_type = base_components[0]["type"] if base_components else "Weapon"
        if ability_mod:
            breakdown_components.append({
                "type": base_type,
                "dice_count": 0,
                "dice_sides": 0,
                "flat": ability_mod,
                "source": "Ability modifier",
            })

        mh_breakdown_components = breakdown_components

        mh_stats = (f"{dice} + {total_mod}\n"
                    f"Damage: {v_min}-{v_max} (Avg {v_avg:.1f})\n"
                    f"Crit:   {c_min}-{c_max} (Avg {c_avg:.1f})")
        
    dpg.set_value("stat_mh_dmg", f"{mh_stats}")
    render_damage_breakdown("mh_breakdown", mh_breakdown_components)

    # --- Ranged ---
    rh_name = dpg.get_value("ranged_main")
    rh_stats = "None"
    rh_breakdown_components = []
    
    if rh_name and rh_name in WEAP_MAP and rh_name != "None":
        w_item = WEAP_MAP[rh_name] 
        dice, enchant = parse_weapon_damage(w_item, '2h') # Most bows are 2h
        if dice == "0d0":
             dice, enchant = parse_weapon_damage(w_item, '1h')
             
        ability_mod = dex_mod # Ranged = Dex
        flat_bonuses, equipment_components = get_equipment_damage_components(is_unarmed=False)
        if 'Titanstring' in rh_name:
            flat_bonuses += str_mod
        
        total_mod = ability_mod + enchant + flat_bonuses
        
        v_min, v_max, v_avg, c_min, c_max, c_avg = calculate_dmg_range(dice, total_mod)
        
        breakdown_components = []
        base_components = parse_weapon_base_components(w_item, '2h', f"{rh_name} (weapon)")
        if not base_components:
            base_components = parse_weapon_base_components(w_item, '1h', f"{rh_name} (weapon)")
        breakdown_components.extend(base_components)
        breakdown_components.extend(parse_additional_damage_components(
            " ".join(w_item.get("effects", [])), f"{rh_name} (weapon effect)"
        ))
        breakdown_components.extend(equipment_components)

        base_type = base_components[0]["type"] if base_components else "Weapon"
        if ability_mod:
            breakdown_components.append({
                "type": base_type,
                "dice_count": 0,
                "dice_sides": 0,
                "flat": ability_mod,
                "source": "Ability modifier",
            })
        if 'Titanstring' in rh_name and str_mod:
            breakdown_components.append({
                "type": base_type,
                "dice_count": 0,
                "dice_sides": 0,
                "flat": str_mod,
                "source": "Titanstring bonus",
            })

        rh_breakdown_components = breakdown_components

        rh_stats = (f"{dice} + {total_mod}\n"
                    f"Damage: {v_min}-{v_max} (Avg {v_avg:.1f})\n"
                    f"Crit:   {c_min}-{c_max} (Avg {c_avg:.1f})")
        
    dpg.set_value("stat_rh_dmg", f"{rh_stats}")
    render_damage_breakdown("rh_breakdown", rh_breakdown_components)
    
    # Update class features display
    update_features_display()
    
    # Sync displayed features to the "display_features_text" tag
    features_content = dpg.get_value("character_features_text")
    if features_content and features_content != "No features selected":
        dpg.set_value("display_features_text", features_content)


def on_selection_change(sender, app_data, user_data):
    # Update Description Text
    item_name = app_data
    desc_tag = user_data # We pass the text tag as user_data
    
    if item_name:
        item = EQUIP_MAP.get(item_name) or WEAP_MAP.get(item_name)
        if item:
            effects = item.get('effects', [])
            # Format nicely
            text = "\n".join([f"- {e}" for e in effects])
            dpg.set_value(desc_tag, text)
        else:
            dpg.set_value(desc_tag, "")
    else:
        dpg.set_value(desc_tag, "")
        
    # Trigger Logic callbacks (enable/disable slots)
    if sender == "melee_main": update_melee_slots(sender, app_data, user_data)
    if sender == "ranged_main": update_ranged_slots(sender, app_data, user_data)
    
    # Recalculate
    recalculate_stats()

# Wrappers for ability updates to also trigger stats
def update_abilities_wrapper(sender, app_data, user_data):
    update_abilities(sender, app_data, user_data)
    recalculate_stats()

# Re-construction of Window for Split View
# dpg.delete_item("Primary Window") # Clear old

with dpg.window(tag="Primary Window", label="BG3 Damage Analyzer"):
    
    with dpg.table(header_row=False, resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_innerV=True):
        dpg.add_table_column(label="Controls", width_stretch=True, init_width_or_weight=0.6)
        dpg.add_table_column(label="Stats", width_stretch=True, init_width_or_weight=0.4)
        
        with dpg.table_row():
            # --- LEFT COLUMN: INPUTS ---
            with dpg.group():
                
                # --- ABILITY SCORES (Moved to Top) ---
                dpg.add_text("Ability Scores", color=[255, 215, 0])
                
                with dpg.group():
                    dpg.add_text(f"Points Used: 0 / {TOTAL_POINTS}", tag="points_display")
                    with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True, borders_innerV=True):
                        dpg.add_table_column(label="Ability")
                        dpg.add_table_column(label="Base", width_fixed=True)
                        dpg.add_table_column(label="+2", width_fixed=True)
                        dpg.add_table_column(label="+1", width_fixed=True)
                        dpg.add_table_column(label="Total", width_fixed=True)
                        dpg.add_table_column(label="Mod", width_fixed=True)

                        # Helper for point buy buttons
                        def change_base(sender, app_data, user_data):
                            # user_data is (ability_name, increment)
                            ab, inc = user_data
                            current = dpg.get_value(f"base_{ab}") # This is now an int value stored in a hidden field or text? 
                            # Wait, we need to store the state. 
                            # Let's use dpg.set_value on a text item or keep the slider but hidden? 
                            # Simpler: use a dpg.add_input_int or similar as state, but we want buttons.
                            # We will use dpg.get_value of the text field 'base_val_{ab}' and parse it.
                            
                            # Actually, let's keep the value in a hidden int variable or just use the label text
                            # Better: Valid Base range 8-15
                            
                            val = int(dpg.get_value(f"base_val_{ab}"))
                            new_val = val + inc
                            if new_val < 8: new_val = 8
                            if new_val > 15: new_val = 15
                            
                            dpg.set_value(f"base_val_{ab}", str(new_val))
                            update_abilities_wrapper(None, None, None)

                        for ab in ABILITIES:
                            with dpg.table_row():
                                dpg.add_text(ab)
                                
                                # Custom +/- UI
                                with dpg.group(horizontal=True):
                                    dpg.add_button(label="-", callback=change_base, user_data=(ab, -1), width=20)
                                    dpg.add_text("8", tag=f"base_val_{ab}")
                                    dpg.add_button(label="+", callback=change_base, user_data=(ab, 1), width=20)
                                
                                dpg.add_checkbox(tag=f"p2_{ab}", callback=update_abilities_wrapper)
                                dpg.add_checkbox(tag=f"p1_{ab}", callback=update_abilities_wrapper)
                                dpg.add_text("8", tag=f"total_{ab}")
                                dpg.add_text("-1", tag=f"mod_{ab}")

                # --- CLASS & LEVEL SYSTEM ---
                dpg.add_text("Class & Level System", color=[255, 215, 0])
                
                with dpg.group():
                    # Total level display
                    dpg.add_text("Total Level: 0 / 12", tag="total_level_text", color=[100, 255, 100])
                    dpg.add_text("No levels assigned", tag="class_breakdown_text", color=[180, 180, 180])
                    
                    dpg.add_spacer(height=10)
                    
                    # Class selection
                    with dpg.group(horizontal=True):
                        dpg.add_text("Select Class:")
                        dpg.add_combo(items=CLASSES, tag="class_selector", callback=on_class_selection_change, width=150, default_value="")
                    
                    dpg.add_spacer(height=5)
                    
                    # Level progression (linear)
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Add Level", tag="add_level_button", callback=add_level_to_class, enabled=False, width=120)
                        dpg.add_button(label="Reset All", callback=reset_levels, width=100)
                    
                    dpg.add_spacer(height=5)
                    
                    # Subclass selection (hidden by default)
                    with dpg.group(tag="subclass_selector_group", show=False):
                        dpg.add_text("Choose Your Subclass:", color=[200, 180, 100])
                        with dpg.group(horizontal=True):
                            dpg.add_combo(items=[], tag="subclass_selector", callback=on_subclass_selection_change, width=250)
                        dpg.add_text("(Select your subclass to continue leveling up)", color=[150, 150, 100])
                    
                    dpg.add_spacer(height=10)
                    dpg.add_text("Class Features", color=[200, 200, 100])
                    dpg.add_text("Select a class and add levels to see features.", tag="character_features_text", color=[180, 180, 180], wrap=400)
                
                dpg.add_separator()
                
                # --- EQUIPMENT ---
                dpg.add_text("Equipment", color=[255, 215, 0])
                
                # Helper to build slot
                def add_slot(label, items, tag, desc_tag, width=200):
                    dpg.add_text(label)
                    # Add None option
                    item_list = ["None"] + items
                    dpg.add_combo(items=item_list, tag=tag, callback=on_selection_change, user_data=desc_tag, width=width)
                    dpg.add_text("", tag=desc_tag, color=[150, 150, 150], wrap=250)
                    dpg.add_spacer(height=5)

                with dpg.group(horizontal=True):
                    # LEFT SIDE: Head, Cape, Torso, Gloves, Boots
                    with dpg.group():
                        add_slot("Helmet", HELMETS, "slot_helmet", "desc_helmet")
                        add_slot("Cape", CAPES, "slot_cape", "desc_cape")
                        add_slot("Armor", ARMOR_CLOTHING, "slot_armor", "desc_armor")
                        add_slot("Gloves", GLOVES, "slot_gloves", "desc_gloves")
                        add_slot("Boots", BOOTS, "slot_boots", "desc_boots")
                    
                    dpg.add_spacer(width=20)

                    # RIGHT SIDE: Amulet, Ring 1, Ring 2
                    with dpg.group():
                        add_slot("Amulet", AMULETS, "slot_amulet", "desc_amulet")
                        add_slot("Ring 1", RINGS, "slot_ring1", "desc_ring1")
                        add_slot("Ring 2", RINGS, "slot_ring2", "desc_ring2")
                
                dpg.add_separator()
                
                # --- WEAPONS ---
                dpg.add_text("Weapons", color=[255, 215, 0])
                
                all_melee = sorted(list(set(MELEE_1H + MELEE_2H)))
                if "Unarmed" not in all_melee:
                    all_melee = ["Unarmed"] + all_melee
                offhand_options = sorted(list(set(SHIELDS + MELEE_1H)))
                all_ranged = sorted(list(set(RANGED_1H + RANGED_2H)))

                with dpg.group(horizontal=True):
                    # MELEE (Left)
                    with dpg.group():
                        dpg.add_text("Melee Main Hand")
                        dpg.add_combo(items=["None"] + all_melee, tag="melee_main", callback=on_selection_change, user_data="desc_melee_main", width=250)
                        dpg.add_text("", tag="desc_melee_main", color=[150, 150, 150], wrap=250)
                        
                        dpg.add_text("Melee Off Hand")
                        dpg.add_combo(items=["None"] + offhand_options, tag="melee_off", callback=on_selection_change, user_data="desc_melee_off", width=250)
                        dpg.add_text("", tag="desc_melee_off", color=[150, 150, 150], wrap=250)
                    
                    dpg.add_spacer(width=20)

                    # RANGED (Right)
                    with dpg.group():
                        dpg.add_text("Ranged Main Hand")
                        dpg.add_combo(items=["None"] + all_ranged, tag="ranged_main", callback=on_selection_change, user_data="desc_ranged_main", width=250)
                        dpg.add_text("", tag="desc_ranged_main", color=[150, 150, 150], wrap=250)
                        
                        dpg.add_text("Ranged Off Hand")
                        dpg.add_combo(items=["None"] + RANGED_1H, tag="ranged_off", callback=on_selection_change, user_data="desc_ranged_off", width=250)
                        dpg.add_text("", tag="desc_ranged_off", color=[150, 150, 150], wrap=250)

            # --- RIGHT COLUMN: STATS ---
            with dpg.group():
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=20)
                    with dpg.group():
                        dpg.add_text("Character Statistics", color=[255, 215, 0])
                        dpg.add_separator()
                        dpg.add_spacer(height=10)
                        
                        dpg.add_text("Armor Class (AC)", color=[100, 200, 255])
                        dpg.add_text("AC: 10", tag="stat_ac")
                        
                        dpg.add_spacer(height=20)
                        dpg.add_text("Damage Output", color=[255, 100, 100])
                        dpg.add_text("Melee Main: --", tag="stat_mh_dmg")
                        dpg.add_text("Melee Breakdown", color=[200, 200, 200])
                        dpg.add_group(tag="mh_breakdown")
                        dpg.add_spacer(height=10)
                        dpg.add_text("Ranged Main: --", tag="stat_rh_dmg")
                        dpg.add_text("Ranged Breakdown", color=[200, 200, 200])
                        dpg.add_group(tag="rh_breakdown")
                        
                        dpg.add_spacer(height=20)
                        dpg.add_text("Class Features", color=[150, 255, 150])
                        with dpg.group():
                            dpg.add_text("Select a class and level to view class features.", tag="display_features_text", color=[180, 180, 180], wrap=700)
                        
                        dpg.add_spacer(height=20)
                        dpg.add_text("Active Effects Log", color=[150, 255, 150])
                        # Placeholder for future thorough log
                        dpg.add_text("(Calculations include attribute modifiers,\nweapon enchantments, and flat bonuses\nfrom equipped items.)", color=[180,180,180])

dpg.create_viewport(title='BG3 Damage Analyzer', width=1280, height=800)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()
