
import pandas as pd
import os
import sys
import io

# Force stdout to handle utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r"c:\Users\gabrielgv\Documents\Code\BG3-Damage-Analyser\resources\BG3 Item Index Cheat Sheet.ods"

try:
    # Try reading the excel file (pandas read_excel supports ods with odfpy installed)
    xl = pd.ExcelFile(file_path, engine="odf")
    print("Sheet names:", xl.sheet_names)
    
    for sheet in xl.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        df = xl.parse(sheet)
        print("Columns:", df.columns.tolist())
        print("First 2 rows:")
        print(df.head(2).to_string())
        
except Exception as e:
    print(f"Error reading file: {e}")
