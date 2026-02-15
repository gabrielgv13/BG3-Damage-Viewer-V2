# BG3 Damage Analyzer

A comprehensive Baldur's Gate 3 damage calculator and character build analyzer built with Python and DearPyGUI.

## Current Features

### Character Building
- **Multi-Class System**: Support for up to 12 total character levels across multiple classes
- **Ability Score Management**: Point-buy system (27 points, base 8-15) with racial bonuses (+2, +1)
- **Ability Modifiers**: Automatic calculation of ability modifiers and their effects

### Equipment System
- **Comprehensive Equipment Database**: 10+ equipment slots (Helmet, Armor, Cape, Gloves, Boots, Amulet, 2 Rings, Weapon slots)
- **Equipment Data**: Detailed JSON database with equipment and weapon effects
- **Equipment Effects**: Conditional bonuses (e.g., Bracers of Defence only work when unarmored without shield)

### Damage Calculations
- **Weapon Damage**: Full dice roll calculations (1d8, 2d6, etc.) with min/max/average ranges
- **Critical Hits**: Complete critical hit damage calculations (double dice, same modifiers)
- **Versatile Weapons**: Automatic 1-handed vs 2-handed damage calculation based on off-hand status
- **Weapon Handedness**: Proper detection and handling of 1H, 2H, and versatile weapons
- **Finesse Support**: Automatic selection of best modifier (STR vs DEX) for finesse weapons
- **Special Weapons**: Support for unique weapon mechanics (e.g., Titanstring Bow adds STR to ranged damage)
- **Enchantment Bonuses**: Weapon enchantment modifiers properly applied
- **Equipment Bonuses**: Additional damage from equipped items integrated into calculations
- **Multiple Damage Types**: Tracking and display of different damage types (slashing, fire, cold, etc.)

### Armor Class (AC) Calculations
- **Base AC from Armor**: Proper AC values for all armor types
- **Dexterity Modifiers**: Correctly capped based on armor type (Heavy: 0, Medium: +2, Light: unlimited)
- **Shield Bonuses**: AC bonus from equipped shields
- **Equipment Bonuses**: Additional AC from items like rings and amulets
- **Armor Type Detection**: Automatic handling of Light, Medium, Heavy armor, and Clothing

### Visual Features
- **Damage Type Icons**: Visual representation of different damage types
- **Color-Coded Display**: Damage types shown in appropriate colors
- **Damage Breakdown**: Detailed breakdown showing each damage component's source and contribution
- **Split View Interface**: Equipment selection on left, real-time statistics on right

### Weapon Categories
- **Melee Weapons**: 1-handed and 2-handed melee weapons
- **Ranged Weapons**: Bows, crossbows (including hand crossbows)
- **Unarmed Combat**: Support for unarmed strikes with equipment bonuses

## What's Not Implemented Yet

### Character Features
- Feats system
- Racial abilities and bonuses
- Class features and abilities
- Subclass features
- Background selection and bonuses

### Combat Calculations
- Spell damage calculations
- Class action damage (e.g., Divine Smite, Sneak Attack)
- Weapon maneuvers
- Attack roll bonuses and calculations
- Saving throw DCs
- Action economy tracking

### Other Features
- Character import/export
- Build sharing via URL
- Equipment comparison tool
- Build optimization suggestions

## Future Development

We are exploring integration with [crpggames/bg3planner](https://github.com/crpggames/bg3planner), an open-source Angular-based character planner that has comprehensive class, subclass, feat, and spell systems. Their project provides the character building foundation we lack, while we have the equipment database and damage calculation systems they're missing. A potential fork and integration could result in a complete, open-source BG3 build planner with full damage calculations.

## Data Sources

The equipment and weapon database was structured using the BG3 Item Index Cheat Sheet by Cayxx on r/BaldursGate3:
https://www.reddit.com/r/BaldursGate3/comments/16acy9l/bg3_cheat_sheet_for_items_in_each_act_spoilers/

## Dependencies

- Python 3.x
- dearpygui

## Installation

```bash
pip install dearpygui
```

## Running the Application

```bash
python main.py
```

## License

This project is provided as-is for the Baldur's Gate 3 community.
