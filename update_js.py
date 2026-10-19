import os
import re

files_to_edit = [
    'js/app.js',
    'mobile_app/js/app.js',
    'ios/App/App/public/js/app.js',
    'android/app/src/main/assets/public/js/app.js',
    'FinalProject/js/app.js',
    'FinalProject/mobile_app/js/app.js',
    'FinalProject/ios/App/App/public/js/app.js',
    'FinalProject/android/app/src/main/assets/public/js/app.js',
]

for f in files_to_edit:
    if not os.path.exists(f):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove the comparison block using regex
    # The block starts with "// Comparison Panel" and ends right before "// Initialize tabs if needed"
    new_content = re.sub(r'^\s*// Comparison Panel[\s\S]*?(?=\s*// Initialize tabs if needed)', '', content, flags=re.MULTILINE)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(new_content)

print('Updated JS files.')
