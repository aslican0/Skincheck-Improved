const fs = require('fs');

global.window = {};
global.document = {
    querySelector: () => ({ style: {}, classList: { remove: ()=>{}, add: ()=>{} }, addEventListener: ()=>{}, innerHTML: '' }),
    querySelectorAll: () => []
};
global['$'] = global.document.querySelector;
global['$$'] = global.document.querySelectorAll;
global.I18N = { currentLang: 'tr', t: (k) => k };
global.SKINQUIZ = { getTypeEmoji: () => 'e', getTypeLabel: () => 'l' };
global.AUTH = {
    getRoutineSettings: () => ({ frequency: 'regularly', products: ['The Ordinary Retinol', 'Simple Face Wash'] }),
    saveRoutine: () => {},
    getSkinProfile: () => ({ primaryType: 'normal' })
};
global.pushToHistory = () => {};
global.currentView = { type: 'home' };

const routineCode = fs.readFileSync('js/routine.js', 'utf8');
const modifiedCode = routineCode.replace('const ROUTINE =', 'global.ROUTINE =');
eval(modifiedCode);

console.log('Testing Basic Routine:');
const basicRes = ROUTINE.generate({ primaryType: 'dry', frequency: 'never' });
console.log('Basic isCustomWeekly:', basicRes.isCustomWeekly);
console.log('Basic schedule days count:', basicRes.schedule ? basicRes.schedule.length : 0);
console.log('Basic Wednesday notifications:', basicRes.schedule[2].notifications);
console.log('Basic Sunday notifications:', basicRes.schedule[6].notifications);

console.log('\nChecking Dry Skin Basic Routine Details:');
console.log('- AM Step 1 (Cleanser):', {
  purpose: basicRes.morning[0].purpose ? 'OK' : 'MISSING',
  skinReason: basicRes.morning[0].skinTypeReason ? 'OK' : 'MISSING',
  containsDryWaterAdvice: basicRes.morning[0].skinTypeReason.includes('ılık su')
});
console.log('- AM Step 2 (Moisturizer):', {
  purpose: basicRes.morning[1].purpose ? 'OK' : 'MISSING',
  skinReason: basicRes.morning[1].skinTypeReason ? 'OK' : 'MISSING',
  containsLipidCeramide: basicRes.morning[1].skinTypeReason.includes('lipid') || basicRes.morning[1].skinTypeReason.includes('Seramid')
});

console.log('\nChecking Oily Skin Basic Routine Details:');
const oilyRes = ROUTINE.generate({ primaryType: 'oily', frequency: 'never' });
console.log('- AM Step 1 (Cleanser for Oily):', {
  purpose: oilyRes.morning[0].purpose ? 'OK' : 'MISSING',
  skinReason: oilyRes.morning[0].skinTypeReason ? 'OK' : 'MISSING',
  containsSebumGel: oilyRes.morning[0].skinTypeReason.includes('sebum') && oilyRes.morning[0].skinTypeReason.includes('jel')
});
console.log('- AM Step 2 (Moisturizer for Oily):', {
  purpose: oilyRes.morning[1].purpose ? 'OK' : 'MISSING',
  skinReason: oilyRes.morning[1].skinTypeReason ? 'OK' : 'MISSING',
  containsOilFreeMyth: oilyRes.morning[1].skinTypeReason.includes('neme ihtiyacı yoktur') || oilyRes.morning[1].skinTypeReason.includes('sebum')
});

console.log('\nTesting Custom Placed Routine:');
const customRes = ROUTINE.generate({
    primaryType: 'combination',
    frequency: 'regularly',
    customRoutine: {
        morning: [{ name: 'CeraVe Foaming Cleanser', category: 'cleanser' }, { name: 'Sunscreen SPF50', category: 'spf' }],
        evening: [{ name: 'CeraVe Foaming Cleanser', category: 'cleanser' }, { name: 'Hydro Boost Gel', category: 'moisturizer' }],
        weekly: [{ name: 'AHA Peeling Solution', category: 'exfoliant' }, { name: 'Clay Mask', category: 'mask' }]
    }
});
console.log('Custom isCustomWeekly:', customRes.isCustomWeekly);
console.log('Custom schedule days count:', customRes.schedule ? customRes.schedule.length : 0);
console.log('Custom Wednesday notifications:', customRes.schedule[2].notifications);
console.log('Custom Sunday notifications:', customRes.schedule[6].notifications);
console.log('Custom Monday AM products:', customRes.schedule[0].am.map(s => s.title));
console.log('Custom Wednesday PM products:', customRes.schedule[2].pm.map(s => s.title));

console.log('\nCustom Step-by-Step Summary Check:');
console.log('Morning steps count:', customRes.morning.length);
customRes.morning.forEach((s, idx) => {
  console.log(`  Step ${idx + 1}: ${s.title}`);
  console.log(`    Purpose: ${s.purpose ? s.purpose.substring(0, 50) + '...' : 'MISSING'}`);
  console.log(`    Skin Reason: ${s.skinTypeReason ? s.skinTypeReason.substring(0, 50) + '...' : 'MISSING'}`);
  console.log(`    WarningOrTip: ${s.warningOrTip ? s.warningOrTip.substring(0, 50) + '...' : 'MISSING'}`);
});

console.log('\nEvening steps count:', customRes.evening.length);
customRes.evening.forEach((s, idx) => {
  console.log(`  Step ${idx + 1}: ${s.title}`);
  console.log(`    Purpose: ${s.purpose ? s.purpose.substring(0, 50) + '...' : 'MISSING'}`);
  console.log(`    Skin Reason: ${s.skinTypeReason ? s.skinTypeReason.substring(0, 50) + '...' : 'MISSING'}`);
  console.log(`    WarningOrTip: ${s.warningOrTip ? s.warningOrTip.substring(0, 50) + '...' : 'MISSING'}`);
});

console.log('\nWeekly steps count:', customRes.weekly.length);
customRes.weekly.forEach((s, idx) => {
  console.log(`  Step ${idx + 1}: ${s.title}`);
  console.log(`    Purpose: ${s.purpose ? s.purpose.substring(0, 50) + '...' : 'MISSING'}`);
  console.log(`    Skin Reason: ${s.skinTypeReason ? s.skinTypeReason.substring(0, 50) + '...' : 'MISSING'}`);
  console.log(`    WarningOrTip: ${s.warningOrTip ? s.warningOrTip.substring(0, 50) + '...' : 'MISSING'}`);
});
