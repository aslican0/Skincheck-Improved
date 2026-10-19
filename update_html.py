import os
import re

files_to_edit = [
    'index.html',
    'mobile_app/index.html',
    'ios/App/App/public/index.html',
    'android/app/src/main/assets/public/index.html',
    'FinalProject/index.html',
    'FinalProject/mobile_app/index.html',
    'FinalProject/ios/App/App/public/index.html',
    'FinalProject/android/app/src/main/assets/public/index.html',
]

for f in files_to_edit:
    if not os.path.exists(f):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove the comparison tab
    content = re.sub(r'<button class="result-tab"\s+data-result="suitabilityPanel">[\s\S]*?</button>\s*', '', content)
    
    # Remove the suitabilityPanel
    content = re.sub(r'<div class="result-panel"\s+id="suitabilityPanel">\s*<div class="suitability-grid"\s+id="suitabilityGrid"></div>\s*<div class="usage-grid"\s+id="usageGrid"></div>\s*</div>\s*', '', content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print('Updated HTML files.')
