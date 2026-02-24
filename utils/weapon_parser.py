"""Utilities for parsing weapon data and extracting handedness information."""
import re


def get_weapon_handedness(weapon_name, weapons_data):
    """
    Extract handedness from weapon name or properties.
    Returns: 'one-handed', 'two-handed', 'versatile', or None
    """
    weapon_lower = weapon_name.lower()
    
    # Check if weapon exists in weapons_data
    weapon_entry = None
    for weapon in weapons_data:
        if weapon.get('name', '').lower() == weapon_lower:
            weapon_entry = weapon
            break
    
    if weapon_entry:
        # Check properties field
        properties = weapon_entry.get('properties', '').lower()
        if 'two-handed' in properties or 'twohanded' in properties:
            return 'two-handed'
        elif 'versatile' in properties:
            return 'versatile'
        else:
            return 'one-handed'
    
    # Fallback to name parsing
    if '(2h)' in weapon_lower or 'two-handed' in weapon_lower:
        return 'two-handed'
    elif '(1h)' in weapon_lower or 'one-handed' in weapon_lower:
        return 'one-handed'
    elif 'versatile' in weapon_lower:
        return 'versatile'
    
    return None


def parse_dice_string(dice_str):
    """
    Parse dice notation like '2d6', '1d8', etc.
    Returns tuple: (num_dice, die_size) or (0, 0) if invalid
    """
    if not dice_str:
        return (0, 0)
    
    dice_str = dice_str.strip().lower()
    match = re.match(r'(\d+)d(\d+)', dice_str)
    
    if match:
        num_dice = int(match.group(1))
        die_size = int(match.group(2))
        return (num_dice, die_size)
    
    return (0, 0)


def parse_damage_value(damage_str):
    """
    Parse damage string which can be:
    - Dice notation: '2d6', '1d8+2'
    - Fixed number: '5', '10'
    - Range: '2-12'
    
    Returns dict: {
        'dice': (num, size),
        'bonus': int,
        'fixed': int or None,
        'type': 'dice' or 'fixed'
    }
    """
    if not damage_str:
        return {'dice': (0, 0), 'bonus': 0, 'fixed': None, 'type': 'dice'}
    
    damage_str = damage_str.strip().lower()
    
    # Check for dice notation with bonus: '2d6+3'
    match = re.match(r'(\d+)d(\d+)\s*\+\s*(\d+)', damage_str)
    if match:
        num_dice = int(match.group(1))
        die_size = int(match.group(2))
        bonus = int(match.group(3))
        return {
            'dice': (num_dice, die_size),
            'bonus': bonus,
            'fixed': None,
            'type': 'dice'
        }
    
    # Check for plain dice notation: '2d6'
    match = re.match(r'(\d+)d(\d+)', damage_str)
    if match:
        num_dice = int(match.group(1))
        die_size = int(match.group(2))
        return {
            'dice': (num_dice, die_size),
            'bonus': 0,
            'fixed': None,
            'type': 'dice'
        }
    
    # Check for fixed number
    match = re.match(r'(\d+)', damage_str)
    if match:
        fixed = int(match.group(1))
        return {
            'dice': (0, 0),
            'bonus': 0,
            'fixed': fixed,
            'type': 'fixed'
        }
    
    return {'dice': (0, 0), 'bonus': 0, 'fixed': None, 'type': 'dice'}


def extract_handedness_segment(weapon_name):
    """
    Extract the handedness segment from weapon name and clean name.
    E.g., "Shortsword (1h)" -> ("Shortsword", "1h")
    """
    match = re.search(r'\(([12]h)\)', weapon_name, re.IGNORECASE)
    if match:
        handedness = match.group(1).lower()
        clean_name = weapon_name[:match.start()].strip()
        return (clean_name, handedness)
    
    return (weapon_name, None)


def categorize_weapon(weapon_entry):
    """
    Categorize a weapon based on its category field.
    Returns: 'melee', 'ranged', or 'unknown'
    """
    category = weapon_entry.get('category', '').lower()
    
    # Melee weapons
    if any(word in category for word in ['simple melee', 'martial melee', 'melee']):
        return 'melee'
    
    # Ranged weapons
    if any(word in category for word in ['simple ranged', 'martial ranged', 'ranged']):
        return 'ranged'
    
    return 'unknown'
