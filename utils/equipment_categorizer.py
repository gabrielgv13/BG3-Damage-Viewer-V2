"""Equipment categorization utilities."""


class EquipmentCategorizer:
    """Categorizes equipment and weapons into different types."""
    
    def __init__(self, equipment_data, weapons_data):
        """Initialize with equipment and weapon data."""
        self.equip_data = equipment_data
        self.weap_data = weapons_data
        
        # Generate categorized lists
        self.helmets = []
        self.armor_clothing = []
        self.boots = []
        self.capes = []
        self.gloves = []
        self.amulets = []
        self.rings = []
        self.shields = []
        
        self.melee_1h = []
        self.melee_2h = []
        self.ranged_1h = []
        self.ranged_2h = []
        
        self._categorize_equipment()
        self._categorize_weapons()
    
    def _categorize_equipment(self):
        """Categorize equipment items by type."""
        for item in self.equip_data:
            item_type = item.get('type', '')
            name = item.get('name', '')
            
            if item_type == 'Helmet':
                self.helmets.append(name)
            elif item_type in ['Medium Armour', 'Heavy Armour', 'Light Armour', 'Clothing']:
                self.armor_clothing.append(name)
            elif item_type == 'Boots':
                self.boots.append(name)
            elif item_type in ['Cape', 'Cloak']:
                self.capes.append(name)
            elif item_type == 'Gloves':
                self.gloves.append(name)
            elif item_type == 'Amulet':
                self.amulets.append(name)
            elif item_type == 'Ring':
                self.rings.append(name)
            elif item_type == 'Shield':
                self.shields.append(name)
        
        # Sort all lists
        self.helmets.sort()
        self.armor_clothing.sort()
        self.boots.sort()
        self.capes.sort()
        self.gloves.sort()
        self.amulets.sort()
        self.rings.sort()
        self.shields.sort()
    
    def _get_weapon_modes(self, weapon_item):
        """
        Determine handedness and melee/ranged classification.
        Returns: set of modes ('1h', '2h', 'melee', 'ranged')
        """
        effects_str = " ".join(weapon_item.get('effects', [])).lower()
        w_type = weapon_item.get('type', '').lower()
        
        modes = set()
        
        # Check for handedness in effects
        if '1h ' in effects_str or (effects_str.startswith('1h') and len(effects_str) >= 2):
            modes.add('1h')
        if '2h ' in effects_str or (effects_str.startswith('2h') and len(effects_str) >= 2):
            modes.add('2h')
        
        # Classify as melee or ranged based on type
        is_ranged = 'bow' in w_type or 'crossbow' in w_type
        
        if is_ranged:
            modes.add('ranged')
        else:
            modes.add('melee')
        
        return modes
    
    def _categorize_weapons(self):
        """Categorize weapons by handedness and type."""
        for weapon in self.weap_data:
            name = weapon.get('name', '')
            modes = self._get_weapon_modes(weapon)
            
            if 'melee' in modes:
                if '1h' in modes:
                    self.melee_1h.append(name)
                if '2h' in modes:
                    self.melee_2h.append(name)
            elif 'ranged' in modes:
                if '1h' in modes:
                    self.ranged_1h.append(name)
                if '2h' in modes:
                    self.ranged_2h.append(name)
                
                # Fallback logic for ranged weapons
                w_type = weapon.get('type', '').lower()
                if 'hand crossbow' in w_type:
                    if name not in self.ranged_1h:
                        self.ranged_1h.append(name)
                elif 'bow' in w_type or 'crossbow' in w_type:
                    if name not in self.ranged_2h:
                        self.ranged_2h.append(name)
        
        # Sort all weapon lists
        self.melee_1h.sort()
        self.melee_2h.sort()
        self.ranged_1h.sort()
        self.ranged_2h.sort()
    
    def is_strictly_two_handed(self, weapon_name, is_ranged=False):
        """Check if a weapon is strictly 2-handed (not versatile)."""
        if is_ranged:
            return weapon_name in self.ranged_2h and weapon_name not in self.ranged_1h
        else:
            return weapon_name in self.melee_2h and weapon_name not in self.melee_1h
    
    def get_all_categories(self):
        """Return dict of all categorized equipment and weapon lists."""
        return {
            'helmets': self.helmets,
            'armor_clothing': self.armor_clothing,
            'boots': self.boots,
            'capes': self.capes,
            'gloves': self.gloves,
            'amulets': self.amulets,
            'rings': self.rings,
            'shields': self.shields,
            'melee_1h': self.melee_1h,
            'melee_2h': self.melee_2h,
            'ranged_1h': self.ranged_1h,
            'ranged_2h': self.ranged_2h,
        }
