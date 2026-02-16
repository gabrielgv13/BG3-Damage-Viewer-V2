#!/usr/bin/env python3
"""
Extract classes, subclasses, feats, and spells from crpggames/bg3planner TypeScript files
and generate structured JSON organized by level.

This script parses the TS files and creates:
- classes/{classname}.json with level-by-level features and subclass selection
- classes/subclasses/{classname}_{subclassname}.json for each subclass
- feats.json with all feat definitions
- spells.json with all spell definitions
"""

import json
import re
import os
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional

class BG3DataExtractor:
    def __init__(self, repo_path: str, output_path: str):
        self.repo_path = Path(repo_path)
        self.output_path = Path(output_path)
        self.classes_file = self.repo_path / "src/app/classes.ts"
        self.feats_file = self.repo_path / "src/app/feats.ts"
        self.spells_file = self.repo_path / "src/app/spells.ts"
        
        # Create output directories
        (self.output_path / "classes").mkdir(parents=True, exist_ok=True)
        (self.output_path / "classes/subclasses").mkdir(parents=True, exist_ok=True)
        
    def read_file(self, filepath: Path) -> str:
        """Read TypeScript file content."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return ""
    
    def extract_class_definitions(self) -> Dict[str, Any]:
        """
        Extract all class definitions from the CLASSES export array.
        Uses a more direct approach focusing on the actual data structure.
        """
        content = self.read_file(self.classes_file)
        classes = {}
        
        # Strategy: Extract all _SUBCLASSES arrays first, then parse CLASSES array
        
        # Step 1: Extract all subclass arrays (const XXX_SUBCLASSES = [ ... ])
        print("   → Extracting subclass arrays...")
        subclass_arrays = self._extract_all_subclass_arrays(content)
        print(f"     Found {len(subclass_arrays)} subclass arrays")
        
        # Step 2: Extract CLASSES array  
        print("   → Parsing CLASSES array...")
        classes_match = re.search(r'export\s+const\s+CLASSES\s*=\s*\[', content)
        if not classes_match:
            print("     ⚠️  Could not find CLASSES export")
            return classes
        
        # Find the matching closing bracket for CLASSES array
        start_pos = classes_match.end() - 1  # Position of the opening [
        class_array_content = self._extract_matching_brackets(content, start_pos)
        
        if not class_array_content:
            print("     ⚠️  Could not extract CLASSES array content")
            return classes
        
        # Step 3: Extract individual class objects
        class_objects = self._extract_object_array(class_array_content)
        print(f"     Found {len(class_objects)} class objects")
        
        # Step 4: Parse each class
        for class_obj_str in class_objects:
            try:
                # Extract basic info
                name_match = re.search(r"name:\s*['\"]([^'\"]+)['\"]", class_obj_str)
                if not name_match:
                    continue
                
                class_name_display = name_match.group(1)
                class_name_key = class_name_display.lower()
                
                # Find subclass level and array name
                subclass_level = None
                subclass_array_name = None
                
                subclass_level_match = re.search(r'subclassLevel:\s*(\d+)', class_obj_str)
                if subclass_level_match:
                    subclass_level = int(subclass_level_match.group(1))
                
                subclass_array_match = re.search(r'subclasses:\s*(\w+_SUBCLASSES)', class_obj_str)
                if subclass_array_match:
                    subclass_array_name = subclass_array_match.group(1)
                
                # Extract features
                features_array = self._extract_class_features(class_obj_str, subclass_level, class_name_display)
                
                # Get subclasses
                subclass_list = []
                if subclass_array_name and subclass_array_name in subclass_arrays:
                    for sub_name in subclass_arrays[subclass_array_name].keys():
                        subclass_list.append(sub_name)
                        
                        # Add subclass to classes dict
                        sub_data = subclass_arrays[subclass_array_name][sub_name]
                        classes[f"{class_name_key}_{sub_name}"] = {
                            "type": "subclass",
                            "parentClass": class_name_key,
                            "name": sub_data["name"],
                            "levels": sub_data["levels"]
                        }
                
                # Add class to dict
                classes[class_name_key] = {
                    "name": class_name_display,
                    "subclassLevel": subclass_level,
                    "subclasses": subclass_list,
                    "levels": features_array
                }
                
                print(f"     ✓ {class_name_display} (subclass@lvl {subclass_level}, {len(subclass_list)} subclasses)")
                
            except Exception as e:
                print(f"     ⚠️  Error parsing class: {e}")
                continue
        
        return classes
    
    def _extract_matching_brackets(self, content: str, start_pos: int) -> str:
        """Extract content between matching brackets starting at start_pos."""
        if content[start_pos] != '[':
            return ""
        
        depth = 0
        in_string = False
        string_char = None
        start = start_pos
        
        for i in range(start_pos, len(content)):
            char = content[i]
            
            # Handle strings
            if char in ('"', "'") and (i == 0 or content[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
            
            # Handle brackets
            if not in_string:
                if char == '[':
                    depth += 1
                elif char == ']':
                    depth -= 1
                    if depth == 0:
                        return content[start + 1:i]
        
        return ""
    
    def _extract_object_array(self, array_content: str) -> List[str]:
        """Extract individual objects from an array string."""
        objects = []
        depth = 0
        obj_start = -1
        in_string = False
        string_char = None
        
        for i, char in enumerate(array_content):
            # Handle strings
            if char in ('"', "'") and (i == 0 or array_content[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
            
            # Handle objects
            if not in_string:
                if char == '{':
                    if depth == 0:
                        obj_start = i
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0 and obj_start >= 0:
                        objects.append(array_content[obj_start:i+1])
        
        return objects
    
    def _extract_class_features(self, class_obj_str: str, subclass_level: Optional[int], class_name: str) -> Dict[str, List[Dict]]:
        """Extract features organized by level from a class object."""
        features_by_level = {str(i): [] for i in range(1, 13)}
        
        # Find features: Feature[][]
        features_match = re.search(r'features:\s*\[(.*?)\]\s*as\s+Feature\[\]\[\]', class_obj_str, re.DOTALL)
        if features_match:
            features_content = features_match.group(1)
            
            # Extract level arrays
            level_arrays = self._parse_feature_levels(features_content)
            
            for level_idx, level_features in enumerate(level_arrays):
                level_num = level_idx + 1
                if level_num <= 12:
                    features_by_level[str(level_num)] = level_features
        
        # Add subclass selection marker
        if subclass_level and subclass_level <= 12:
            features_by_level[str(subclass_level)].insert(0, {
                "name": f"Choose {class_name} Subclass",
                "type": "subclassSelection",
                "description": f"Select your {class_name} archetype"
            })
        
        return {level: features for level, features in features_by_level.items() if features}
    
    def _parse_feature_levels(self, features_content: str) -> List[List[Dict]]:
        """Parse feature arrays organized by level."""
        level_arrays = []
        depth = 0
        level_start = -1
        in_string = False
        string_char = None
        
        for i, char in enumerate(features_content):
            # Handle strings
            if char in ('"', "'") and (i == 0 or features_content[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
            
            # Handle arrays
            if not in_string:
                if char == '[':
                    if depth == 0:
                        level_start = i
                    depth += 1
                elif char == ']':
                    depth -= 1
                    if depth == 0 and level_start >= 0:
                        level_content = features_content[level_start + 1:i]
                        features = self._parse_features_in_level(level_content)
                        level_arrays.append(features)
        
        return level_arrays
    
    def _parse_features_in_level(self, level_content: str) -> List[Dict]:
        """Parse individual feature objects from a level."""
        features = []
        objects = self._extract_object_array(level_content)
        
        for obj_str in objects:
            # Extract name
            name_match = re.search(r"name:\s*['\"]([^'\"]*)['\"]", obj_str)
            if name_match:
                features.append({
                    "name": name_match.group(1),
                    "type": "feature"
                })
        
        return features
    
    def _extract_all_subclass_arrays(self, content: str) -> Dict[str, Dict[str, Dict]]:
        """Extract all subclass arrays (e.g., BARD_SUBCLASSES)."""
        subclass_arrays = {}
        
        # Find all const XXX_SUBCLASSES = [ ... ] as Subclass[]
        pattern = r'const\s+(\w+_SUBCLASSES)\s*=\s*\['
        
        for match in re.finditer(pattern, content):
            array_name = match.group(1)
            array_start = match.end() - 1  # Position of opening [
            
            # Extract matching brackets
            array_content = self._extract_matching_brackets(content, array_start)
            if not array_content:
                continue
            
            # Extract individual subclass objects
            subclass_objs = self._extract_object_array(array_content)
            subclasses = {}
            
            for sub_obj_str in subclass_objs:
                try:
                    # Extract name
                    name_match = re.search(r"name:\s*['\"]([^'\"]+)['\"]", sub_obj_str)
                    if not name_match:
                        continue
                    
                    sub_display_name = name_match.group(1)
                    sub_name_key = sub_display_name.lower().replace(' ', '_')
                    
                    # Extract features
                    sub_features = self._extract_subclass_features_from_obj(sub_obj_str)
                    
                    subclasses[sub_name_key] = {
                        "name": sub_display_name,
                        "levels": sub_features
                    }
                except Exception as e:
                    print(f"     ⚠️  Error parsing subclass: {e}")
                    continue
            
            subclass_arrays[array_name] = subclasses
        
        return subclass_arrays
    
    def _extract_subclass_features_from_obj(self, sub_obj_str: str) -> Dict[str, List[Dict]]:
        """Extract features organized by level from a subclass object."""
        features_by_level = {str(i): [] for i in range(1, 13)}
        
        # Find features array
        features_match = re.search(r'features:\s*\[(.*?)\](?=\s*[},])', sub_obj_str, re.DOTALL)
        if features_match:
            features_content = features_match.group(1)
            level_arrays = self._parse_feature_levels(features_content)
            
            for level_idx, level_features in enumerate(level_arrays):
                level_num = level_idx + 1
                if level_num <= 12:
                    features_by_level[str(level_num)] = level_features
        
        return {level: features for level, features in features_by_level.items() if features}
    
    def extract_feats(self) -> List[Dict]:
        """Extract all feats from feats.ts."""
        content = self.read_file(self.feats_file)
        feats = []
        
        # Extract individual feat definitions
        feat_pattern = r'\{\s*name:\s*[\'"]([^\'"]+)[\'"].*?description:\s*[\'"]([^\'"]*)[\'"]'
        
        for match in re.finditer(feat_pattern, content, re.DOTALL):
            name = match.group(1)
            description = match.group(2)
            
            feats.append({
                "name": name,
                "description": description,
                "type": "feat"
            })
        
        return feats
    
    def extract_spells(self) -> List[Dict]:
        """Extract all spells from spells.ts."""
        content = self.read_file(self.spells_file)
        spells = []
        
        # Extract SPELL_XXX definitions
        spell_pattern = r'export\s+const\s+SPELL_(\w+)\s*=\s*\{(.*?)\}\s*as\s+Spell'
        
        for match in re.finditer(spell_pattern, content, re.DOTALL):
            spell_id = match.group(1)
            spell_content = match.group(2)
            
            # Extract name
            name_match = re.search(r'name:\s*[\'"]([^\'"]+)[\'"]', spell_content)
            name = name_match.group(1) if name_match else spell_id.replace('_', ' ').title()
            
            # Extract description
            desc_match = re.search(r'description:\s*[\'"]([^\'"]*)[\'"]', spell_content)
            description = desc_match.group(1) if desc_match else ""
            
            # Extract school
            school_match = re.search(r'school:\s*SpellSchool\.(\w+)', spell_content)
            school = school_match.group(1) if school_match else "Unknown"
            
            spells.append({
                "name": name,
                "description": description,
                "school": school,
                "type": "spell"
            })
        
        return spells
    
    def save_class_json(self, class_name: str, class_data: Dict):
        """Save a class definition to JSON file."""
        if class_data.get("type") == "subclass":
            # Save subclasses to subclasses folder
            parent_class = class_data["parentClass"]
            subclass_name = class_name.replace(f"{parent_class}_", "")
            
            output_file = self.output_path / f"classes/subclasses/{parent_class}_{subclass_name}.json"
            
            # Prepare data
            output_data = {
                "name": class_data["name"],
                "parentClass": parent_class,
                "levels": class_data["levels"]
            }
        else:
            # Save regular classes
            output_file = self.output_path / f"classes/{class_name}.json"
            output_data = {
                "name": class_data["name"],
                "subclassLevel": class_data["subclassLevel"],
                "subclasses": class_data["subclasses"],
                "levels": class_data["levels"]
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {output_file}")
    
    def run(self):
        """Execute the full extraction process."""
        print("🔍 Starting BG3 Data Extraction...")
        print(f"📂 Input: {self.repo_path}")
        print(f"📤 Output: {self.output_path}\n")
        
        # Extract classes
        print("📚 Extracting classes...")
        classes = self.extract_class_definitions()
        
        class_count = 0
        subclass_count = 0
        
        for class_name, class_data in classes.items():
            if "_" in class_name and class_data.get("type") == "subclass":
                subclass_count += 1
            else:
                class_count += 1
            
            self.save_class_json(class_name, class_data)
        
        print(f"✓ Extracted {class_count} classes and {subclass_count} subclasses\n")
        
        # Extract feats
        print("⚔️  Extracting feats...")
        feats = self.extract_feats()
        feats_file = self.output_path / "feats.json"
        
        with open(feats_file, 'w', encoding='utf-8') as f:
            json.dump(feats, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Extracted {len(feats)} feats")
        print(f"✓ Saved {feats_file}\n")
        
        # Extract spells
        print("🔮 Extracting spells...")
        spells = self.extract_spells()
        spells_file = self.output_path / "spells.json"
        
        with open(spells_file, 'w', encoding='utf-8') as f:
            json.dump(spells, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Extracted {len(spells)} spells")
        print(f"✓ Saved {spells_file}\n")
        
        # Generate summary
        print("=" * 60)
        print("✨ EXTRACTION COMPLETE!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   Classes:    {class_count}")
        print(f"   Subclasses: {subclass_count}")
        print(f"   Feats:      {len(feats)}")
        print(f"   Spells:     {len(spells)}")
        print(f"\n📂 Files generated in: {self.output_path}")


if __name__ == "__main__":
    # Paths
    repo_path = r"c:\Users\gabrielgv\Documents\Code\BG3-Damage-Analyser\bg3planner_repo"
    output_path = r"c:\Users\gabrielgv\Documents\Code\BG3-Damage-Analyser\data"
    
    extractor = BG3DataExtractor(repo_path, output_path)
    extractor.run()
