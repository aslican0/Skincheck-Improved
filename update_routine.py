import os
import re

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

new_generate_code = r'''
  // Generate routine based on skin type or existing products
  generate(skinProfile) {
    const frequency = skinProfile.frequency || 'regularly';
    const products = skinProfile.products || [];
    
    // If user has products AND doesn't want a from-scratch basic routine
    if (products.length > 0 && frequency !== 'never') {
      return this._generateFromProducts(skinProfile);
    } else {
      return this._generateFromScratch(skinProfile);
    }
  },

  _generateFromScratch(skinProfile) {
    const type = skinProfile.primaryType || 'normal';
    const concerns = skinProfile.concerns || [];
    const frequency = skinProfile.frequency || 'regularly';

    const routine = {
      isCustomWeekly: false,
      skinType: type,
      budgetPreference: skinProfile.budgetPreference || 'both',
      isBasic: frequency === 'never' || frequency === 'rarely',
      morning: this._getMorningSteps(type, concerns, frequency),
      evening: this._getEveningSteps(type, concerns, frequency),
      weekly: this._getWeeklySteps(type, concerns, frequency),
      tips: this._getTips(type, concerns),
      suggestions: this._getSuggestions(type, concerns),
      timelineAlerts: [],
      routineConflicts: []
    };

    if (skinProfile.productStartDates) {
      this._analyzeTimeline(routine, skinProfile.productStartDates);
    }
    if (skinProfile.products) {
      this._analyzeConflicts(routine, skinProfile.products);
    }
    return routine;
  },

  _categorizeProduct(name) {
    const lowerName = name.toLowerCase();
    // Actives
    if (lowerName.includes('retinol') || lowerName.includes('retinal') || lowerName.includes('ретенол')) return 'retinol';
    if (lowerName.includes('aha') || lowerName.includes('bha') || lowerName.includes('glycolic') || lowerName.includes('salicylic') || lowerName.includes('lactic') || lowerName.includes('peeling')) return 'exfoliant';
    if (lowerName.includes('vitamin c') || lowerName.includes('ascorbic') || lowerName.includes('витамин с')) return 'vitc';
    if (lowerName.includes('niacinamide')) return 'niacinamide';
    // Masks
    if (lowerName.includes('mask') || lowerName.includes('clay') || lowerName.includes('kil') || lowerName.includes('маск')) return 'mask';
    // Basics
    if (lowerName.includes('cleanse') || lowerName.includes('wash') || lowerName.includes('temizle') || lowerName.includes('yıkama') || lowerName.includes('gel moussant') || lowerName.includes('пенка')) return 'cleanser';
    if (lowerName.includes('spf') || lowerName.includes('sun') || lowerName.includes('güneş') || lowerName.includes('солнц')) return 'spf';
    if (lowerName.includes('toner') || lowerName.includes('tonik')) return 'toner';
    if (lowerName.includes('cream') || lowerName.includes('moisturiz') || lowerName.includes('nemlendirici') || lowerName.includes('lotion') || lowerName.includes('krem')) return 'moisturizer';
    
    return 'serum_other'; // fallback
  },

  _generateFromProducts(skinProfile) {
    const products = skinProfile.products || [];
    const type = skinProfile.primaryType || 'normal';
    const concerns = skinProfile.concerns || [];
    
    const categorized = {
      cleanser: [], toner: [], vitc: [], niacinamide: [], retinol: [], exfoliant: [], serum_other: [], moisturizer: [], spf: [], mask: []
    };
    
    products.forEach(p => {
      categorized[this._categorizeProduct(p)].push(p);
    });

    // Create a 7-day schedule
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const schedule = [];
    
    // Logic for weekly distribution
    // Retinol: 2-3x a week (e.g. Tue, Thu, Sat PM)
    // Exfoliant: 1-2x a week (e.g. Wed, Sun PM) - avoid same day as retinol if possible
    // Mask: 1x a week (e.g. Sunday)
    // Vit C: Daily AM
    
    days.forEach((day, index) => {
      let isRetinolDay = index === 1 || index === 3 || index === 5; // Tue, Thu, Sat
      let isExfoliantDay = index === 2 || index === 6; // Wed, Sun
      let isMaskDay = index === 6; // Sunday
      
      let amSteps = [];
      let pmSteps = [];
      let notifications = [];

      // AM ROUTINE
      if (categorized.cleanser.length > 0) amSteps.push({ title: I18N.t('stepCleanser') || 'Temizleyici', icon: '🧴', products: [categorized.cleanser[0]] });
      if (categorized.toner.length > 0) amSteps.push({ title: I18N.t('stepToner') || 'Tonik', icon: '💧', products: [categorized.toner[0]] });
      if (categorized.vitc.length > 0) amSteps.push({ title: 'C Vitamini', icon: '🍊', products: categorized.vitc });
      if (categorized.niacinamide.length > 0) amSteps.push({ title: 'Niacinamide', icon: '✨', products: categorized.niacinamide });
      if (categorized.serum_other.length > 0) amSteps.push({ title: 'Serum', icon: '💧', products: categorized.serum_other });
      if (categorized.moisturizer.length > 0) amSteps.push({ title: I18N.t('stepMoisturizer') || 'Nemlendirici', icon: '🧊', products: [categorized.moisturizer[0]] });
      if (categorized.spf.length > 0) amSteps.push({ title: I18N.t('stepSPF') || 'Güneş Kremi', icon: '☀️', products: categorized.spf });

      // PM ROUTINE
      if (categorized.cleanser.length > 0) pmSteps.push({ title: I18N.t('stepCleanser') || 'Temizleyici', icon: '🧴', products: categorized.cleanser });
      if (categorized.toner.length > 0) pmSteps.push({ title: I18N.t('stepToner') || 'Tonik', icon: '💧', products: [categorized.toner[0]] });
      
      if (isMaskDay && categorized.mask.length > 0) {
          pmSteps.push({ title: 'Maske', icon: '🧖‍♀️', products: categorized.mask });
          notifications.push('mask');
      }

      if (isRetinolDay && categorized.retinol.length > 0) {
          pmSteps.push({ title: 'Retinol', icon: '🔬', products: categorized.retinol });
          notifications.push('retinol');
      } else if (isExfoliantDay && categorized.exfoliant.length > 0) {
          pmSteps.push({ title: 'Peeling / Asit', icon: '🧪', products: categorized.exfoliant });
          notifications.push('exfoliant');
      } else {
          // Normal serums on off-days
          if (categorized.serum_other.length > 0) pmSteps.push({ title: 'Serum', icon: '💧', products: categorized.serum_other });
      }

      if (categorized.moisturizer.length > 0) pmSteps.push({ title: I18N.t('stepMoisturizer') || 'Nemlendirici', icon: '🌙', products: categorized.moisturizer });

      schedule.push({
        dayName: day,
        am: amSteps,
        pm: pmSteps,
        notifications: notifications
      });
    });

    const routine = {
      isCustomWeekly: true,
      skinType: type,
      schedule: schedule,
      tips: this._getTips(type, concerns),
      timelineAlerts: [],
      routineConflicts: []
    };

    if (skinProfile.productStartDates) {
      this._analyzeTimeline(routine, skinProfile.productStartDates);
    }
    if (skinProfile.products) {
      this._analyzeConflicts(routine, skinProfile.products);
    }

    return routine;
  }
'''

for f in files_to_edit:
    if not os.path.exists(f):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace the existing generate method
    # It starts with "  generate(skinProfile) {" and goes until the start of "_analyzeTimeline"
    pattern = r'  generate\(skinProfile\) \{[\s\S]*?(?=  _analyzeTimeline)'
    content = re.sub(pattern, new_generate_code.strip() + '\n\n', content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print('Updated routine.js')
