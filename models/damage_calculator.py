"""Damage calculation and breakdown utilities."""
import re


class DamageCalculator:
    """Calculates weapon damage and builds damage breakdowns."""
    
    def __init__(self, equipment_data, weapons_data):
        """Initialize with equipment and weapon data."""
        self.equip_map = {item['name']: item for item in equipment_data}
        self.weap_map = {item['name']: item for item in weapons_data}
    
    def calculate_damage_range(self, dice_str, total_mod):
        """
        Calculate damage ranges for normal and critical hits.
        Returns: (min, max, avg, crit_min, crit_max, crit_avg)
        """
        count, sides = self._parse_dice_string(dice_str)
        if count == 0:
            return (0, 0, 0, 0, 0, 0)
        
        # Normal damage
        v_min = count + total_mod
        v_max = (count * sides) + total_mod
        v_avg = (count * (sides + 1) / 2) + total_mod
        
        # Critical (double dice, flat mod stays same)
        c_min = (count * 2) + total_mod
        c_max = (count * 2 * sides) + total_mod
        c_avg = (count * 2 * (sides + 1) / 2) + total_mod
        
        return v_min, v_max, v_avg, c_min, c_max, c_avg
    
    def _parse_dice_string(self, dice_str):
        """Parse dice notation like '2d6' into (num_dice, die_size)."""
        if not dice_str:
            return (0, 0)
        parts = dice_str.lower().split('d')
        if len(parts) != 2:
            return (0, 0)
        return (int(parts[0]), int(parts[1]))
    
    def parse_damage_value(self, value_str):
        """
        Parse damage string like '1d8 + 1' or '2' into (count, sides, flat).
        """
        if not value_str:
            return 0, 0, 0
        
        value_str = value_str.strip()
        
        # Check for dice + bonus: '2d6+3'
        dice_match = re.match(r"^(\d+)d(\d+)(?:\s*\+\s*(\d+))?$", value_str)
        if dice_match:
            count = int(dice_match.group(1))
            sides = int(dice_match.group(2))
            flat = int(dice_match.group(3)) if dice_match.group(3) else 0
            return count, sides, flat
        
        # Check for plain number
        flat_match = re.match(r"^(\d+)$", value_str)
        if flat_match:
            return 0, 0, int(flat_match.group(1))
        
        return 0, 0, 0
    
    def extract_handedness_segment(self, effects_str, handedness):
        """Extract damage segment for specific handedness from effects string."""
        tokens = list(re.finditer(r"(?:^|\s|\))(?P<h>1h|2h)\s+", effects_str))
        for idx, token in enumerate(tokens):
            if token.group("h").lower() == handedness.lower():
                start = token.end()
                end = tokens[idx + 1].start() if idx + 1 < len(tokens) else len(effects_str)
                return effects_str[start:end]
        return ""
    
    def parse_weapon_base_components(self, item, handedness, source_name):
        """
        Parse base weapon damage from effects.
        Returns list of damage components: [{type, dice_count, dice_sides, flat, source}]
        """
        effects_str = " ".join(item.get("effects", []))
        segment = self.extract_handedness_segment(effects_str, handedness)
        
        if not segment:
            return []
        
        components = []
        # Pattern: DamageType(value)
        for match in re.finditer(r"([A-Za-z]+)\(([^)]+)\)", segment):
            dmg_type = match.group(1)
            value_str = match.group(2)
            count, sides, flat = self.parse_damage_value(value_str)
            components.append({
                "type": dmg_type,
                "dice_count": count,
                "dice_sides": sides,
                "flat": flat,
                "source": source_name,
            })
        
        return components
    
    def parse_additional_damage_components(self, effects_str, source_name):
        """
        Parse additional damage from effects (like weapon enchantments).
        Returns list of damage components.
        """
        components = []
        pattern = r"(?:deal\s+)?an\s+additional\s+(?:([A-Za-z]+)|🎲)\(([^)]+)\)"
        
        for match in re.finditer(pattern, effects_str, re.IGNORECASE):
            dmg_type = match.group(1) or "Unspecified"
            value_str = match.group(2)
            count, sides, flat = self.parse_damage_value(value_str)
            
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
    
    def get_equipment_damage_components(self, equipped_items, is_unarmed=False):
        """
        Get damage bonuses from equipped items.
        Returns: (flat_total, components_list)
        """
        flat_total = 0
        components = []
        
        for item_name in equipped_items:
            if not item_name or item_name not in self.equip_map:
                continue
            
            item = self.equip_map[item_name]
            effects_str = " ".join(item.get("effects", []))
            
            # Skip unarmed bonuses if not unarmed
            if (not is_unarmed) and re.search(r"\bunarmed\b", effects_str, re.IGNORECASE):
                continue
            
            item_components = self.parse_additional_damage_components(
                effects_str, f"{item_name} (equipment)"
            )
            
            for comp in item_components:
                components.append(comp)
                if comp["dice_count"] == 0 and comp["flat"]:
                    flat_total += comp["flat"]
        
        return flat_total, components
    
    def parse_weapon_damage(self, item, handedness='1h'):
        """
        Extract dice and enchantment bonus from weapon effects.
        Returns: (dice_str, enchantment)
        """
        effects = " ".join(item.get('effects', []))
        
        # Pattern: "1h Slashing(1d8 + 1)" or "2h Piercing(1d6)"
        pattern = rf"{handedness}\s+\w+\(([\d]+d[\d]+)(?:\s*\+\s*(\d+))?\)"
        match = re.search(pattern, effects, re.IGNORECASE)
        
        if match:
            dice = match.group(1)
            enchant = int(match.group(2)) if match.group(2) else 0
            return dice, enchant
        
        # Fallback: try loose pattern
        loose_pattern = r"\(([\d]+d[\d]+)(?:\s*\+\s*(\d+))?\)"
        match = re.search(loose_pattern, effects)
        if match:
            return match.group(1), (int(match.group(2)) if match.group(2) else 0)
        
        return "0d0", 0
    
    def get_mean_damage(self, dice_str, flat_bonus=0, modifier=0):
        """Calculate average damage for a dice string."""
        count, sides = self._parse_dice_string(dice_str)
        return (count * (sides + 1) / 2) + flat_bonus + modifier
