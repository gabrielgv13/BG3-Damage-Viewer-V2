"""UI components package."""

from .damage_ui import (
    DAMAGE_TYPE_COLORS,
    DAMAGE_TYPE_ICON_NAMES,
    DAMAGE_TYPE_TEXTURES,
    hex_to_rgb,
    get_damage_type_color,
    normalize_damage_type,
    get_damage_texture_tag,
    load_damage_type_textures,
    render_damage_breakdown,
    format_damage_components,
)

__all__ = [
    'DAMAGE_TYPE_COLORS',
    'DAMAGE_TYPE_ICON_NAMES',
    'DAMAGE_TYPE_TEXTURES',
    'hex_to_rgb',
    'get_damage_type_color',
    'normalize_damage_type',
    'get_damage_texture_tag',
    'load_damage_type_textures',
    'render_damage_breakdown',
    'format_damage_components',
]