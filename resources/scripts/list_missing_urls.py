import json

# List of missing spells to fetch
missing_spells = [
    "Staggering Smite",
    "Grant Flight", 
    "Knock",
    "Banishing Smite",
    "Flame Strike",
    "Heal",
    "Mass Cure Wounds",
    "Wall of Fire",
    "Wall of Stone",
    "Otiluke's Freezing Sphere",
    "Power Word Kill",
    "Booming Blade",
    # Skipping special/ritual spells like:
    # "Bhaal's Power Word Kill Ritual", "Curriculum of Strategy: Artistry of War",
    # "Divine Revelry", "Formsculpt: Tressym", "Karsus' Compulsion",
    # "Power Word: Ruin", "Sights of the Seelie: Summon Deva", "Bursting Sinew"
]

# Generate wiki URLs
print("Missing spells to fetch from BG3 wiki:\n")
print("=" * 60)
for spell in missing_spells:
    url_name = spell.replace(" ", "_").replace("'", "%27")
    url = f"https://bg3.wiki/wiki/{url_name}"
    print(f"{spell}: {url}")

print("\n" + "=" * 60)
print(f"\nTotal spells to fetch: {len(missing_spells)}")
