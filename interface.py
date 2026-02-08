
import dearpygui.dearpygui as dpg
import json
import os

# --- Data Loading ---

def load_data():
    equip_data_path = os.path.join(os.path.dirname(__file__), 'equip_data.json')
    weap_data_path = os.path.join(os.path.dirname(__file__), 'weap_data.json')

    with open(equip_data_path, 'r', encoding='utf-8') as f:
        equip_data = json.load(f)

    with open(weap_data_path, 'r', encoding='utf-8') as f:
        weap_data = json.load(f)
    
    return equip_data, weap_data

EQUIP_DATA, WEAP_DATA = load_data()

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
    Also returns 'ranged' if it appears to be a ranged weapon (checks for 'Bow' in damage or type).
    """
    effects_str = " ".join(weapon_item.get('effects', [])).lower()
    
    modes = set()
    if '1h ' in effects_str or '1h' == effects_str[:2]:
        modes.add('1h')
    if '2h ' in effects_str or '2h' == effects_str[:2]:
        modes.add('2h')
    
    # Fallback/Heuristics if parsing fails or for specific types
    w_type = weapon_item.get('type', '').lower()
    
    is_ranged = 'bow' in effects_str or 'crossbow' in w_type or 'bow' in w_type
    
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

dpg.create_context()

with dpg.window(tag="Primary Window", label="BG3 Inventory"):
    
    # Layout mimicking the logic: 
    # Left column: Helm, Cape, Armor, Gloves, Boots
    # Right column: Amulet, Ring 1, Ring 2
    # Bottom: Weapons
    
    with dpg.group(horizontal=True):
        
        # Left Paperdoll Column
        with dpg.group():
            dpg.add_text("Left Side")
            dpg.add_combo(items=HELMETS, label="Helmet", width=200)
            dpg.add_combo(items=CAPES, label="Cape", width=200)
            dpg.add_combo(items=ARMOR_CLOTHING, label="Armor / Clothing", width=200)
            dpg.add_combo(items=GLOVES, label="Gloves", width=200)
            dpg.add_combo(items=BOOTS, label="Boots", width=200)

        # Spacer
        dpg.add_spacer(width=50)

        # Right Paperdoll Column
        with dpg.group():
            dpg.add_text("Right Side")
            dpg.add_combo(items=AMULETS, label="Amulet", width=200)
            dpg.add_combo(items=RINGS, label="Ring 1", width=200)
            dpg.add_combo(items=RINGS, label="Ring 2", width=200)

    dpg.add_separator()
    dpg.add_text("Weapons")

    with dpg.group(horizontal=True):
        # Melee Group
        with dpg.group():
            dpg.add_text("Melee")
            # Main Hand: Can be any melee weapon (1H or 2H)
            all_melee = sorted(list(set(MELEE_1H + MELEE_2H)))
            dpg.add_combo(items=all_melee, label="Main Hand", tag="melee_main", width=200, callback=update_melee_slots)
            
            # Off Hand: Can be Shield or 1H Weapon
            offhand_options = sorted(list(set(SHIELDS + MELEE_1H)))
            dpg.add_combo(items=offhand_options, label="Off Hand", tag="melee_off", width=200)

        dpg.add_spacer(width=50)

        # Ranged Group
        with dpg.group():
            dpg.add_text("Ranged")
            # Main Hand: Can be any ranged weapon
            all_ranged = sorted(list(set(RANGED_1H + RANGED_2H)))
            dpg.add_combo(items=all_ranged, label="Main Hand", tag="ranged_main", width=200, callback=update_ranged_slots)
            
            # Off Hand: Usually just 1H ranged (Hand Crossbows)
            dpg.add_combo(items=RANGED_1H, label="Off Hand", tag="ranged_off", width=200)

dpg.create_viewport(title='BG3 Damage Analyzer - Inventory', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()
