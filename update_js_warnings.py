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
    
    warnings_replacement = r'''
    // Warnings Panel
    const warnList = $('#warningsList');
    const warnTab = document.querySelector('.result-tab[data-result="warningsPanel"]');
    
    let displayWarnings = analysis.warnings || [];
    let showFragranceBadge = false;

    // Check if the only warning is the fragrance warning
    if (displayWarnings.length === 1 && (displayWarnings[0].title === (typeof I18N !== 'undefined' ? I18N.t('containsFragranceTitle') : 'Parfüm İçerir') || displayWarnings[0].title.includes('Parfüm') || displayWarnings[0].title.includes('Fragrance'))) {
        displayWarnings = [];
        showFragranceBadge = true;
    }

    if (warnTab) {
        if (displayWarnings.length === 0) {
            warnTab.style.display = 'none';
        } else {
            warnTab.style.display = '';
        }
    }

    if (warnList) {
        warnList.innerHTML = displayWarnings.length ? displayWarnings.map(w => `
            <div class="warning-item" style="padding: 1rem; border-left: 4px solid var(--accent-red); background: rgba(239, 68, 68, 0.05); margin-bottom: 1rem; border-radius: 4px;">
                <strong style="display: flex; align-items: center; gap: 0.5rem;">${w.icon} ${w.title}</strong>
                <p style="font-size: 0.9rem; margin-top: 0.5rem; color: var(--text-secondary);">${w.desc}</p>
            </div>
        `).join('') : `<p style="padding: 1rem; color: var(--text-secondary);">${I18N.currentLang === 'tr' ? 'Uyarı bulunamadı.' : 'No warnings found.'}</p>`;
    }
'''

    pattern_warnings = r'// Warnings Panel\s*const warnList = \$\(\'#warningsList\'\);\s*if \(warnList\) \{[\s\S]*?\}\s*// Dupes Panel'
    content = re.sub(pattern_warnings, warnings_replacement.strip() + '\n\n    // Dupes Panel', content)
    
    standAlone_replacement = r'''
        let fragranceHtml = '';
        if (showFragranceBadge) {
            fragranceHtml = `
            <div style="display: flex; align-items: center; gap: 0.35rem; padding: 0.35rem 0.75rem; border-radius: 6px; border: 1px solid rgba(239, 68, 68, 0.3); background: rgba(239, 68, 68, 0.05); font-size: 0.85rem;">
               <span style="font-size: 1rem; color: var(--accent-red);">❗️</span>
               <span style="font-weight: 600; color: var(--text-primary);">${I18N.currentLang === 'tr' ? 'Parfüm İçerir' : 'Contains Fragrance'}</span>
            </div>
            `;
        }

        standAlone.innerHTML = `
           <div style="display: flex; flex-direction: column; gap: 0.75rem; margin: 1.5rem 0;">
             <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">${suitHtml}</div>
             <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">${useHtml}${fragranceHtml}</div>
           </div>
        `;
'''

    pattern_standalone = r'standAlone\.innerHTML = `\s*<div style="display: flex; flex-direction: column; gap: 0\.75rem; margin: 1\.5rem 0;">\s*<div style="display: flex; flex-wrap: wrap; gap: 0\.5rem;">\$\{suitHtml\}</div>\s*<div style="display: flex; flex-wrap: wrap; gap: 0\.5rem;">\$\{useHtml\}</div>\s*</div>\s*`;'
    content = re.sub(pattern_standalone, standAlone_replacement.strip(), content)

    tabs_init_replacement = r'''
    // Initialize tabs if needed
    let anyActive = false;
    $$('.result-tab').forEach(tab => {
      if (tab.style.display !== 'none' && tab.classList.contains('active')) {
          anyActive = true;
      }
      const newTab = tab.cloneNode(true);
      tab.parentNode.replaceChild(newTab, tab);
      newTab.addEventListener('click', () => {
        $$('.result-tab').forEach(t => t.classList.remove('active'));
        $$('.result-panel').forEach(p => p.classList.remove('active'));
        newTab.classList.add('active');
        $(`#${newTab.dataset.result}`).classList.add('active');
      });
    });
    
    // If no tab is active (because we hid it), click the first visible one
    if (!anyActive) {
        const firstVisible = Array.from(document.querySelectorAll('.result-tab')).find(t => t.style.display !== 'none');
        if (firstVisible) firstVisible.click();
    }
'''

    pattern_tabs = r'// Initialize tabs if needed\s*\$\$\(\'\.result-tab\'\)\.forEach\(tab => \{[\s\S]*?\}\);'
    content = re.sub(pattern_tabs, tabs_init_replacement.strip(), content)

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print('Updated JS files for Warnings.')
