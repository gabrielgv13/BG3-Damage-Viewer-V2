#!/usr/bin/env python3
"""Test spell slot calculations."""

import json
import os

# Load spell slot data
spell_slot_path = os.path.join(os.path.dirname(__file__), 'resources', 'spell_slots.json')
with open(spell_slot_path, 'r', encoding='utf-8') as f:
    SPELL_SLOT_DATA = json.load(f)

# --- Caster Classification ---
FULL_CASTERS = {'bard', 'cleric', 'druid', 'sorcerer', 'wizard', 'warlock'}
HALF_CASTERS = {'paladin', 'ranger'}
ONE_THIRD_CASTERS = {'eldritch knight', 'arcane trickster'}

def get_caster_type(class_name):
    """Returns 'full', 'half', 'one_third', or None if not a caster."""
    class_lower = class_name.lower()
    if class_lower in FULL_CASTERS:
        return 'full'
    elif class_lower in HALF_CASTERS:
        return 'half'
    elif class_lower in ONE_THIRD_CASTERS:
        return 'one_third'
    return None

def calculate_esl(class_levels):
    """
    Test function to calculate ESL from a dict of {class: level}.
    """
    esl = 0.0
    
    for class_name, level in class_levels.items():
        caster_type = get_caster_type(class_name)
        
        if caster_type == 'full':
            esl += level / 1
        elif caster_type == 'half':
            esl += level / 2
        elif caster_type == 'one_third':
            esl += level / 3
    
    return int(esl)

def get_spell_slots(esl):
    """Get spell slots for a given ESL."""
    progression_table = SPELL_SLOT_DATA['progression_tables']['full_casters']
    
    for entry in progression_table:
        if entry['level'] == esl:
            return entry['slots']
    
    if esl > 12:
        return progression_table[-1]['slots']
    
    return {}

# --- Test Cases ---

print("=== Spell Slot Calculation Tests ===\n")

# Test 1: Single full caster
print("Test 1: Wizard Level 5")
esl = calculate_esl({"Wizard": 5})
slots = get_spell_slots(esl)
print(f"  ESL: {esl} (expected 5)")
print(f"  Spell Slots: {slots}")
print()

# Test 2: Single half caster
print("Test 2: Paladin Level 5")
esl = calculate_esl({"Paladin": 5})
slots = get_spell_slots(esl)
print(f"  ESL: {esl} (expected 2, since 5/2 = 2.5 -> 2)")
print(f"  Spell Slots: {slots}")
print()

# Test 3: Single one-third caster
print("Test 3: Eldritch Knight Level 5")
esl = calculate_esl({"Eldritch Knight": 5})
slots = get_spell_slots(esl)
print(f"  ESL: {esl} (expected 1, since 5/3 = 1.66 -> 1)")
print(f"  Spell Slots: {slots}")
print()

# Test 4: The user's example - multiclass
print("Test 4: Eldritch Knight Level 5 + Arcane Trickster Level 5")
esl = calculate_esl({"Eldritch Knight": 5, "Arcane Trickster": 5})
slots = get_spell_slots(esl)
print(f"  ESL: {esl} (expected 3, since (5/3 + 5/3) = 3.33 -> 3)")
print(f"  Spell Slots: {slots}")
print()

# Test 5: Complex multiclass
print("Test 5: Wizard Level 5 + Paladin Level 4 + Eldritch Knight Level 3")
esl = calculate_esl({"Wizard": 5, "Paladin": 4, "Eldritch Knight": 3})
slots = get_spell_slots(esl)
# Expected: 5/1 + 4/2 + 3/3 = 5 + 2 + 1 = 8
print(f"  ESL: {esl} (expected 8, since 5 + 2 + 1 = 8)")
print(f"  Spell Slots: {slots}")
print()

# Test 6: Multiple half casters
print("Test 6: Paladin Level 6 + Ranger Level 6")
esl = calculate_esl({"Paladin": 6, "Ranger": 6})
slots = get_spell_slots(esl)
# Expected: 6/2 + 6/2 = 3 + 3 = 6
print(f"  ESL: {esl} (expected 6, since 3 + 3 = 6)")
print(f"  Spell Slots: {slots}")
print()

print("=== Tests Complete ===")
