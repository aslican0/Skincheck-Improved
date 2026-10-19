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

new_routine_render = r'''
    let routineHTML = '';
    const trDays = { 'Monday': 'Pazartesi', 'Tuesday': 'Salı', 'Wednesday': 'Çarşamba', 'Thursday': 'Perşembe', 'Friday': 'Cuma', 'Saturday': 'Cumartesi', 'Sunday': 'Pazar' };
    const engDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const currentDayName = engDays[new Date().getDay()];

    if (routine.isCustomWeekly) {
       routineHTML = `
         <div class="weekly-calendar" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-top: 1rem;">
           ${routine.schedule.map(day => `
             <div class="calendar-day" style="background: var(--bg-card); border-radius: 12px; padding: 1.5rem; border: 1px solid var(--border-color); ${day.dayName === currentDayName ? 'border-color: var(--accent-primary); box-shadow: 0 0 15px rgba(217,70,168,0.25);' : ''}">
                <h3 style="text-align: center; color: var(--accent-primary); margin-bottom: 1rem; border-bottom: 2px solid var(--bg-secondary); padding-bottom: 0.5rem; font-size: 1.2rem;">${I18N.currentLang === 'tr' ? trDays[day.dayName] : day.dayName} ${day.dayName === currentDayName ? '✨' : ''}</h3>
                
                <div class="am-block" style="margin-bottom: 1.5rem;">
                   <h4 style="font-size: 0.95rem; color: var(--text-secondary); margin-bottom: 0.75rem; border-left: 3px solid #fbc531; padding-left: 0.5rem;">☀️ ${I18N.currentLang === 'tr' ? 'Sabah' : 'Morning'}</h4>
                   ${day.am.length > 0 ? day.am.map(step => `
                      <div style="display:flex; align-items:flex-start; gap:0.5rem; margin-bottom:0.75rem; font-size:0.9rem;">
                         <span style="font-size: 1.2rem;">${step.icon}</span>
                         <div>
                            <strong style="display:block; color: var(--text-primary);">${step.title}</strong>
                            <span style="color:var(--text-muted); font-size:0.8rem; line-height:1.2; display:block; margin-top:0.2rem;">${step.products.join('<br>')}</span>
                         </div>
                      </div>
                   `).join('') : `<span style="font-size:0.85rem; color:var(--text-muted); font-style:italic;">${I18N.currentLang === 'tr' ? 'Ürün yok' : 'No products'}</span>`}
                </div>

                <div class="pm-block">
                   <h4 style="font-size: 0.95rem; color: var(--text-secondary); margin-bottom: 0.75rem; border-left: 3px solid #273c75; padding-left: 0.5rem;">🌙 ${I18N.currentLang === 'tr' ? 'Akşam' : 'Evening'}</h4>
                   ${day.pm.length > 0 ? day.pm.map(step => `
                      <div style="display:flex; align-items:flex-start; gap:0.5rem; margin-bottom:0.75rem; font-size:0.9rem;">
                         <span style="font-size: 1.2rem;">${step.icon}</span>
                         <div>
                            <strong style="display:block; color: var(--text-primary);">${step.title}</strong>
                            <span style="color:var(--text-muted); font-size:0.8rem; line-height:1.2; display:block; margin-top:0.2rem;">${step.products.join('<br>')}</span>
                         </div>
                      </div>
                   `).join('') : `<span style="font-size:0.85rem; color:var(--text-muted); font-style:italic;">${I18N.currentLang === 'tr' ? 'Ürün yok' : 'No products'}</span>`}
                </div>
             </div>
           `).join('')}
         </div>
       `;
    } else {
       routineHTML = `
        <div class="routine-grid">
          <div class="routine-column routine-am">
            <h3>☀️ ${I18N.t('morningRoutine')}</h3>
            <div class="routine-timeline">${routine.morning.map(step => renderStep(step, 'am')).join('')}</div>
          </div>
          <div class="routine-column routine-pm">
            <h3>🌙 ${I18N.t('eveningRoutine')}</h3>
            <div class="routine-timeline">${routine.evening.map(step => renderStep(step, 'pm')).join('')}</div>
          </div>
        </div>
        <div class="routine-weekly">
          <h3>📅 ${I18N.t('weeklyTreatments')}</h3>
          <div class="weekly-grid">${routine.weekly.map(step => renderStep(step, 'wk')).join('')}</div>
        </div>
       `;
    }

    section.innerHTML = `
      <div class="routine-container">
        <button class="btn btn-secondary back-to-home" id="routineBackToHome" onclick="goHome()" style="margin-bottom: 1.5rem;">← ${I18N.t('backToHome')}</button>
        ${retestHTML}
        <div class="routine-header">
          <h2>${emoji} ${I18N.t('personalizedRoutine')}</h2>
          <div style="display:flex;gap:0.5rem;align-items:center;">
            <p class="routine-skin-badge">${label}</p>
          </div>
        </div>
        ${alertsHTML}
        ${routineHTML}
        <div class="routine-tips">
          <h3>💡 ${I18N.t('skinTips')}</h3>
          <ul>${routine.tips.map(t => `<li>${t.text || t.tr || t.en}</li>`).join('')}</ul>
        </div>
        <div id="routineExclusionsArea"></div>
      </div>`;
'''

new_listeners_and_notifs = r'''
    // Add Listeners
    $$('.routine-step').forEach(stepEl => {
      stepEl.querySelector('.step-header').addEventListener('click', () => {
        stepEl.classList.toggle('open');
      });

      stepEl.querySelectorAll('.mini-product-card').forEach(card => {
        card.addEventListener('click', async (e) => {
          e.stopPropagation();
          const prefix = card.dataset.prefix;
          const stepIdx = parseInt(card.dataset.step);
          const optIdx = parseInt(card.dataset.idx);
          
          const targetRoutine = prefix === 'am' ? routine.morning : prefix === 'pm' ? routine.evening : routine.weekly;
          const stepData = targetRoutine.find(s => s.order === stepIdx);
          const opt = stepData.options[optIdx];

          // Update Selection UI
          stepEl.querySelectorAll('.mini-product-card').forEach(c => c.classList.remove('selected'));
          card.classList.add('selected');
          $(`#${prefix}-name-${stepIdx}`).textContent = opt.name;
          if (opt.price) {
             const pb = $(`#${prefix}-price-${stepIdx}`);
             if(pb) {
               pb.textContent = opt.price === 'low' ? '$' : opt.price === 'mid' ? '$$' : '$$$';
               pb.className = `price-badge ${opt.price}`;
             }
          }
        });
      });
    });

    if (routine.isCustomWeekly && typeof window !== 'undefined' && 'Notification' in window) {
      const currentDayIndex = (new Date().getDay() + 6) % 7; // Mon=0
      const todaysSchedule = routine.schedule[currentDayIndex];
      if (todaysSchedule && todaysSchedule.notifications && todaysSchedule.notifications.length > 0) {
          const sendDailyNotification = () => {
              let msgs = [];
              if (todaysSchedule.notifications.includes('mask')) msgs.push(I18N.currentLang === 'tr' ? 'Maske Günü 🧖‍♀️' : 'Mask Day 🧖‍♀️');
              if (todaysSchedule.notifications.includes('retinol')) msgs.push(I18N.currentLang === 'tr' ? 'Retinol Günü 🔬' : 'Retinol Day 🔬');
              if (todaysSchedule.notifications.includes('exfoliant')) msgs.push(I18N.currentLang === 'tr' ? 'Peeling/Asit Günü 🧪' : 'Exfoliant Day 🧪');
              
              const body = msgs.join(' & ');
              const lastNotifDate = localStorage.getItem('SKINCHECK_LastNotif');
              const todayDate = new Date().toDateString();
              
              if (lastNotifDate !== todayDate && msgs.length > 0) {
                 try {
                     new Notification(I18N.currentLang === 'tr' ? "Günün Rutin Hatırlatıcısı" : "Daily Routine Reminder", {
                         body: (I18N.currentLang === 'tr' ? 'Bugün ' : 'Today is ') + body + '!',
                         icon: 'assets/icon/icon.png'
                     });
                     localStorage.setItem('SKINCHECK_LastNotif', todayDate);
                 } catch(e) { console.warn("Notifications not supported in this context.", e); }
              }
          };

          if (Notification.permission === 'granted') {
             sendDailyNotification();
          } else if (Notification.permission !== 'denied') {
             Notification.requestPermission().then(permission => {
                 if (permission === 'granted') sendDailyNotification();
             });
          }
      }
    }
'''

for f in files_to_edit:
    if not os.path.exists(f):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Replace section.innerHTML block
    pattern_html = r'    section\.innerHTML = `\s*<div class="routine-container">[\s\S]*?</div>`;'
    content = re.sub(pattern_html, new_routine_render.strip(), content)

    # 2. Replace add Listeners block
    pattern_listeners = r'    // Add Listeners\s*\$\$\(\'\.routine-step\'\)[\s\S]*?(?=    if \(profile\.products\))'
    content = re.sub(pattern_listeners, new_listeners_and_notifs.strip() + '\n\n', content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print('Updated app.js for Routine Rendering and Notifications')
