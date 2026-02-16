#!/usr/bin/env python3
"""Test linear level progression system"""

import sys
import os

# Add workspace to path
sys.path.insert(0, os.path.dirname(__file__))

from class_features_loader import ClassFeaturesLoader

# Initialize loader
loader = ClassFeaturesLoader()

print("[*] Testing Linear Level Progression Logic\n")

# Test 1: Bard progression
print("Test 1: Bard Progression")
print("=" * 50)

bard_subclass_level = loader.get_subclass_level("bard")
print(f"Bard chooses subclass at level: {bard_subclass_level}")
assert bard_subclass_level == 3, f"Expected 3, got {bard_subclass_level}"

# Simulate progression
progression = {
    1: {"should_have_subclass_choice": False},
    2: {"should_have_subclass_choice": False},
    3: {"should_have_subclass_choice": True},
}

for level, expected in progression.items():
    has_choice = loader.has_subclass_choice_at_level("bard", level)
    print(f"  Level {level}: subclass_choice={has_choice} (expected {expected['should_have_subclass_choice']})")
    assert has_choice == expected['should_have_subclass_choice'], f"Bard level {level} mismatch!"

print("[OK] Bard progression is correct\n")

# Test 2: Cleric progression
print("Test 2: Cleric Progression")
print("=" * 50)

cleric_subclass_level = loader.get_subclass_level("cleric")
print(f"Cleric chooses subclass at level: {cleric_subclass_level}")
assert cleric_subclass_level == 1, f"Expected 1, got {cleric_subclass_level}"

# Simulate progression
has_choice_at_1 = loader.has_subclass_choice_at_level("cleric", 1)
has_choice_at_2 = loader.has_subclass_choice_at_level("cleric", 2)
print(f"  Level 1: subclass_choice={has_choice_at_1} (expected True)")
print(f"  Level 2: subclass_choice={has_choice_at_2} (expected False)")
assert has_choice_at_1 == True, "Cleric should have subclass choice at level 1!"
assert has_choice_at_2 == False, "Cleric should NOT have subclass choice at level 2!"

print("[OK] Cleric progression is correct\n")

# Test 3: Paladin progression
print("Test 3: Paladin Progression")
print("=" * 50)

paladin_subclass_level = loader.get_subclass_level("paladin")
print(f"Paladin chooses subclass at level: {paladin_subclass_level}")
assert paladin_subclass_level == 1, f"Expected 1, got {paladin_subclass_level}"

print("[OK] Paladin progression is correct\n")

print("[*] ALL TESTS PASSED!")
print("\nLinear Progression System:")
print("  1. User selects class (e.g., Bard)")
print("  2. User clicks 'Add Level' to go 1 → level 1")
print("  3. User clicks 'Add Level' to go 2 → level 2")
print("  4. User clicks 'Add Level' to try to go to level 3")
print("     - System detects subclass choice needed at level 3")
print("     - Shows subclass selector")
print("     - User selects subclass (e.g., College of Lore)")
print("     - Level 3 is granted with subclass features")
print("  5. User can continue clicking 'Add Level' for levels 4-12")
