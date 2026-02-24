import json

# Define the missing spells based on wiki data
missing_spells = [
    {
        "name": "Staggering Smite",
        "description": "Possibly Stagger your target. It can't take reactions and is more likely to miss.",
        "school": "Evocation",
        "type": "spell",
        "level": 4,
        "upcastable": False,
        "damage": "Weapon damage + 4d6 Psychic damage (4-24)",
        "buff": "",
        "debuff": "Target must make WIS save or be Staggered for 1 turn (Disadvantage on Attack Rolls, Ability Checks, can't take reactions). Requires Concentration."
    },
    {
        "name": "Grant Flight",
        "description": "Bestow the ability to Fly upon yourself or an ally.",
        "school": "Transmutation",
        "type": "spell",
        "level": 3,
        "upcastable": True,
        "damage": "",
        "buff": "Target gains the ability to fly for 10 turns, moving up to 18m per turn. Requires Concentration. When upcast, affects an additional target per spell slot level above 3rd.",
        "debuff": ""
    },
    {
        "name": "Knock",
        "description": "Unlock an object that is held shut by a mundane lock.",
        "school": "Transmutation",
        "type": "spell",
        "level": 2,
        "upcastable": False,
        "damage": "",
        "buff": "Instantly unlocks any non-magical lock regardless of lockpicking difficulty.",
        "debuff": ""
    },
    {
        "name": "Banishing Smite",
        "description": "Possibly Banish your target to another plane of existence. Targets with 50 Hit Points or more can't be Banished.",
        "school": "Abjuration",
        "type": "spell",
        "level": 5,
        "upcastable": False,
        "damage": "Weapon damage + 5d10 Force damage (5-50)",
        "buff": "",
        "debuff": "If target is left with 1-49 HP after damage, it is Banished for 2 turns (can't be targeted, move, or take actions). Requires Concentration."
    },
    {
        "name": "Flame Strike",
        "description": "Make a pillar of divine fire roar down from the heavens like the wrath of affronted angels.",
        "school": "Evocation",
        "type": "spell",
        "level": 5,
        "upcastable": True,
        "damage": "5d6 Fire + 5d6 Radiant damage (10-60 total). When upcast, deals an additional 1d6 Fire and 1d6 Radiant per spell slot level above 5th.",
        "buff": "",
        "debuff": "Targets that fail DEX save take full damage (half on success)."
    },
    {
        "name": "Heal",
        "description": "Heals a target's wounds and remove Blindness and any diseases.",
        "school": "Evocation",
        "type": "spell",
        "level": 6,
        "upcastable": False,
        "damage": "",
        "buff": "Target regains 70 hit points and is cured of Blindness and diseases. Has no effect on undead or constructs.",
        "debuff": ""
    },
    {
        "name": "Mass Cure Wounds",
        "description": "Unleash a soothing hum of energy that heals you and nearby allies.",
        "school": "Evocation",
        "type": "spell",
        "level": 5,
        "upcastable": True,
        "damage": "",
        "buff": "Heals up to 6 allies for 3d8 hit points. When upcast, heals an extra 1d8 per spell slot level above 5th. Has no effect on undead or constructs.",
        "debuff": ""
    },
    {
        "name": "Wall of Fire",
        "description": "Create a blazing wall of fire, Burning anyone who dares stand too close. Deals Fire to anything that moves into or ends its turn in the area.",
        "school": "Evocation",
        "type": "spell",
        "level": 4,
        "upcastable": True,
        "damage": "5d8 Fire damage (5-40) to creatures within 3m. When upcast, deals an extra 1d8 Fire damage per spell slot level above 4th.",
        "buff": "",
        "debuff": "Creates a 36m line wall of fire for 10 turns. Creatures may be Burned (1d4 Fire damage per turn). Requires Concentration."
    },
    {
        "name": "Wall of Stone",
        "description": "Raise a wall of non-magical, solid stone. The wall is made up of Stone Pillars with 30 HP each, immune to Psychic and vulnerable to Force and Thunder damage.",
        "school": "Evocation",
        "type": "spell",
        "level": 5,
        "upcastable": False,
        "damage": "",
        "buff": "Creates a stone barrier that blocks movement and line of sight. Requires Concentration.",
        "debuff": ""
    },
    {
        "name": "Otiluke's Freezing Sphere",
        "description": "Create a ball of churning ice that can be launched instantly to generate a frosty explosion or stored for later use.",
        "school": "Evocation",
        "type": "spell",
        "level": 6,
        "upcastable": False,
        "damage": "10d6 Cold damage (10-60)",
        "buff": "",
        "debuff": "Targets must make CON save or take full damage."
    },
    {
        "name": "Power Word Kill",
        "description": "Compel an enemy with 100 Hit Points or fewer to die instantly. Limited to one use only.",
        "school": "Enchantment",
        "type": "spell",
        "level": 9,
        "upcastable": False,
        "damage": "Instant death if target has 100 HP or less",
        "buff": "",
        "debuff": "Target with 100 HP or less dies instantly. No saving throw. Can only be learned by Dark Urge after defeating Orin and accepting Bhaal's gift."
    },
    {
        "name": "Booming Blade",
        "description": "Strike with your weapon, afflicting your foe with a resonance that hurts them for 1d8 Thunder when they move. This spell can be cast while Silenced.",
        "school": "Evocation",
        "type": "spell",
        "level": 0,
        "upcastable": False,
        "damage": "Weapon damage + 1d8 Thunder when target moves. At level 5: +1d8 Thunder on hit, +2d8 when target moves. At level 11: +2d8 Thunder on hit, +3d8 when target moves.",
        "buff": "",
        "debuff": "Target takes Thunder damage when it moves on its next turn."
    }
]

# Read the current spells.json
with open('data/spells.json', 'r', encoding='utf-8') as f:
    spells = json.load(f)

print(f"Current spell count: {len(spells)}")
print(f"Adding {len(missing_spells)} new spells...")

# Add missing spells to the list
spells.extend(missing_spells)

# Write back to file
with open('data/spells.json', 'w', encoding='utf-8') as f:
    json.dump(spells, f, indent=4, ensure_ascii=False)

print(f"\nNew spell count: {len(spells)}")
print("\nAdded spells:")
for spell in missing_spells:
    print(f"  - {spell['name']} (Level {spell['level']} {spell['school']})")

print("\n✅ Successfully added all missing spells to spells.json!")
