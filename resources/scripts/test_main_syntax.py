#!/usr/bin/env python3
"""Test that main.py syntax is valid without launching GUI"""

import sys
import py_compile

try:
    print("[*] Checking main.py syntax...")
    py_compile.compile('main.py', doraise=True)
    print("[OK] main.py syntax is valid!")
    
    print("\n[*] Testing imports...")
    from class_features_loader import ClassFeaturesLoader
    print("[OK] ClassFeaturesLoader imported")
    
    print("\n[*] All checks passed!")
except py_compile.PyCompileError as e:
    print(f"[ERROR] Syntax error in main.py:")
    print(e)
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
