"""Data loader for equipment, weapons, spells, and class features."""

import json
import os
from class_features_loader import ClassFeaturesLoader


class DataLoader:
    """Centralized data loader for all game data."""
    
    def __init__(self, data_path="data", resources_path="resources"):
        self.data_path = data_path
        self.resources_path = resources_path
        
        # Load all data
        self.equipment_data = self._load_equipment()
        self.weapon_data = self._load_weapons()
        self.spell_slot_data = self._load_spell_slots()
        self.features_loader = self._load_class_features()
        
        # Create lookup maps
        self.equipment_map = {item['name']: item for item in self.equipment_data}
        self.weapon_map = {item['name']: item for item in self.weapon_data}
        
    def _load_equipment(self):
        """Load equipment data from JSON."""
        equip_path = os.path.join(self.data_path, 'equipment.json')
        with open(equip_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_weapons(self):
        """Load weapon data from JSON."""
        weapon_path = os.path.join(self.data_path, 'weapons.json')
        with open(weapon_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_spell_slots(self):
        """Load spell slot progression data."""
        spell_slot_path = os.path.join(self.resources_path, 'spell_slots.json')
        with open(spell_slot_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_class_features(self):
        """Load class features using ClassFeaturesLoader."""
        print("[*] Loading class features, feats, and spells...")
        loader = ClassFeaturesLoader(data_path=self.data_path)
        print("[OK] Features loader initialized\n")
        return loader
    
    def get_equipment_by_type(self, equipment_type):
        """Get all equipment of a specific type."""
        return sorted([
            item['name'] for item in self.equipment_data 
            if item['type'] == equipment_type
        ])
    
    def get_equipment_by_types(self, equipment_types):
        """Get all equipment matching any of the specified types."""
        return sorted([
            item['name'] for item in self.equipment_data 
            if item['type'] in equipment_types
        ])
    
    def get_weapons_by_category(self, category_filter):
        """Get weapons matching a filter function."""
        return sorted([
            item['name'] for item in self.weapon_data 
            if category_filter(item)
        ])
