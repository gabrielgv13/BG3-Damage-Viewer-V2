"""Armor class calculation utilities."""
import re


class ArmorCalculator:
    """Calculates armor class based on equipped items and stats."""
    
    def __init__(self, equipment_data, weapons_data, shields_list):
        """Initialize with equipment and weapon data."""
        self.equip_map = {item['name']: item for item in equipment_data}
        self.weap_map = {item['name']: item for item in weapons_data}
        self.shields = shields_list
    
    def calculate_ac(self, dex_mod, equipped_items, armor_name, offhand_name):
        """
        Calculate total armor class.
        
        Args:
            dex_mod: Dexterity modifier
            equipped_items: Dict of slot -> item_name for all equipment slots
            armor_name: Name of equipped armor
            offhand_name: Name of offhand item (could be shield)
        
        Returns:
            Dict with keys: base_ac, effective_dex, bonus_ac, final_ac
        """
        base_ac = 10
        max_dex_bonus = 99  # Uncapped by default
        active_ac_bonus = 0
        
        # --- Process Armor ---
        armor_item = self.equip_map.get(armor_name)
        is_unarmored = (not armor_name or armor_name == "None")
        
        if armor_item and armor_name != "None":
            item_type = armor_item.get('type', '')
            effects = " ".join(armor_item.get('effects', []))
            
            # Check if it's clothing (counts as unarmored)
            if armor_item.get('type') == 'Clothing':
                is_unarmored = True
            else:
                is_unarmored = False
            
            # Parse base AC from effects: "Shield X AC"
            match = re.search(r"Shield (\d+) AC", effects)
            if match:
                base_ac = int(match.group(1))
            elif armor_item.get('armor_class'):
                base_ac = armor_item['armor_class']
            
            # Set dex bonus cap based on armor type
            if 'Medium' in item_type:
                max_dex_bonus = 2
            elif 'Heavy' in item_type:
                max_dex_bonus = 0
        
        # --- Process Shield ---
        has_shield = (offhand_name in self.shields and offhand_name != "None")
        
        if has_shield:
            shield_item = self.equip_map.get(offhand_name) or self.weap_map.get(offhand_name)
            if shield_item:
                if shield_item.get('armor_class'):
                    active_ac_bonus += shield_item['armor_class']
                else:
                    active_ac_bonus += 2  # Default shield bonus
        
        # --- Process Misc AC Bonuses ---
        # Check all equipment slots for AC bonuses
        for item_name in equipped_items.values():
            if not item_name or item_name == "None":
                continue
            
            item = self.equip_map.get(item_name) or self.weap_map.get(item_name)
            if not item:
                continue
            
            effects = " ".join(item.get('effects', []))
            
            # Look for "Shield + X AC" bonuses
            matches = re.findall(r"Shield \+ (\d+) AC", effects)
            for m in matches:
                # Special case: Bracers of Defence only work when unarmored and no shield
                if item['name'] == "Bracers of Defence":
                    if is_unarmored and not has_shield:
                        active_ac_bonus += int(m)
                else:
                    active_ac_bonus += int(m)
        
        # --- Calculate Final AC ---
        effective_dex = min(dex_mod, max_dex_bonus)
        final_ac = base_ac + effective_dex + active_ac_bonus
        
        return {
            'base_ac': base_ac,
            'effective_dex': effective_dex,
            'bonus_ac': active_ac_bonus,
            'final_ac': final_ac
        }
    
    def get_ac_breakdown(self, ac_data):
        """
        Format AC calculation breakdown as a string.
        
        Args:
            ac_data: Dict returned from calculate_ac()
        
        Returns:
            Formatted string like "Armor Class: 15 (Base 10 + Dex 2 + Bonus 3)"
        """
        return (f"Armor Class: {ac_data['final_ac']} "
                f"(Base {ac_data['base_ac']} + "
                f"Dex {ac_data['effective_dex']} + "
                f"Bonus {ac_data['bonus_ac']})")
