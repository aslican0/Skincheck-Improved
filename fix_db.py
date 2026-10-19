import re
import sys

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    fixed_lines = []
    
    buffer = ""
    for line in lines:
        if not buffer:
            buffer = line
        else:
            buffer += " " + line.strip()
            
        stripped = buffer.strip()
        if not stripped or stripped.endswith(',') or stripped.endswith('{') or stripped.endswith('}') or stripped.endswith('[') or stripped.endswith(']') or stripped.endswith(';') or stripped.endswith('(') or stripped.endswith(')') or stripped.startswith('//'):
            fixed_lines.append(buffer)
            buffer = ""
        else:
            pass

    if buffer:
        fixed_lines.append(buffer)
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    print(f"Fixed newlines in {path}")

if __name__ == '__main__':
    fix_file(r'c:\Users\hasli\OneDrive\Masaüstü\FinalProject\js\products.js')
