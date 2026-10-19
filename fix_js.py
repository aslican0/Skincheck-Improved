import os

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
    
    # Replace the extra });
    content = content.replace("    if (firstVisible) firstVisible.click();\n    }\n    });", "    if (firstVisible) firstVisible.click();\n    }")
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print('Fixed syntax error.')
