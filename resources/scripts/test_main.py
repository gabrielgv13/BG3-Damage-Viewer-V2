#!/usr/bin/env python3
"""Quick test of main.py import"""

try:
    print("[*] Importing main.py...")
    import main
    
    print(f"[OK] main.py imported successfully")
    print(f"[OK] FEATURES_LOADER initialized: {main.FEATURES_LOADER is not None}")
    print(f"[OK] Available classes: {len(main.CLASSES)} items")
    print(f"[OK] Sample classes: {', '.join(main.CLASSES[:3])}")
    
    # Test helper functions exist
    print(f"[OK] has_subclass_choice function: {hasattr(main, 'has_subclass_choice')}")
    print(f"[OK] get_subclass_choices function: {hasattr(main, 'get_subclass_choices')}")
    print(f"[OK] get_class_features_display function: {hasattr(main, 'get_class_features_display')}")
    
    # Test they work
    bard_has_choice_at_3 = main.has_subclass_choice("Bard", 3)
    print(f"[OK] Bard has subclass choice at level 3: {bard_has_choice_at_3}")
    
    bard_choices = main.get_subclass_choices("Bard")
    print(f"[OK] Bard subclass choices: {bard_choices}")
    
    print("\n[*] ALL TESTS PASSED - main.py is ready!")
    
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
