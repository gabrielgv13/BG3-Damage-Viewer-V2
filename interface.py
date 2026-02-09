
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

ABILITIES = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
BASE_COSTS = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
TOTAL_POINTS = 27

# --- Parsing Logic ---

def parse_dice_string(dice_str):
    # Parses "1d8" -> (1, 8)
    if not dice_str: return (0, 0)
    parts = dice_str.lower().split('d')
    if len(parts) != 2: return (0, 0)
    return (int(parts[0]), int(parts[1]))

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
    # Scan all equipped items (except weapons themselves for now, simplifying)
    bonus = 0
    # List of slots to check for flat dmg bonuses (Rings, Gloves, Helmets, etc)
    slots = ["slot_helmet", "slot_cape", "slot_armor", "slot_gloves", "slot_boots", "slot_amulet", "slot_ring1", "slot_ring2"]
    
    for tag in slots:
        item_name = dpg.get_value(tag)
        if not item_name or item_name not in EQUIP_MAP: continue
        item = EQUIP_MAP[item_name]
        effects = " ".join(item.get('effects', []))
        
        # Look for "Deal an additional ... (X)"
        # Regex: additional \w+\((\d+)\) or additional 🎲\((\d+)\)
        # Examples: "Deal an additional Acid(2)", "Deal an additional 🎲(2)"
        
        matches = re.findall(r"additional (?:🎲|\w+)\((\d+)\)", effects, re.IGNORECASE)
        for m in matches:
            bonus += int(m)
            
    return bonus

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
    
    if mh_name and mh_name in WEAP_MAP and mh_name != "None":
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
        flat_bonuses = get_global_damage_bonuses()
        
        total_mod = ability_mod + enchant + flat_bonuses
        
        v_min, v_max, v_avg, c_min, c_max, c_avg = calculate_dmg_range(dice, total_mod)
        
        mh_stats = (f"{dice} + {total_mod}\n"
                    f"Damage: {v_min}-{v_max} (Avg {v_avg:.1f})\n"
                    f"Crit:   {c_min}-{c_max} (Avg {c_avg:.1f})")
        
    dpg.set_value("stat_mh_dmg", f"{mh_stats}")

    # --- Ranged ---
    rh_name = dpg.get_value("ranged_main")
    rh_stats = "None"
    
    if rh_name and rh_name in WEAP_MAP and rh_name != "None":
        w_item = WEAP_MAP[rh_name] 
        dice, enchant = parse_weapon_damage(w_item, '2h') # Most bows are 2h
        if dice == "0d0":
             dice, enchant = parse_weapon_damage(w_item, '1h')
             
        ability_mod = dex_mod # Ranged = Dex
        flat_bonuses = get_global_damage_bonuses() + (str_mod if 'Titanstring' in rh_name else 0) 
        
        total_mod = ability_mod + enchant + flat_bonuses
        
        v_min, v_max, v_avg, c_min, c_max, c_avg = calculate_dmg_range(dice, total_mod)
        
        rh_stats = (f"{dice} + {total_mod}\n"
                    f"Damage: {v_min}-{v_max} (Avg {v_avg:.1f})\n"
                    f"Crit:   {c_min}-{c_max} (Avg {c_avg:.1f})")
        
    dpg.set_value("stat_rh_dmg", f"{rh_stats}")


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

import re # Ensure re is available

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
                        dpg.add_text("Ranged Main: --", tag="stat_rh_dmg")
                        
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
