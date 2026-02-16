#!/usr/bin/env python3
"""Quick test of ClassFeaturesLoader"""

import sys
print(f"[*] Python: {sys.version}")

try:
    from class_features_loader import ClassFeaturesLoader
    print("[OK] Loader imported")
    
    loader = ClassFeaturesLoader()
    print("[OK] Loader instantiated")
    
    classes = loader.get_available_classes()
    print(f"[OK] Classes loaded: {len(classes)}")
    print(f"    {', '.join(classes)}")
    
    bard_level = loader.get_subclass_level("bard")
    print(f"[OK] Bard subclass level: {bard_level}")
    
    bard_opts = loader.get_subclass_options("bard")
    print(f"[OK] Bard subclass options: {bard_opts}")
    
    paladin_features = loader.get_features_at_level("paladin", 1)
    print(f"[OK] Paladin level 1 features: {len(paladin_features)} items")
    
    print("\n[*] ALL TESTS PASSED!")
    
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
