"""
Class Features Loader
=====================
Loads extracted class, subclass, feat, and spell data from JSON files.
Integrates with the character level system to provide features at each level.

Data structure:
- classes/{classname}.json
  {
    "name": "Bard",
    "subclassLevel": 3,
    "subclasses": ["college_of_lore", "college_of_valour", ...],
    "levels": {
      "1": [ { "name": "Bardic Inspiration", "type": "feature" }, ... ],
      "3": [ { "name": "Choose Bard Subclass", "type": "subclassSelection", ... }, ... ]
    }
  }
- classes/subclasses/{classname}_{subclassname}.json
- feats.json
- spells.json
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ClassFeaturesLoader:
    """Loads and manages class features, subclasses, feats, and spells."""
    
    def __init__(self, data_path: str = "data"):
        """Initialize loader with path to data directory."""
        self.data_path = Path(data_path)
        self.classes = {}  # Loaded class data
        self.subclasses = {}  # Loaded subclass data
        self.feats = []
        self.spells = []
        self.class_subclass_levels = {}  # {class_name: level_number}
        
        self._load_all_data()
    
    def _load_all_data(self) -> None:
        """Load all class, subclass, feat, and spell data."""
        self._load_classes()
        self._load_subclasses()
        self._load_feats()
        self._load_spells()
    
    def _load_classes(self) -> None:
        """Load all class JSON files."""
        classes_dir = self.data_path / "classes"
        
        if not classes_dir.exists():
            print(f"[!] Classes directory not found at {classes_dir}")
            return
        
        # Load all .json files in classes directory (not subdirectories)
        for class_file in classes_dir.glob("*.json"):
            try:
                with open(class_file, 'r', encoding='utf-8') as f:
                    class_data = json.load(f)
                
                class_name = class_file.stem  # filename without .json
                self.classes[class_name] = class_data
                
                # Track subclass selection level
                if "subclassLevel" in class_data:
                    self.class_subclass_levels[class_name] = class_data["subclassLevel"]
                
                print(f"[OK] Loaded class: {class_name}")
            except Exception as e:
                print(f"[!] Error loading {class_file}: {e}")
    
    def _load_subclasses(self) -> None:
        """Load all subclass JSON files."""
        subclasses_dir = self.data_path / "classes" / "subclasses"
        
        if not subclasses_dir.exists():
            print(f"[!] Subclasses directory not found at {subclasses_dir}")
            return
        
        for subclass_file in subclasses_dir.glob("*.json"):
            try:
                with open(subclass_file, 'r', encoding='utf-8') as f:
                    subclass_data = json.load(f)
                
                subclass_name = subclass_file.stem
                self.subclasses[subclass_name] = subclass_data
            except Exception as e:
                print(f"[!] Error loading {subclass_file}: {e}")
        
        print(f"[OK] Loaded {len(self.subclasses)} subclasses")
    
    def _load_feats(self) -> None:
        """Load feats.json."""
        feats_file = self.data_path / "feats.json"
        
        if not feats_file.exists():
            print(f"[!] Feats file not found at {feats_file}")
            return
        
        try:
            with open(feats_file, 'r', encoding='utf-8') as f:
                self.feats = json.load(f)
            print(f"[OK] Loaded {len(self.feats)} feats")
        except Exception as e:
            print(f"[!] Error loading feats: {e}")
    
    def _load_spells(self) -> None:
        """Load spells.json."""
        spells_file = self.data_path / "spells.json"
        
        if not spells_file.exists():
            print(f"[!] Spells file not found at {spells_file}")
            return
        
        try:
            with open(spells_file, 'r', encoding='utf-8') as f:
                self.spells = json.load(f)
            print(f"[OK] Loaded {len(self.spells)} spells")
        except Exception as e:
            print(f"[!] Error loading spells: {e}")
    
    def get_class_data(self, class_name: str) -> Optional[Dict]:
        """Get full data for a class."""
        class_key = class_name.lower()
        return self.classes.get(class_key)
    
    def get_subclass_level(self, class_name: str) -> Optional[int]:
        """Get the level at which a class chooses its subclass (e.g., Bard at level 3)."""
        class_key = class_name.lower()
        return self.class_subclass_levels.get(class_key)
    
    def get_subclass_options(self, class_name: str) -> List[str]:
        """Get available subclasses for a class."""
        class_data = self.get_class_data(class_name)
        if class_data and "subclasses" in class_data:
            return class_data["subclasses"]
        return []
    
    def get_subclass_data(self, class_name: str, subclass_name: str) -> Optional[Dict]:
        """Get full data for a specific subclass."""
        # Subclass keys are formatted as: {classname}_{subclassname}
        subclass_key = f"{class_name.lower()}_{subclass_name.lower()}"
        return self.subclasses.get(subclass_key)
    
    def get_features_at_level(self, class_name: str, level: int) -> List[Dict]:
        """Get all features for a class at a specific level."""
        class_data = self.get_class_data(class_name)
        if not class_data:
            return []
        
        levels = class_data.get("levels", {})
        return levels.get(str(level), [])
    
    def get_subclass_features_at_level(self, class_name: str, subclass_name: str, level: int) -> List[Dict]:
        """Get features for a subclass at a specific level."""
        subclass_data = self.get_subclass_data(class_name, subclass_name)
        if not subclass_data:
            return []
        
        levels = subclass_data.get("levels", {})
        return levels.get(str(level), [])
    
    def has_subclass_choice_at_level(self, class_name: str, level: int) -> bool:
        """Check if a class has a subclass choice at a specific level."""
        features = self.get_features_at_level(class_name, level)
        return any(f.get("type") == "subclassSelection" for f in features)
    
    def get_all_features_for_level_range(
        self, 
        class_name: str, 
        start_level: int, 
        end_level: int,
        subclass_name: Optional[str] = None
    ) -> Dict[int, List[Dict]]:
        """
        Get all features for a class in a level range, optionally including subclass features.
        
        Args:
            class_name: Name of the class
            start_level: Starting level (inclusive)
            end_level: Ending level (inclusive)
            subclass_name: Optional subclass to include features from
            
        Returns:
            Dict with level as key and list of features as value
        """
        features_by_level = {}
        
        for level in range(start_level, end_level + 1):
            features = self.get_features_at_level(class_name, level)
            
            # Add subclass features if provided
            if subclass_name:
                subclass_features = self.get_subclass_features_at_level(class_name, subclass_name, level)
                features = features + subclass_features
            
            if features:
                features_by_level[level] = features
        
        return features_by_level
    
    def build_character_feature_summary(
        self,
        classes_dict: Dict[str, int],  # {"Bard": 5, "Rogue": 3}
        subclasses_dict: Optional[Dict[str, str]] = None  # {"Bard": "college_of_lore"}
    ) -> Dict[str, any]:
        """
        Build a comprehensive feature summary for a multiclass character.
        
        Args:
            classes_dict: Dictionary of class name to level
            subclasses_dict: Dictionary of class name to subclass name
            
        Returns:
            Dict with features organized by level showing what character gains at each level
        """
        if subclasses_dict is None:
            subclasses_dict = {}
        
        all_features = {}  # {level: [features]}
        
        # Collect features from each class
        for class_name, class_level in sorted(classes_dict.items()):
            subclass_name = subclasses_dict.get(class_name)
            
            for level in range(1, class_level + 1):
                if level not in all_features:
                    all_features[level] = []
                
                # Get class features
                class_features = self.get_features_at_level(class_name, level)
                for feature in class_features:
                    feature_copy = feature.copy()
                    feature_copy["source"] = f"{class_name} (Level {level})"
                    all_features[level].append(feature_copy)
                
                # Get subclass features
                if subclass_name:
                    subclass_features = self.get_subclass_features_at_level(class_name, subclass_name, level)
                    for feature in subclass_features:
                        feature_copy = feature.copy()
                        feature_copy["source"] = f"{class_name} - {subclass_name.title()} (Level {level})"
                        all_features[level].append(feature_copy)
        
        return all_features
    
    def get_feat_by_name(self, feat_name: str) -> Optional[Dict]:
        """Get a specific feat by name."""
        for feat in self.feats:
            if feat.get("name", "").lower() == feat_name.lower():
                return feat
        return None
    
    def get_spell_by_name(self, spell_name: str) -> Optional[Dict]:
        """Get a specific spell by name."""
        for spell in self.spells:
            if spell.get("name", "").lower() == spell_name.lower():
                return spell
        return None
    
    def get_available_classes(self) -> List[str]:
        """Get list of all available classes."""
        return sorted(list(self.classes.keys()))
    
    def format_feature_display(self, feature: Dict, indent: str = "") -> str:
        """Format a feature for display."""
        lines = []
        
        name = feature.get("name", "Unknown")
        feature_type = feature.get("type", "feature")
        
        if feature_type == "subclassSelection":
            lines.append(f"{indent}🎭 {name}")
            lines.append(f"{indent}   → {feature.get('description', 'Choose your subclass')}")
        else:
            lines.append(f"{indent}⭐ {name}")
        
        return "\n".join(lines)
    
    def print_class_progression(self, class_name: str, subclass_name: Optional[str] = None) -> None:
        """Print a formatted progression of a class through all levels."""
        class_data = self.get_class_data(class_name)
        if not class_data:
            print(f"Class {class_name} not found")
            return
        
        print(f"\n{'='*60}")
        print(f"{class_name.upper()} CLASS PROGRESSION")
        if subclass_name:
            print(f"Subclass: {subclass_name.upper()}")
        print(f"{'='*60}\n")
        
        for level in range(1, 13):
            features = self.get_features_at_level(class_name, level)
            subclass_features = []
            
            if subclass_name:
                subclass_features = self.get_subclass_features_at_level(class_name, subclass_name, level)
            
            if features or subclass_features:
                print(f"LEVEL {level}:")
                for feature in features:
                    print(f"  • {feature.get('name', 'Unknown Feature')}")
                for feature in subclass_features:
                    print(f"  • {feature.get('name', 'Unknown Feature')} (Subclass)")
                print()


if __name__ == "__main__":
    # Test the loader
    print("[*] Testing ClassFeaturesLoader...\n")
    
    loader = ClassFeaturesLoader()
    
    print(f"\n[OK] Available classes: {', '.join(loader.get_available_classes())}\n")
    
    # Example: Show Bard progression
    bard_level = loader.get_subclass_level("bard")
    print(f"[->] Bard chooses subclass at level: {bard_level}")
    print(f"[->] Bard subclass options: {loader.get_subclass_options('bard')}\n")
    
    loader.print_class_progression("paladin")
    loader.print_class_progression("bard", "college_of_lore")
