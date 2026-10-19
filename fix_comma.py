import os

files_to_edit = [
    'js/routine.js',
    'mobile_app/js/routine.js',
    'ios/App/App/public/js/routine.js',
    'android/app/src/main/assets/public/js/routine.js',
    'FinalProject/js/routine.js',
    'FinalProject/mobile_app/js/routine.js',
    'FinalProject/ios/App/App/public/js/routine.js',
    'FinalProject/android/app/src/main/assets/public/js/routine.js',
]

for f in files_to_edit:
    if not os.path.exists(f):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace the missing comma
    content = content.replace("    return routine;\n  }\n\n  _analyzeTimeline(routine, startDates) {", "    return routine;\n  },\n\n  _analyzeTimeline(routine, startDates) {")
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print('Fixed syntax error in routine.js')
