#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Targeted fix: Find all lines with '' inside string values and fix them.
"""
import subprocess
import re

filepath = r"c:\Users\hasli\OneDrive\Masaüstü\FinalProject\js\products.js"

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
fixes = 0

for lineno, line in enumerate(lines, 1):
    # Check for patterns like: name: 'text''more text' or brand: 'D''ALBA'
    # These are the '' (two single quotes) inside what should be a single-quoted string
    
    # Pattern: field_name: 'text with '' in it'
    # The fix: convert the whole value to double-quoted and replace '' with '
    
    # Use regex to find JS object property assignments with broken string values
    # Look for: 'some text' ''another text' or similar
    
    # Simple approach: for lines with name:, brand:, imageUrl: etc.
    # If the line has '' (two consecutive single quotes) in the value part, fix it
    
    if "''" in line:
        # This line has '' which causes syntax issues
        # Extract the property name and fix the value
        
        # Strategy: find everything after the colon on this line
        # and if it's a string value with '', fix it
        
        # Pattern to match: key: 'value with '' issues',
        def fix_value_with_double_apostrophe(m):
            full = m.group(0)
            key = m.group(1)
            val_with_quotes = m.group(2)
            
            # The value has '' in it - these are escaped apostrophes in SQL style
            # Convert to a clean string: remove the extra quote
            # 'text''more' -> "text'more"
            
            # Strip the outer quotes
            inner = val_with_quotes[1:-1]  # remove first and last '
            
            # Replace all '' with ' (SQL-style escape -> regular apostrophe)
            inner = inner.replace("''", "'")
            
            # Now wrap in double quotes (in case there are still apostrophes)
            # Escape any double quotes in inner
            inner = inner.replace('"', '\\"')
            
            return key + ': "' + inner + '"'
        
        # Match: (key): ('value') where value may contain ''
        # Be careful: the value ends at the last ' before , or \n
        
        # Simple regex: find 'text' patterns that have '' inside
        # Pattern: starts with ' ends with ', and contains ''
        
        # Let's do it more carefully
        new_line = re.sub(
            r"((?:name|brand|category|quantity|barcode|id|imageUrl|url|veganStatus|vegetarianStatus|source|barcode)):\s*'((?:[^']*(?:''[^']*)*)?)'",
            fix_value_with_double_apostrophe,
            line
        )
        
        if new_line != line:
            fixes += 1
        fixed_lines.append(new_line)
    else:
        fixed_lines.append(line)

print(f"Fixed {fixes} lines with '' patterns")

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

# Check syntax
result = subprocess.run(
    ['node', '--check', filepath],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
if result.returncode == 0:
    print("SYNTAX OK!")
else:
    err_lines = result.stderr.split('\n')
    # Find the line number
    for l in err_lines[:3]:
        print(l)
