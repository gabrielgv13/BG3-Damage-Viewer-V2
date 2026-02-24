# BG3 Damage Analyser - Modular Refactoring

## Overview

The BG3 Damage Analyser codebase has been restructured into a modular architecture, separating concerns into distinct packages for better maintainability and organization.

## New Directory Structure

```
BG3-Damage-Analyser/
├── models/              # Game logic and calculations
│   ├── __init__.py
│   ├── character.py               # Character state management
│   ├── spell_slots.py             # Spell slot calculations
│   ├── damage_calculator.py       # Damage calculations and breakdowns
│   └── armor_calculator.py        # Armor class calculations
├── loaders/             # Data loading
│   ├── __init__.py
│   └── data_loader.py             # Equipment, weapons, spells data loading
├── utils/               # Helper utilities
│   ├── __init__.py
│   ├── ability_calculator.py      # Ability score and point buy calculations
│   ├── equipment_categorizer.py   # Equipment/weapon categorization
│   └── weapon_parser.py           # Weapon parsing utilities
├── ui/                  # UI rendering
│   ├── __init__.py
│   └── damage_ui.py               # Damage breakdown rendering
├── main.py              # Main application entry point (TO BE REFACTORED)
├── class_features_loader.py       # Class features loader
└── data/                # JSON data files
    ├── equipment.json
    ├── weapons.json
    ├── spells.json
    ├── feats.json
    └── classes/
```

## Module Descriptions

### `models/` - Game Logic Models

#### `character.py` - Character Class
Manages character state including levels, subclasses, and ability scores.

**Key Features:**
- Track levels in multiple classes (multiclassing support)
- Manage subclass selections
- Store ability scores
- Calculate total level (max 12)
- Get class breakdown for display

**Usage:**
```python
from models import Character

char = Character()
char.add_level("wizard", 5)
char.set_subclass("wizard", "abjuration_school")
char.ability_scores["Intelligence"] = 16

total_level = char.get_total_level()  # Returns 5
breakdown = char.get_class_breakdown()  # Returns {"wizard": 5}
```

#### `spell_slots.py` - SpellSlotCalculator
Calculates spell slots based on caster levels and Effective Spell Level (ESL).

**Key Features:**
- Identify caster types (full, half, one-third)
- Calculate ESL for multiclass characters
- Get spell slots by level (1-6)
- Support for warlock, sorcerer, wizard (full), paladin, ranger (half), eldritch knight, arcane trickster (one-third)

**Usage:**
```python
from models import SpellSlotCalculator

calculator = SpellSlotCalculator(spell_slot_data)
esl = calculator.calculate_effective_spell_level(
    {"wizard": 5, "paladin": 2},
    {"wizard": "abjuration_school"}
)
# ESL = 5 (full) + 1 (half) = 6

slots = calculator.get_all_spell_slots(esl)
# Returns {1: 4, 2: 3, 3: 3, 4: 1, 5: 0, 6: 0}
```

#### `damage_calculator.py` - DamageCalculator
Handles weapon damage calculations and damage component parsing.

**Key Features:**
- Calculate damage ranges (min, max, avg, crit min/max/avg)
- Parse weapon damage from effects strings
- Extract base weapon components
- Parse additional damage (enchantments, equipment bonuses)
- Get equipment damage bonuses

**Usage:**
```python
from models import DamageCalculator

calc = DamageCalculator(equipment_data, weapons_data)

# Calculate damage range
min_dmg, max_dmg, avg_dmg, crit_min, crit_max, crit_avg = calc.calculate_damage_range("2d6", 5)
# Normal: 7-17 (avg 12), Crit: 9-29 (avg 19)

# Parse weapon damage
dice, enchant = calc.parse_weapon_damage(weapon_item, '1h')

# Get equipment bonuses
flat_bonus, components = calc.get_equipment_damage_components(
    ["Gloves of Power", "Ring of Flinging"],
    is_unarmed=False
)
```

#### `armor_calculator.py` - ArmorCalculator
Calculates armor class from equipped items.

**Key Features:**
- Calculate base AC from armor
- Apply dexterity modifier with caps (light/medium/heavy armor)
- Add shield bonuses
- Add miscellaneous AC bonuses (Bracers of Defence, etc.)
- Format AC breakdown for display

**Usage:**
```python
from models import ArmorCalculator

calc = ArmorCalculator(equipment_data, weapons_data, shields_list)

ac_data = calc.calculate_ac(
    dex_mod=2,
    equipped_items={"slot_armor": "Chain Mail", "slot_ring1": "Ring of Protection"},
    armor_name="Chain Mail",
    offhand_name="Shield"
)
# Returns: {'base_ac': 16, 'effective_dex': 0, 'bonus_ac': 2, 'final_ac': 18}

breakdown = calc.get_ac_breakdown(ac_data)
# "Armor Class: 18 (Base 16 + Dex 0 + Bonus 2)"
```

### `loaders/` - Data Loading

#### `data_loader.py` - DataLoader
Centralized data loading for equipment, weapons, spells, and class features.

**Key Features:**
- Load all JSON data files
- Filter equipment by type
- Filter weapons by category
- Get spell slot progression data

**Usage:**
```python
from loaders import DataLoader

loader = DataLoader()

# Get all helmets
helmets = loader.get_equipment_by_type("Helmet")

# Get all armor and clothing
armor = loader.get_equipment_by_types(["Light Armour", "Medium Armour", "Heavy Armour"])

# Get melee weapons
melee_weapons = loader.get_weapons_by_category(lambda w: "melee" in w.get("type", "").lower())
```

### `utils/` - Utilities

#### `ability_calculator.py` - AbilityScoreCalculator
Point buy system for ability scores.

**Key Features:**
- Calculate ability modifiers
- Calculate point buy costs
- Validate point buy (27 points total)
- Calculate final scores with racial bonuses
- Format modifiers with signs

**Usage:**
```python
from utils import AbilityScoreCalculator

# Calculate modifier
mod = AbilityScoreCalculator.calculate_modifier(16)  # Returns +3

# Check point buy
base_scores = {"Strength": 15, "Dexterity": 14, "Constitution": 13, ...}
is_valid = AbilityScoreCalculator.is_valid_point_buy(base_scores)

# Add racial bonuses
racial_bonuses = {"Strength": 2, "Constitution": 1}
final_scores = AbilityScoreCalculator.calculate_final_scores(base_scores, racial_bonuses)
```

#### `equipment_categorizer.py` - EquipmentCategorizer
Categorizes equipment and weapons into lists.

**Key Features:**
- Categorize equipment by type (helmets, armor, boots, gloves, rings, etc.)
- Categorize weapons by handedness and melee/ranged
- Check if weapon is strictly two-handed

**Usage:**
```python
from utils import EquipmentCategorizer

categorizer = EquipmentCategorizer(equipment_data, weapons_data)

categories = categorizer.get_all_categories()
# Returns dict with: helmets, armor_clothing, melee_1h, melee_2h, ranged_1h, ranged_2h, etc.

is_2h = categorizer.is_strictly_two_handed("Greatsword", is_ranged=False)  # True
is_2h = categorizer.is_strictly_two_handed("Longsword", is_ranged=False)  # False (versatile)
```

#### `weapon_parser.py` - Weapon Parsing Utilities
Utility functions for parsing weapon data.

**Key Features:**
- Get weapon handedness
- Parse dice strings
- Parse damage values
- Extract handedness segments
- Categorize weapons

**Usage:**
```python
from utils import parse_dice_string, parse_damage_value

count, sides = parse_dice_string("2d6")  # Returns (2, 6)

dice_data = parse_damage_value("1d8 + 2")
# Returns {'dice': (1, 8), 'bonus': 2, 'fixed': None, 'type': 'dice'}
```

### `ui/` - UI Components

#### `damage_ui.py` - Damage UI Rendering
Render damage breakdowns with colored damage types and icons.

**Key Features:**
- Damage type color mappings
- Load damage type icon textures
- Render damage breakdown components
- Format damage components as text
- Normalize damage type names

**Usage:**
```python
from ui import render_damage_breakdown, load_damage_type_textures

# Load textures once at startup
load_damage_type_textures()

# Render damage breakdown
components = [
    {"type": "Slashing", "dice_count": 1, "dice_sides": 8, "flat": 3, "source": "Longsword"},
    {"type": "Fire", "dice_count": 1, "dice_sides": 6, "flat": 0, "source": "Weapon enchantment"},
]
render_damage_breakdown("breakdown_tag", components)
```

## Migration Guide

### Next Steps for Refactoring

The main.py file still contains:
1. UI construction code (window, widgets)
2. Callback functions
3. Global state variables
4. Application initialization

**Recommended approach:**
1. Extract UI construction into separate files in `ui/`:
   - `ui/ability_ui.py` - Ability score UI
   - `ui/class_ui.py` - Class selection and level UI
   - `ui/equipment_ui.py` - Equipment slots UI
   - `ui/stats_ui.py` - Stats display UI

2. Create a controller/manager class to handle callbacks and coordinate between UI and models

3. Reduce main.py to:
   - Import all modules
   - Initialize DearPyGUI
   - Create controller
   - Build UI
   - Run main loop

### Example Future main.py Structure

```python
import dearpygui.dearpygui as dpg
from loaders import DataLoader
from models import Character, SpellSlotCalculator, DamageCalculator, ArmorCalculator
from utils import EquipmentCategorizer
from ui import load_damage_type_textures

# Initialize data
loader = DataLoader()
categorizer = EquipmentCategorizer(loader.equipment, loader.weapons)

# Initialize calculators
character = Character()
spell_calc = SpellSlotCalculator(loader.spell_slots)
damage_calc = DamageCalculator(loader.equipment, loader.weapons)
armor_calc = ArmorCalculator(loader.equipment, loader.weapons, categorizer.shields)

# Initialize DearPyGUI
dpg.create_context()
load_damage_type_textures()

# Build UI (from ui modules)
# ... UI construction ...

# Start application
dpg.create_viewport(title="BG3 Damage Analyser", width=1200, height=800)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
```

## Benefits

1. **Separation of Concerns**: Each module has a clear, single responsibility
2. **Testability**: Modules can be tested independently
3. **Reusability**: Models and utilities can be used in other projects
4. **Maintainability**: Easier to find and modify specific functionality
5. **Readability**: Smaller, focused files are easier to understand
6. **Extensibility**: New features can be added without touching unrelated code

## Testing

Each module can be tested independently:

```python
# Test spell slot calculator
from models import SpellSlotCalculator
import json

with open('data/spell_slots.json') as f:
    slot_data = json.load(f)

calc = SpellSlotCalculator(slot_data)
assert calc.calculate_effective_spell_level({"wizard": 5}, {}) == 5
assert calc.get_spell_slots_for_level(5, 3) == 2  # Level 5 wizard has 2 level 3 slots
```

## Notes

- All modules preserve the original functionality from main.py
- The existing main.py still works but should be refactored to use these modules
- Data files remain unchanged
- class_features_loader.py remains as-is for now
