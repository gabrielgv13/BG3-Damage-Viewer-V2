"""UI rendering utilities for damage breakdowns and other components."""
import os
import dearpygui.dearpygui as dpg


# Damage type color mappings
DAMAGE_TYPE_COLORS = {
    "slashing": "#C8C8C8",
    "bludgeoning": "#C8C8C8",
    "piercing": "#C8C8C8",
    "cold": "#77C4DE",
    "acid": "#D0DE15",
    "necrotic": "#84C69E",
    "poison": "#91A049",
    "psychic": "#B56BA4",
    "radiant": "#F2D57D",
    "force": "#D36B6C",
    "thunder": "#8266A6",
    "lightning": "#5F93DD",
    "fire": "#DD5F5F",
}

DAMAGE_TYPE_ICON_NAMES = {
    "acid": "Acid.png",
    "bludgeoning": "Bludgeoning.png",
    "cold": "Cold.png",
    "fire": "Fire.png",
    "force": "Force.png",
    "lightning": "Lightning.png",
    "necrotic": "Necrotic.png",
    "piercing": "Piercing.png",
    "poison": "Poison.png",
    "psychic": "Psychic.png",
    "radiant": "Radiant.png",
    "slashing": "Slashing.png",
    "thunder": "Thunder.png",
}

# Global texture registry
DAMAGE_TYPE_TEXTURES = {}


def hex_to_rgb(hex_str):
    """Convert hex color to RGB list."""
    hex_str = hex_str.lstrip("#")
    return [int(hex_str[i:i + 2], 16) for i in (0, 2, 4)]


def get_damage_type_color(damage_type):
    """Get color for a damage type."""
    return DAMAGE_TYPE_COLORS.get(damage_type.lower(), "#FFFFFF")


def normalize_damage_type(damage_type):
    """Normalize damage type string."""
    if not damage_type:
        return "Unspecified"
    return damage_type.strip().capitalize()


def get_damage_texture_tag(damage_type):
    """Get texture tag for a damage type icon."""
    return DAMAGE_TYPE_TEXTURES.get(damage_type.lower())


def load_damage_type_textures():
    """Load damage type icon textures from files."""
    icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "damage_types")
    
    if not os.path.isdir(icon_dir):
        return
    
    for dmg_key, filename in DAMAGE_TYPE_ICON_NAMES.items():
        file_path = os.path.join(icon_dir, filename)
        if not os.path.isfile(file_path):
            continue
        
        width, height, channels, data = dpg.load_image(file_path)
        texture_tag = f"tex_damage_{dmg_key}"
        
        if not dpg.does_item_exist(texture_tag):
            dpg.add_static_texture(width, height, data, tag=texture_tag)
        
        DAMAGE_TYPE_TEXTURES[dmg_key] = texture_tag


def render_damage_breakdown(parent_tag, components):
    """
    Render damage breakdown components in a DearPyGUI parent.
    
    Args:
        parent_tag: DPG tag of parent item
        components: List of damage component dicts with keys:
                   type, dice_count, dice_sides, flat, source
    """
    if not dpg.does_item_exist(parent_tag):
        return
    
    # Clear existing children
    dpg.delete_item(parent_tag, children_only=True)
    
    if not components:
        dpg.add_text("(no damage breakdown)", 
                    parent=parent_tag, 
                    color=[180, 180, 180])
        return
    
    for comp in components:
        dmg_type_raw = comp["type"]
        dmg_type = normalize_damage_type(dmg_type_raw)
        color = hex_to_rgb(get_damage_type_color(dmg_type_raw))
        texture_tag = get_damage_texture_tag(dmg_type_raw)
        
        count = comp["dice_count"]
        sides = comp["dice_sides"]
        flat = comp["flat"]
        source = comp["source"]
        
        # Build detail string
        if count > 0:
            d_min = count
            d_max = count * sides
            d_avg = (count * (sides + 1)) / 2
            detail = f"{count}d{sides} -> {d_min}-{d_max} (Avg {d_avg:.1f})"
            if flat:
                sign = "+" if flat > 0 else ""
                detail += f" {sign}{flat} flat"
        else:
            sign = "+" if flat >= 0 else ""
            detail = f"{sign}{flat} flat"
        
        # Render component
        with dpg.group(horizontal=True, parent=parent_tag):
            if texture_tag:
                dpg.add_image(texture_tag, width=16, height=16)
            dpg.add_text(dmg_type, color=color)
            dpg.add_text(f"({source}): {detail}")


def format_damage_components(components):
    """
    Format damage components as text lines.
    
    Args:
        components: List of damage component dicts
    
    Returns:
        List of formatted strings
    """
    lines = []
    
    for comp in components:
        dmg_type = comp["type"]
        source = comp["source"]
        count = comp["dice_count"]
        sides = comp["dice_sides"]
        flat = comp["flat"]
        
        if count > 0:
            d_min = count
            d_max = count * sides
            d_avg = (count * (sides + 1)) / 2
            line = f"{dmg_type} ({source}): {count}d{sides} -> {d_min}-{d_max} (Avg {d_avg:.1f})"
            if flat:
                sign = "+" if flat > 0 else ""
                line += f" {sign}{flat} flat"
        else:
            sign = "+" if flat >= 0 else ""
            line = f"{dmg_type} ({source}): {sign}{flat} flat"
        
        lines.append(line)
    
    return lines
